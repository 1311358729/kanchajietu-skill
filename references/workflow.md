# 完整操作流程（Workflow）

## 背景与目标

典型场景：岩土勘察 / 工程验收中，一个项目目录下按钻孔编号（ZK1、ZK2…）分子目录存放视频（.mp4）和照片（.jpg）。需要：

1. 每个视频截取第 2 秒画面；
2. 每张照片复制一份；
3. 所有输出图片统一尺寸（例如 297×269）。

## 步骤

### 第 1 步：摸清源目录结构

```bash
# 列出源目录，看是否有子目录、有哪些文件类型
find "源目录" -type f | head -50
# 统计类型分布
find "源目录" -type f | sed 's/.*\.//' | sort | uniq -c
```

要点：
- 确认视频/图片的扩展名是否在脚本默认支持列表内（视频 `.mp4/.mov/.avi/.mkv/.wmv/.flv/.m4v/.ts/.webm`，图片 `.jpg/.jpeg/.png/.bmp/.webp/.tif/.tiff`）。
- 确认是否有子目录（决定输出用 `keep` 还是 `flat`）。

### 第 2 步：确认环境

```bash
python -c "import cv2, numpy; print('ok', cv2.__version__)"
```

未安装则：

```bash
pip install opencv-python-headless numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> 不需要 ffmpeg，OpenCV 内置视频解码（对常见 H.264 mp4 足够）。

### 第 3 步：运行脚本

保留目录结构：

```bash
python scripts/extract_frames.py --src "源目录" --dst "输出目录" --seconds 2 --width 297 --height 269
```

平铺到单一目录（目录名前缀防重名，如 `ZK1_开孔.jpg`）：

```bash
python scripts/extract_frames.py --src "源目录" --dst "输出目录" --layout flat
```

### 第 4 步：验证结果

```bash
# 数量
find "输出目录" -type f | wc -l

# 尺寸全量校验（297x269）
python - <<'PY'
from PIL import Image
import os
bad, n = [], 0
for root, _, files in os.walk("输出目录"):
    for fn in files:
        p = os.path.join(root, fn); n += 1
        try:
            if Image.open(p).size != (297, 269):
                bad.append((p, Image.open(p).size))
        except Exception as e:
            bad.append((p, str(e)))
print("总数", n, "尺寸不符/异常", len(bad))
for b in bad[:20]: print(b)
PY
```

> 尺寸校验用 Pillow 更省心（`pip install pillow`）。

## 真实案例回放

- 源：`.中航` 下 24 个 ZK 子目录，共 257 个文件（168 mp4 + 89 jpg）。
- 输出：`1` 目录，168 视频截帧 + 89 图片复制 = 257 张 297×269 jpg，0 失败。
- 后续需求「不分文件夹、平铺到 1 下并删子目录」→ 因 ZK 间存在同名文件（开孔.jpg、第1箱…等），平铺时统一加 `ZK编号_` 前缀避免覆盖。

## 决策要点

| 需求 | 参数/做法 |
|---|---|
| 要保留分文件夹 | `--layout keep`（默认） |
| 不要分文件夹、平铺 | `--layout flat`（自动加目录名前缀，防同名覆盖） |
| 平铺但同名要覆盖 | `--layout single`（慎用） |
| 截的不是第 2 秒 | `--seconds N` |
| 尺寸不是 297×269 | `--width W --height H` |
