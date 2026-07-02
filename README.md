# GhostCut-ai

GhostCut-ai contains Agent-oriented skills and reference material for using GhostCut APIs.

当前仓库主要提供一个 Agent Skill：

```text
skills/ghostcut-api-guide/
```

这个 skill 面向 Codex、Claude Code、Cursor、OpenCode 等支持 Agent Skills 的工具使用，帮助 Agent 选择 GhostCut API 调用流程、组装请求体、解释参数、查询任务状态、处理异步轮询和 callback 回调。具体能力清单以 skill 内的 API 索引为准。

## 目录结构

```text
skills/
└── ghostcut-api-guide/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── examples/
    │   ├── .env.example
    │   ├── image-translate.payload.json
    │   ├── video-inpaint-advanced-lite-fullscreen.payload.json
    │   └── work-status.payload.json
    ├── references/
    │   ├── index.md
    │   ├── sample-assets.md
    │   └── api-guide/
    └── scripts/
        ├── ghostcut_api.py
        └── sync_api_guide.py
```

## 信息分工

为了减少重复维护，`README.md` 只做仓库总览和入口路由。安装命令、Agent 运行规则、API 参数、示例素材和脚本用法分别由下面文档维护：

| 内容 | 维护位置 |
| --- | --- |
| 安装、更新、手动复制、给 Agent 的安装提示词 | `skills.md` |
| 安装后 Agent 必须遵守的路由规则、强规则和维护规则 | `skills/ghostcut-api-guide/SKILL.md` |
| API 文档分类和功能索引 | `skills/ghostcut-api-guide/references/api-guide/llms.txt`、`skills/ghostcut-api-guide/references/index.md` |
| 新用户最小闭环 | `skills/ghostcut-api-guide/references/api-guide/01-quickstart.md` |
| API 凭证获取、鉴权和签名 | `skills/ghostcut-api-guide/references/api-guide/02-auth-and-sign.md` |
| 视频、图片、SRT 的格式和 URL 约束 | `skills/ghostcut-api-guide/references/api-guide/03-media-requirements.md` |
| 没有素材时可用的演示视频、图片 URL | `skills/ghostcut-api-guide/references/sample-assets.md` |
| 可复制请求体和辅助脚本用法 | `skills/ghostcut-api-guide/examples/README.md`、`skills/ghostcut-api-guide/SKILL.md` |

## 安装入口

推荐把安装入口发给 Agent，让它按说明安装：

```text
请访问 https://raw.githubusercontent.com/zhaoli-ai/GhostCut-ai/main/skills.md 并按说明为我安装 GhostCut AI Skills。
```

如果网络无法访问 `raw.githubusercontent.com`，打开 GitHub 页面阅读同一份说明：

```text
https://github.com/zhaoli-ai/GhostCut-ai/blob/main/skills.md
```

安装、更新、指定 Agent 和手动复制说明都维护在 `skills.md`。

## 快速上手

安装后先阅读 `skills/ghostcut-api-guide/references/api-guide/01-quickstart.md`。它会引导你完成获取凭证、设置环境变量、提交“视频去文字 / 高擦 Lite / 1 个全屏框选范围”任务，以及查询处理结果的最小闭环。

如果只想查看能力分类和文档索引，先读 `skills/ghostcut-api-guide/references/api-guide/llms.txt`。

## 能力范围

具体能力分类和功能清单以 `skills/ghostcut-api-guide/references/api-guide/llms.txt` 和 `skills/ghostcut-api-guide/references/index.md` 为准。

## 维护建议

更新 API 文档或 skill 时，优先修改对应的单一维护位置，不要把同一条规则复制到多个入口文档。提交前重点检查：

- `skills.md` 是否仍只承担安装、更新和分发入口。
- `skills/ghostcut-api-guide/SKILL.md` 是否仍只承担安装后的 Agent 运行规则。
- `references/api-guide/llms.txt` 和 `references/index.md` 的分类是否一致。
- 示例素材 URL 是否只在 `references/sample-assets.md` 和必要的可复制示例中维护。
- 真实 `AppKey`、`AppSecret`、`.env`、本地缓存和临时文件没有进入仓库。

## 重要说明

本仓库的使用边界和安装入口见 `skills.md`。
本技能会代你调用 GhostCut API，产生的费用由你的账号承担。AI 生成的内容不保证完全准确，用于重要决策前请自行判断。请妥善保管 API Key。本项目仅供体验和参考，不提供任何可用性或稳定性保证。
