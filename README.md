# video-frame-extractor

批量「视频截帧 + 图片复制 + 统一缩放」的 AI Skill。可直接导入任意支持 SKILL 规范的 AI 代理（如 WorkBuddy / Claude Code 类），让 AI 自主完成媒体批处理。

## 功能

- 递归遍历源目录，识别视频与图片。
- 视频：截取指定秒（默认第 2 秒）画面。
- 图片：复制并统一缩放。
- 所有输出统一 resize 到固定尺寸（默认 **297×269**）。
- 三种输出组织方式：保留目录结构 / 平铺（目录名前缀防重名）/ 平铺无前缀。
- 内置 Windows 中文路径写入兼容（`cv2.imwrite` 对中文路径静默失败，改用 `imencode+tofile` 规避）。

## 目录结构

```
video-frame-extractor/
├── SKILL.md                        # Skill 元数据 + 使用说明（AI 入口）
├── scripts/
│   └── extract_frames.py           # 核心处理脚本
├── references/
│   ├── workflow.md                 # 完整操作流程与真实案例
│   └── environment.md              # 环境依赖与排错
└── README.md
```

## 快速开始

```bash
# 1. 安装依赖（国内可加清华镜像）
pip install opencv-python-headless numpy -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 运行
python scripts/extract_frames.py \
  --src "源目录" --dst "输出目录" \
  --seconds 2 --width 297 --height 269

# 3. 平铺输出（目录名前缀防重名）
python scripts/extract_frames.py --src "源目录" --dst "输出目录" --layout flat
```

## 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `--src` | 必填 | 源目录（递归遍历） |
| `--dst` | 必填 | 输出目录 |
| `--seconds` | `2.0` | 截取第几秒 |
| `--width` / `--height` | `297` / `269` | 输出尺寸 |
| `--quality` | `95` | jpg 质量 |
| `--layout` | `keep` | `keep`/`flat`/`single` |
| `--flat-prefix-sep` | `_` | flat 模式前缀分隔符 |

## 导入到其他 AI

把整个 `video-frame-extractor/` 目录作为 Skill 安装（放入对应 AI 的 skills 目录，或通过其 Skill 导入功能）。SKILL.md 顶部 frontmatter 的 `description` 已包含触发词，AI 会在用户提到「视频截帧 / 截取视频第 X 秒 / 统一图片尺寸」等需求时自动加载本 Skill。

## License

MIT
