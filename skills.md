# GhostCut AI Skills

把 GhostCut API 使用指引装进你的 Agent，让 Agent 帮你选择流程、组装请求、查询状态和排查错误。

## 本文定位

本文是仓库级安装入口，面向还没有安装或准备更新 skill 的用户与 Agent。它主要说明如何安装、更新、手动复制、启动最小示例，以及安装后可以怎么唤起 `ghostcut-api-guide`。

安装完成后，Agent 的实际行为规则、功能路由、强约束和文档地图以 skill 内的 `skills/ghostcut-api-guide/SKILL.md` 为准；具体 API 参数和示例以 `skills/ghostcut-api-guide/references/api-guide/` 为准。

| 文件 | 作用 | 适合谁阅读 |
| --- | --- | --- |
| `skills.md` | 安装前入口、安装和更新命令、使用示例和能力摘要。 | 新用户、准备安装或更新 skill 的 Agent。 |
| `skills/ghostcut-api-guide/SKILL.md` | 安装后的 skill 主说明，包含 Agent 路由规则、强规则和维护规则。 | 已安装 skill 后执行任务的 Agent、维护者。 |
| `skills/ghostcut-api-guide/references/api-guide/` | 具体 API 功能文档、请求体、参数、状态查询和示例。 | 需要组装或校验 API 请求的 Agent。 |

## 一句话安装

需要 Node.js 18+。

```bash
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide
```

如果你的 Agent 支持指定安装目标，可以使用：

```bash
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent codex --global
```

常见 Agent 示例：

```bash
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent claude-code --global
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent cursor --global
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent opencode --global
```

查看仓库中的可安装 skill：

```bash
npx skills add zhaoli-ai/GhostCut-ai --list
```

## 更新已安装的 skill

本仓库的 GitHub `main` 分支是 GhostCut AI Skill 的更新入口。Skill 不会在本地静默自动更新；需要用户主动重新安装最新版本，并重启对应 Agent。

如果你是用 `npx skills` 安装的，可以重新执行对应 Agent 的安装命令：

```bash
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent codex --global
```

如果 CLI 提示 skill 已存在或目标目录已存在，先删除旧版本，再重新执行安装命令。Codex 的常见全局目录如下：

```bash
rm -rf ~/.codex/skills/ghostcut-api-guide
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent codex --global
```

更新后请重启 Codex、Claude Code、Cursor 或 OpenCode，让 Agent 重新加载 skill。

## 手动安装

在支持 Agent Skills 的环境中，将下面目录复制到对应 Agent 的 skills 目录：

```text
skills/ghostcut-api-guide
```

Codex 常见安装位置：

```text
~/.codex/skills/ghostcut-api-guide
```

不同 Agent 的本地目录可能不同；使用 `npx skills add ... --agent <name>` 时，CLI 会自动放到对应位置。

## 让 Agent 来安装

把下面这段话发给你的 AI Agent：

```text
请帮我安装 GhostCut AI Skills：
1. 先检查本机是否安装 Node.js 18+；如果没有，请指导我安装 Node.js。
2. 运行或指导我运行：npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide
3. 如果需要选择安装目标，请优先选择我当前正在使用的 Agent；如果不确定，请询问我。
4. 如果我使用 Codex，请安装到 Codex 全局 skills 目录。
5. 安装完成后，请说“GhostCut API 指引 skill 已装载”，并告诉我如何用它完成一个最小示例。
```

如果 Agent 已经能执行命令，并且你明确使用 Codex，也可以使用更直接的版本：

```text
请帮我安装 GhostCut AI Skills：
1. 检查 Node.js 18+。
2. 执行：npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent codex --global
3. 安装完成后，读取 ghostcut-api-guide 的 SKILL.md，告诉我这个 skill 能做什么。
```

## 技能清单

| Skill | 能力 |
| --- | --- |
| `ghostcut-api-guide` | 面向 Agent 的 GhostCut API 使用指引。具体能力分类和功能清单以 skill 内的 `references/api-guide/llms.txt` 为准。 |

## 使用示例

安装后，可以这样对 Agent 说：

```text
Use $ghostcut-api-guide 帮我把本地视频上传到 GhostCut，并发起视频去字幕任务。
```

```text
Use $ghostcut-api-guide 帮我根据 GhostCut API 指引生成一个字幕压制请求体和 Python 调用示例。
```

```text
Use $ghostcut-api-guide 我想体验一下 API，但手上没有视频，请使用文档中的演示视频 URL。
```

```text
Use $ghostcut-api-guide 帮我查询译制出海任务状态，并说明如何从 task/list 继续查作品详情。
```

```text
Use $ghostcut-api-guide 帮我按 5 分钟快速上手跑通一个视频去文字最小示例。
```

## API 凭证

GhostCut API 通常使用 `AppKey` 和 `AppSecret` 生成 `AppSign`。

安装后请按 skill 内的 `references/api-guide/02-auth-and-sign.md` 获取凭证、设置环境变量并生成签名。不要把真实密钥写入仓库、文档或聊天记录。

## 快速上手

安装后建议先阅读 skill 内的 `references/api-guide/01-quickstart.md`。该文档会引导你使用 `examples/video-inpaint-advanced-lite-fullscreen.payload.json` 创建一个“视频去文字 / 高擦 Lite / 1 个全屏框选范围”的最小任务，并用 `work-status` 查询结果。

视频、图片、SRT 的 URL 与格式要求见 `references/api-guide/03-media-requirements.md`。

## 演示素材

当你只是想体验 API 流程、但暂时没有可用视频或图片时，安装后可查看 skill 内的 `references/sample-assets.md`。该文档集中维护演示视频、演示图片 URL 和使用限制。

## 仓库结构

```text
skills/
└── ghostcut-api-guide/
    ├── SKILL.md
    ├── agents/
    ├── examples/
    ├── references/
    └── scripts/
```

核心入口：

- `skills/ghostcut-api-guide/SKILL.md`：Agent 读取的 skill 主说明。
- `skills/ghostcut-api-guide/examples/`：最小请求体和环境变量模板。
- `skills/ghostcut-api-guide/references/api-guide/llms.txt`：API 指引文档索引。
- `skills/ghostcut-api-guide/references/api-guide/02-auth-and-sign.md`：API 凭证与签名说明。
- `skills/ghostcut-api-guide/references/api-guide/03-media-requirements.md`：素材 URL 与格式要求。
- `skills/ghostcut-api-guide/references/sample-assets.md`：演示素材说明。
- `skills/ghostcut-api-guide/scripts/ghostcut_api.py`：签名、上传、查询状态等辅助脚本。

## 参与贡献

欢迎一起来建设！你可以通过以下方式参与：

- **反馈 Bug** — 遇到问题？[提 Issue](https://github.com/zhaoli-ai/GhostCut-ai/issues) 并附上复现步骤。
- **提需求** — 对新技能或改进有想法？欢迎提 Feature Request。
- **提交 PR** — Fork 仓库，新建分支，改完后提 Pull Request。
- **完善文档** — 错别字、表述不清、更好的示例，统统欢迎。

## 重要说明

本技能会代你调用 GhostCut API，产生的费用由你的账号承担。AI 生成的内容不保证完全准确，用于重要决策前请自行判断。请妥善保管 API Key。本项目仅供体验和参考，不提供任何可用性或稳定性保证。