# GhostCut-ai

GhostCut-ai contains Agent-oriented skills and reference material for using GhostCut APIs.

当前仓库主要提供一个 Agent Skill：

```text
skills/ghostcut-api-guide/
```

这个 skill 面向 Codex、Claude Code、Cursor、OpenCode 等支持 Agent Skills 的工具使用，帮助 Agent 选择 GhostCut API 调用流程、组装请求体、解释参数、查询任务状态，并处理本地文件上传、字幕擦除、字幕压制、OCR/ASR 字幕提取、背景音乐分离、视频翻译配音、公共音色查询、语言支持和“译制出海”模块。

## 目录结构

```text
skills/
└── ghostcut-api-guide/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── references/
    │   ├── index.md
    │   ├── sample-assets.md
    │   └── api-guide/
    └── scripts/
        ├── ghostcut_api.py
        └── sync_api_guide.py
```

## 如何使用

### 使用 npx skills 安装

如果本地已经安装 Node.js，可以直接用 `npx skills` 从 GitHub 安装：

```bash
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide
```

安装到 Codex 的全局 skills 目录：

```bash
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent codex --global
```

安装到 Claude Code：

```bash
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent claude-code --global
```

安装到 Cursor：

```bash
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent cursor --global
```

安装到 OpenCode：

```bash
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent opencode --global
```

也可以一次选择多个 Agent：

```bash
npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide --agent codex --agent claude-code --agent cursor --global
```

也可以先查看仓库中可安装的 skill：

```bash
npx skills add zhaoli-ai/GhostCut-ai --list
```

说明：

- `zhaoli-ai/GhostCut-ai` 是 GitHub 的 `owner/repo` 写法。
- `ghostcut-api-guide` 来自 `skills/ghostcut-api-guide/SKILL.md` 中的 `name` 字段。
- `--agent` 用于指定安装到哪个 Agent；不确定本地支持哪些 Agent 时，可以先运行 `npx skills add zhaoli-ai/GhostCut-ai --skill ghostcut-api-guide`，按交互提示选择。
- 如果本地没有 Node.js 或不想使用命令行，可以继续使用下面的手动复制方式。

### 手动安装

在支持 Agent Skills 的环境中，将下面目录复制到对应 Agent 的 skills 目录：

```text
skills/ghostcut-api-guide
```

Codex 常见安装位置：

```text
~/.codex/skills/ghostcut-api-guide
```

不同 Agent 的本地目录可能不同；使用 `npx skills add ... --agent <name>` 时，CLI 会自动放到对应位置。

使用时可以对 Agent 说：

```text
Use $ghostcut-api-guide 帮我根据 GhostCut API 指引组装请求
```

如果 Agent 已经在本仓库上下文中，也可以直接要求它阅读：

```text
skills/ghostcut-api-guide/SKILL.md
```

## 能力范围

该 skill 覆盖：

- 本地文件上传并获取可用于 GhostCut API 的 URL
- 视频去字幕、去文字、去 logo 或固定区域擦除
- 字幕压制和字幕样式配置
- OCR 画面字幕提取
- ASR 语音字幕提取
- 背景音乐去除/分离
- 视频翻译并重新配音
- 公共音色查询
- 译制出海项目、素材、字幕和批量任务流程
- 任务状态查询、结果读取和错误排查
- 不同功能支持的语言列表

## API 凭证

GhostCut API 通常使用 `AppKey` 和 `AppSecret` 生成 `AppSign`。

`AppKey` 和 `AppSecret` 可在鬼手剪辑网站的账号设置或账户信息中查看。

不要把真实密钥写入仓库、文档或提交记录。需要运行脚本时，建议使用环境变量：

```bash
export GHOSTCUT_APP_KEY="your_app_key"
export GHOSTCUT_APP_SECRET="your_app_secret"
```

## 演示视频

当用户只是想体验 API 流程、但暂时没有可用视频时，可以使用演示视频：

```text
https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4
```

该视频只适合演示普通视频 URL 如何填写。涉及 ASR、配音、角色识别、字幕翻译或真实业务质量验证时，应换成用户自己的视频。

## 脚本说明

`skills/ghostcut-api-guide/scripts/ghostcut_api.py` 是通用辅助脚本，用于：

- 生成 `AppSign`
- 发送签名后的 GhostCut JSON 请求
- 上传本地文件并输出 URL
- 查询 `/v-w-c/gateway/ve/work/status`
- 查询译制出海 `task/list`

示例：

```bash
python skills/ghostcut-api-guide/scripts/ghostcut_api.py work-status 521461135
```

`skills/ghostcut-api-guide/scripts/sync_api_guide.py` 用于维护 skill 内的 API 指引快照，检查或同步 `references/api-guide/`。

## 维护建议

更新 API 文档或 skill 后，建议运行：

```bash
python /path/to/skill-creator/scripts/quick_validate.py skills/ghostcut-api-guide
python -m py_compile skills/ghostcut-api-guide/scripts/ghostcut_api.py skills/ghostcut-api-guide/scripts/sync_api_guide.py
```

提交前请确认：

- 没有真实 `AppKey`、`AppSecret` 或其他密钥
- 没有上传 `.env`、本地缓存、临时文件或 IDE 配置
- `skills/ghostcut-api-guide/SKILL.md` 中的入口和引用路径仍然有效

## 重要说明

本仓库提供的是面向 Agent 的 GhostCut API 使用指引，不包含真实账户凭证，也不替代 GhostCut 官方接口权限、计费和服务策略。实际调用 API 前，请确认账户权限、素材来源、语言支持和接口返回状态。
