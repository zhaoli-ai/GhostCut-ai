# GhostCut AI Skills

把 GhostCut API 使用指引装进你的 Agent，让 Agent 帮你选择流程、组装请求、查询状态和排查错误。

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
| `ghostcut-api-guide` | 面向 Agent 的 GhostCut API 使用指引。覆盖文件上传、去字幕、字幕压制、OCR/ASR 字幕提取、背景音乐分离、视频翻译配音、公共音色、语言支持、状态查询和译制出海模块。 |

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

## API 凭证

GhostCut API 通常使用 `AppKey` 和 `AppSecret` 生成 `AppSign`。

`AppKey` 和 `AppSecret` 可在鬼手剪辑网站的账号设置或账户信息中查看。

不要把真实密钥写入仓库、文档或聊天记录。需要运行脚本时，建议使用环境变量：

```bash
export GHOSTCUT_APP_KEY="your_app_key"
export GHOSTCUT_APP_SECRET="your_app_secret"
```

## 演示视频

当你只是想体验 API 流程、但暂时没有可用视频时，可以使用：

```text
https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4
```

该视频只适合演示普通视频 URL 如何填写。涉及 ASR、配音、角色识别、字幕翻译或真实业务质量验证时，应换成你自己的视频。

## 仓库结构

```text
skills/
└── ghostcut-api-guide/
    ├── SKILL.md
    ├── agents/
    ├── references/
    └── scripts/
```

核心入口：

- `skills/ghostcut-api-guide/SKILL.md`：Agent 读取的 skill 主说明。
- `skills/ghostcut-api-guide/references/api-guide/llms.txt`：API 指引文档索引。
- `skills/ghostcut-api-guide/references/sample-assets.md`：演示素材说明。
- `skills/ghostcut-api-guide/scripts/ghostcut_api.py`：签名、上传、查询状态等辅助脚本。

## 重要说明

本仓库提供的是面向 Agent 的 GhostCut API 使用指引，不包含真实账户凭证，也不替代 GhostCut 官方接口权限、计费和服务策略。实际调用 API 前，请确认账户权限、素材来源、语言支持和接口返回状态。
