---
name: video-frame-extractor
display_name: 视频截帧图片提取器
display_name_en: Video Frame & Image Extractor
description: 批量把视频截取指定秒画面、复制并统一缩放图片的通用 Skill。当用户说"把视频截第X秒的图 / 视频截帧 / 截取视频画面 / 图片复制并缩放 / 统一图片尺寸 / 把某目录下的视频和图片处理成统一尺寸的图片 / 批量提取视频封面 / 视频转图片"时使用。核心脚本 scripts/extract_frames.py 递归遍历源目录，视频用 OpenCV 截取指定秒（默认第2秒）画面、图片复制，统一 resize 到指定尺寸（默认 297x269），支持保留目录结构 / 平铺（目录名前缀防重名）/ 平铺无前缀三种输出方式。已内置 Windows 中文路径写入兼容（cv2.imwrite 对中文路径静默失败，改用 imencode+tofile 规避）。
description_zh: 批量把视频截取指定秒画面、复制并统一缩放图片的通用 Skill。触发词：视频截帧、截取视频画面、视频转图片、提取视频第X秒、图片复制缩放、统一图片尺寸、批量处理视频图片、视频封面提取。递归遍历源目录，OpenCV 截取视频指定秒（默认第2秒），图片复制，统一 resize（默认297x269），支持保留目录结构/平铺（目录名前缀防重名）三种输出方式，内置 Windows 中文路径兼容。
description_en: Batch-extract a frame at a given second from videos, copy and uniformly resize images. Triggers: extract video frame, video to image, capture video frame at second N, copy & resize images, unify image size, batch process videos/images. Recursively walks the source directory, uses OpenCV to grab a frame at a given second (default 2nd), copies images, resizes everything to a fixed size (default 297x269), supports keep-tree / flatten-with-prefix / flatten-no-prefix output layouts, with built-in Windows non-ASCII path write compatibility.
category: 媒体处理
version: 1.0.0
author: workbuddy
agent_created: true
---

# 视频截帧 + 图片复制 + 统一缩放

一句话：**给定一个源目录，把里面所有视频截第 N 秒画面、所有图片复制，统一缩放到固定尺寸，输出到目标目录。**

核心脚本 `scripts/extract_frames.py`，依赖 `opencv-python-headless` + `numpy`。

## 什么时候用

用户的需求命中以下任意一条时使用本 Skill：

- 「把这个目录下的视频截第 2 秒的图」
- 「视频截帧」「视频转图片」「提取视频画面/封面」
- 「图片复制并统一缩放」「把所有图片尺寸统一成 X×Y」
- 「批量处理视频和图片，输出统一尺寸的图」

## 快速开始（代理直接执行）

1. 确认源目录 `--src` 与目标目录 `--dst`（用户通常只给源目录和输出目录）。
2. 确认参数：截取秒数（默认 2）、输出宽高（默认 297×269）、输出组织方式。
3. 运行：

```bash
python scripts/extract_frames.py \
  --src "源目录" --dst "输出目录" \
  --seconds 2 --width 297 --height 269
```

4. 读脚本 stdout 的 `[完成] 视频截帧 N 图片复制 M 失败 K` 判断结果；有失败时逐条排查。

## 参数说明

| 参数 | 默认 | 说明 |
|---|---|---|
| `--src` | 必填 | 源目录，递归遍历 |
| `--dst` | 必填 | 输出目录，自动创建 |
| `--seconds` | `2.0` | 截取第几秒的画面（视频短于此秒时回退第一帧） |
| `--width` | `297` | 输出图片宽度 |
| `--height` | `269` | 输出图片高度 |
| `--quality` | `95` | jpg 质量 1–100 |
| `--layout` | `keep` | `keep` 保留子目录结构；`flat` 平铺+目录名前缀防重名；`single` 平铺无前缀（同名会被覆盖，慎用） |
| `--flat-prefix-sep` | `_` | flat 模式下目录名与文件名的分隔符 |

## 关键坑（务必遵守）

1. **Windows 中文/非 ASCII 路径写入**：`cv2.imwrite` 对中文路径**静默失败**（返回 False 但不报错），必须用 `cv2.imencode` + `ndarray.tofile` 写入。本脚本已内置，勿改回 `imwrite`。
2. **视频读取中文路径**：`cv2.VideoCapture` 多数版本可用；若个别视频打不开，先 `shutil.copy` 到临时英文路径再读。
3. **平铺同名冲突**：不同子目录常有同名文件（如各孔的 `开孔.jpg`），平铺时务必用 `--layout flat`（加目录名前缀），不要用 `single` 以免覆盖丢失。

## 环境安装（一次性）

```bash
# 国内网络建议加清华镜像
pip install opencv-python-headless numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> 完整流程、环境自检、排错见 `references/workflow.md` 与 `references/environment.md`。

## 目录结构

```
video-frame-extractor/
├── SKILL.md                        # 本文件（元数据 + 使用说明）
├── scripts/
│   └── extract_frames.py           # 核心处理脚本
└── references/
    ├── workflow.md                 # 完整操作流程与真实案例
    └── environment.md              # 环境依赖与排错
```
