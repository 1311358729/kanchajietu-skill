# -*- coding: utf-8 -*-
"""
视频截帧 + 图片复制 + 统一缩放 通用处理脚本

功能：
  1. 递归遍历源目录，找出所有视频文件，截取指定秒数的画面（默认第 2 秒）。
  2. 找出所有图片文件，复制并统一缩放。
  3. 所有输出图片统一 resize 到指定尺寸（默认 297x269）。
  4. 支持三种输出组织方式：
       keep   —— 保留源目录子目录结构（默认）
       flat   —— 全部平铺到输出根目录（子目录名前缀防重名）
       single —— 全部平铺，不加前缀（同名会被后写的覆盖，慎用）

关键坑（Windows 中文路径）：
  cv2.imwrite 对含中文/非 ASCII 的路径会【静默失败】——返回 False 但不报错。
  因此本脚本统一用 cv2.imencode + ndarray.tofile 写入，规避此问题。
  视频读取 cv2.VideoCapture 对中文路径在多数 OpenCV 版本下可用，若失败请
  先用 shutil 复制到临时英文路径再读。

用法示例：
  python extract_frames.py --src "E:\\某目录\\视频" --dst "E:\\某目录\\输出"
  python extract_frames.py --src . --dst out --seconds 2 --width 297 --height 269 --layout flat
  python extract_frames.py --src . --dst out --seconds 1 --quality 90

依赖：
  pip install opencv-python-headless numpy
"""

import os
import re
import sys
import argparse
import numpy as np
import cv2

# 默认支持扩展名（小写）
DEFAULT_VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".m4v", ".ts", ".webm"}
DEFAULT_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def resize_to(img, width, height):
    """统一缩放到固定尺寸（直接拉伸，不保持宽高比）。"""
    return cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)


def imwrite_cn(path, img, quality):
    """写含中文路径的 jpg。cv2.imwrite 对中文路径静默失败，改用 imencode+tofile。"""
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        return False
    buf.tofile(path)
    return True


def read_image_cn(src_path):
    """读含中文路径的图片。cv2.imread 对中文路径可能失败，用 fromfile+imdecode。"""
    img = cv2.imdecode(np.fromfile(src_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        img = cv2.imread(src_path, cv2.IMREAD_COLOR)  # 回退
    return img


def extract_video_frame(src_path, seconds):
    """截取视频第 seconds 秒的画面帧，返回 BGR ndarray，失败返回 None。"""
    cap = cv2.VideoCapture(src_path)
    if not cap.isOpened():
        return None
    # 定位到目标秒
    cap.set(cv2.CAP_PROP_POS_MSEC, int(seconds * 1000))
    ret, frame = cap.read()
    if not ret or frame is None:
        # 视频短于目标秒时回退到第一帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        return None
    return frame


def _sort_key(name):
    """按名称中的数字排序（ZK1, ZK2, ..., ZK10 ...）。"""
    nums = re.sub(r"\D", "", name)
    return int(nums) if nums else 0


def main():
    ap = argparse.ArgumentParser(description="视频截帧 + 图片复制 + 统一缩放")
    ap.add_argument("--src", required=True, help="源目录（递归遍历）")
    ap.add_argument("--dst", required=True, help="输出目录")
    ap.add_argument("--seconds", type=float, default=2.0, help="截取第几秒的画面，默认 2.0")
    ap.add_argument("--width", type=int, default=297, help="输出宽度，默认 297")
    ap.add_argument("--height", type=int, default=269, help="输出高度，默认 269")
    ap.add_argument("--quality", type=int, default=95, help="jpg 质量 1-100，默认 95")
    ap.add_argument("--layout", choices=["keep", "flat", "single"], default="keep",
                    help="输出组织方式：keep=保留子目录结构(默认) flat=平铺+目录名前缀 single=平铺无前缀")
    ap.add_argument("--flat-prefix-sep", default="_", help="flat 模式下目录名与文件名的分隔符，默认 _")
    args = ap.parse_args()

    src = os.path.abspath(args.src)
    dst = os.path.abspath(args.dst)
    os.makedirs(dst, exist_ok=True)

    ok_video = 0
    ok_image = 0
    fail = []

    # 先收集所有文件，再统一决定输出路径
    entries = []
    for root, dirs, files in os.walk(src):
        dirs.sort(key=_sort_key)
        rel = os.path.relpath(root, src)
        for fn in files:
            entries.append((rel, fn))

    for rel, fn in entries:
        ext = os.path.splitext(fn)[1].lower()
        src_path = os.path.join(src, rel, fn) if rel != "." else os.path.join(src, fn)
        out_name = os.path.splitext(fn)[0] + ".jpg"

        # 决定输出目录
        if args.layout == "keep":
            out_dir = dst if rel == "." else os.path.join(dst, rel)
        else:  # flat / single
            out_dir = dst

        os.makedirs(out_dir, exist_ok=True)

        if ext in DEFAULT_VIDEO_EXT:
            frame = extract_video_frame(src_path, args.seconds)
            if frame is None:
                fail.append((src_path, "视频读帧失败"))
                continue
            frame = resize_to(frame, args.width, args.height)
            if args.layout == "flat":
                out_name = rel.replace(os.sep, args.flat_prefix_sep) + args.flat_prefix_sep + out_name if rel != "." else out_name
            out_path = os.path.join(out_dir, out_name)
            if imwrite_cn(out_path, frame, args.quality):
                ok_video += 1
            else:
                fail.append((src_path, "写帧失败"))

        elif ext in DEFAULT_IMAGE_EXT:
            img = read_image_cn(src_path)
            if img is None:
                fail.append((src_path, "图片读取失败"))
                continue
            img = resize_to(img, args.width, args.height)
            if args.layout == "flat":
                out_name = rel.replace(os.sep, args.flat_prefix_sep) + args.flat_prefix_sep + out_name if rel != "." else out_name
            out_path = os.path.join(out_dir, out_name)
            if imwrite_cn(out_path, img, args.quality):
                ok_image += 1
            else:
                fail.append((src_path, "写图失败"))

    print(f"[完成] 视频截帧: {ok_video}  图片复制: {ok_image}  失败: {len(fail)}")
    for p, why in fail:
        print(f"  [FAIL] {p} -> {why}")

    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
