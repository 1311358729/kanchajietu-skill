# 环境依赖与排错

## 依赖清单

| 依赖 | 版本建议 | 用途 | 安装 |
|---|---|---|---|
| Python | 3.8+ | 运行脚本 | 系统自带或官网安装 |
| opencv-python-headless | 5.x / 4.x | 视频解码 + 截帧 + 图像缩放 | `pip install opencv-python-headless` |
| numpy | 1.x/2.x | 图像数组读写（中文路径） | `pip install numpy`（随 opencv 自动装） |
| pillow | 可选 | 结果尺寸校验 | `pip install pillow` |

> **不需要 ffmpeg**：OpenCV（headless 版）内置视频解码与帧定位，对常见 mp4（H.264）足够。

## 一键安装（国内加速）

```bash
pip install opencv-python-headless numpy pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 环境自检

```bash
python -c "import cv2, numpy; print('cv2', cv2.__version__, '| numpy', numpy.__version__)"
# 期望输出类似：cv2 5.0.0.93 | numpy 2.5.4
```

## 常见问题排错

### 1. 脚本报成功，但输出目录是空的 / 没有文件

**根因**：Windows 下 `cv2.imwrite` 对含中文（或非 ASCII）的路径**静默失败**——不抛异常、返回 False，但文件根本没写进去。

**解决**：必须用 `cv2.imencode(".jpg", img, ...)` 得到字节缓冲，再 `buf.tofile(中文路径)` 写入。本脚本已内置 `imwrite_cn()`，勿改回 `cv2.imwrite`。

### 2. 某个视频打不开 / 读帧失败

- 确认扩展名在支持列表内；非标准扩展名可在脚本 `DEFAULT_VIDEO_EXT` 里加。
- 中文路径 + 个别 OpenCV 版本导致 `VideoCapture` 打开失败：先复制到临时英文路径再读：

```python
import shutil, tempfile, cv2
tmp = os.path.join(tempfile.gettempdir(), "tmp_video" + os.path.splitext(src)[1])
shutil.copy(src, tmp)
cap = cv2.VideoCapture(tmp)
# ... 读帧后 os.remove(tmp)
```

### 3. 视频短于目标秒数，截出来是黑的

脚本在 `CAP_PROP_POS_MSEC` 定位后若读不到帧，会回退读第一帧，不会全黑。若仍异常，检查视频本身是否损坏（可先用 `ffprobe`/播放器确认）。

### 4. 平铺后文件被覆盖 / 数量变少

不同子目录存在同名文件（如 `开孔.jpg`）。平铺必须用 `--layout flat`（自动加目录名前缀），不要用 `--layout single`。

### 5. 想保持图片宽高比而不是拉伸

默认直接 `cv2.resize` 拉伸到固定尺寸。若要保比例（留白/裁剪），需改脚本 `resize_to()`，属于定制需求。

## 跨平台说明

- Windows / macOS / Linux 均可运行。
- macOS/Linux 路径通常无中文，`imwrite` 也能用，但脚本统一用 `imencode+tofile` 无副作用。
