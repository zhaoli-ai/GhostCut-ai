---
name: ghostcut-api-guide
description: GhostCut API 使用指引 / API usage guide for agents. 用于选择 GhostCut API 调用流程、组装或校验请求体、解释参数、编写 Python 示例、查询任务状态，以及处理本地文件上传、字幕擦除 subtitle erasure、字幕压制 subtitle burning、OCR/ASR 字幕提取、背景音乐分离、视频翻译配音 video voice translation/dubbing、公共音色 public voices、语言支持、处理状态和“译制出海” Series Editing 模块。
---

# GhostCut API 指引

使用本 skill 时，必须基于随附的 GhostCut API 指引文档工作，不要凭记忆猜测接口路径、字段名、ID 含义、任务类型、语言代码或结果查询流程。

## 参考文档地图

详细文档位于 `references/api-guide/`。当用户目标较宽泛，或还不确定应该调用哪个接口时，先读 `references/api-guide/llms.txt`。当用户只是想体验功能但没有素材时，读 `references/sample-assets.md`，可提供演示视频 URL，并明确说明它不是业务默认素材。

核心入口：

- `references/api-guide/00-api-overview.md`：总览、签名规则、普通单视频流程和文档路由。
- `references/api-guide/10-file-upload.md`：本地视频、SRT、图片上传，获取后续接口可用的 URL。
- `references/api-guide/11-work-status-query.md`：查询 `/v-w-c/gateway/ve/work/status`，读取视频作品结果。
- `references/api-guide/40-series-overview.md`：译制出海模块入口。
- `references/api-guide/41-series-edit-common-task-structure.md`：译制出海通用请求结构、字段来源和 Python 提交通用模板。
- `references/api-guide/42-series-edit-task-list.md`：译制出海 `task/list` 任务查询。
- `references/api-guide/48-series-edit-errors-and-checklist.md`：译制出海错误示例和提交前检查。
- `references/api-guide/90-language-support.md`：不同功能支持的语言。
- `references/api-guide/91-video-process-status.md`：`processStatus` 与公共错误码。
- `references/sample-assets.md`：缺少素材时可选的演示视频 URL 和使用限制。

普通单视频功能：

- 去字幕/去文字：`20-erase-video-subtitle.md`，遮罩框规则见 `21-inpaint-masks-supplement.md`。
- 字幕压制：`22-burn-subtitles.md`，字幕样式细节见 `25-subtitle-style-and-fonts.md`。
- OCR 字幕提取：`23-ocr-subtitle-extraction.md`。
- ASR 字幕提取：`24-asr-subtitle-extraction.md`。
- 背景音乐去除/分离：`30-background-music-separation.md`。
- 视频翻译并重新配音：`31-video-voice-translation.md`，公共音色见 `32-public-voice-characters.md`。

译制出海功能：

- 字幕提取：`43-series-subtitle-extract.md`。
- 字幕擦除：`44-series-subtitle-inpaint.md`。
- AI 配音：`45-series-dubbing.md`。
- 字幕压制：`46-series-subtitle-burn.md`。
- 音频分离：`47-series-audio-separate.md`。
- 项目与视频素材：`49-series-project-and-video-materials.md`。
- 字幕素材与 `slInfo`：`50-series-subtitle-materials.md`。
- 字幕翻译：`51-series-subtitle-translation.md`。
- 翻译术语库：`52-series-translation-glossary.md`。

## 使用流程

1. 先判断用户要调用的是普通单视频 API，还是译制出海模块。
2. 普通单视频任务先读 `00-api-overview.md`；译制出海任务先读 `40-series-overview.md`。
3. 组装参数前必须阅读对应功能文档，不要从记忆推断接口路径或字段名。
4. 保持文档中的请求层级。译制出海任务使用 `items[]`、`workDto`、`videoEditParamsDto`。
5. 如果用户提供本地文件路径，先读 `10-file-upload.md` 完成上传；任务创建接口通常需要 URL 或素材 ID，不直接接收本地路径。
6. 涉及语言字段时，读 `90-language-support.md`，不要凭常识猜测语言代码。
7. 按正确流程查询状态和结果：
   - 普通单视频任务：创建任务后拿作品 ID，再调用 `/v-w-c/gateway/ve/work/status`。
   - 译制出海任务：先调用 `task/list`；如果需要作品 ID、播放地址或作品详情，用 `task/list.body[].id` 作为 project/task ID 调用 `/v-w-c/gateway/ve/work/status`，再从 `body.content[].id` 读取作品 ID。

## 快速路由

- 用户给本地文件路径：读 `10-file-upload.md`，需要实际上传时可用 `scripts/ghostcut_api.py upload`。
- 用户没有视频但想体验：读 `references/sample-assets.md`，提供演示视频 URL，并提醒依赖语音、字幕或剧集上下文的功能应换成真实素材。
- 用户要查询普通单视频结果：读 `11-work-status-query.md`，需要实际查询时可用 `scripts/ghostcut_api.py work-status`。
- 用户要查询译制出海任务：读 `42-series-edit-task-list.md`，需要实际查询时可用 `scripts/ghostcut_api.py task-list`。
- 用户要基于前序译制出海结果继续处理：先查 `task/list` 拿任务 ID，再查 `/work/status` 拿 `body.content[].id` 作为作品 ID。
- 用户要译制出海配音：至少读 `40-series-overview.md`、`41-series-edit-common-task-structure.md`、`45-series-dubbing.md`；涉及音色时读 `32-public-voice-characters.md`；涉及字幕样式时读 `25-subtitle-style-and-fonts.md`。

## 强规则

- 不要把 `task/list.body[].id` 当成作品 ID。它是任务 ID，也可理解为 project ID。
- 后续译制出海任务需要 `workDto.materialWorkIds` 时，取 `/work/status.body.content[].id`。
- 不要把 `idRelation` 当成业务字段使用。
- 译制出海配音中，`workDto.idVeMaterialSrt` 和 `workDto.extraOptions.customer_input` 二选一，不能同时传。
- 译制出海配音不能完全不传字幕；情感克隆模式也必须提供字幕输入。
- 经典配音模式使用 `wyTaskType=FULL`，并传 `character_voices[]`。
- 情感克隆模式使用 `wyTaskType=VOICE_CLONE_PRO`，不传 `character_voices[]`。
- `voice_type=CLONE` 表示经典模式下的超真实音色，不表示情感克隆模式。
- 公共音色统一使用 `character_voices[].id_ve_voice_character`，取值来自 `voicecharacter/aggregate/list` 返回的 `body[].id`。
- AI 配音任务中不要主动生成字幕擦除字段，除非功能文档明确要求先创建字幕擦除任务。
- 字幕擦除遮罩框和 OCR 框使用 `0` 到 `1` 的相对坐标，点序为左上、右上、右下、左下。

## 可用脚本

脚本位于 `scripts/`，用于减少重复签名、上传和查询代码。`AppKey` 和 `AppSecret` 可在鬼手剪辑网站的账号设置或账户信息中查看。运行脚本前优先使用环境变量提供凭证，不要把真实密钥写入文档或提交到仓库：

```bash
export GHOSTCUT_APP_KEY="your_app_key"
export GHOSTCUT_APP_SECRET="your_app_secret"
```

常用命令：

- `python scripts/ghostcut_api.py sign --payload payload.json`：为 JSON 请求体生成 `AppSign`。
- `python scripts/ghostcut_api.py post --path /v-w-c/gateway/ve/work/status --payload payload.json`：发送签名后的 GhostCut JSON 请求。
- `python scripts/ghostcut_api.py upload --file /path/input.mp4 --material-file-type video`：上传本地文件，输出 URL 和 OSS key。
- `python scripts/ghostcut_api.py work-status 521461135`：查询 `/v-w-c/gateway/ve/work/status` 并汇总状态和常见结果 URL。
- `python scripts/ghostcut_api.py task-list --id-series 10001 --task-type-in SERIES_CLIP2 SERIES_CLIP3`：查询译制出海任务列表。

维护快照时使用：

- `python scripts/sync_api_guide.py --check`：检查 `api指引/` 与 `references/api-guide/` 是否一致。
- `python scripts/sync_api_guide.py`：从 `api指引/` 同步当前文档快照到 skill。

## 文档编写与维护

更新随附 API 指引时，保持面向 Agent 的写法：

- 推荐稳定章节顺序：检查清单、使用流程、关键字段、请求体、完整 Python 示例、结果查询、Agent 决策规则、相关文档。
- Python 示例要能直接复制：包含 imports、凭证占位、签名函数、请求体、POST 调用和结果打印。
- 避免猜测性措辞、未完成占位、内部历史表述，以及业务流程中用不到的字段解释。
- 长表格和通用规则优先链接到共享文档，不要在多个功能文档里重复维护字幕样式、语言列表、状态枚举或遮罩框规则。
- 修改主项目 `api指引/` 后，应运行 `python scripts/sync_api_guide.py --check`；如有差异，再运行 `python scripts/sync_api_guide.py` 更新 skill 快照。
