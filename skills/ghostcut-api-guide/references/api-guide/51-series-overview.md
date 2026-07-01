# 译制出海剪辑 API 总览

> 本模块是“译制出海”的独立 API 文档入口。它面向剧集或项目级素材处理，围绕 `idSeries`、`idMaterialVideo` 和 `items[]` 发起批量任务。不要把本模块的请求结构和普通单视频处理接口混用。

## 模块特点

- 剪辑任务接口前缀：`gateway/ve/series/edit`
- 项目、素材和字幕准备接口前缀：`gateway/ve/series`
- 字幕翻译和术语库接口前缀：`gateway/ve/translate`
- 请求和返回均使用 JSON。
- 请求需要 `AppKey` 和 `AppSign` 签名。
- 一个任务请求可以同时提交多个视频，每个视频对应 `items[]` 中一个元素。
- 顶层 `sourceLang`、`lang` 使用语种 code，例如 `zh`、`en`、`ja`、`ko`。
- 无目标语种的任务，`lang` 可传空字符串。
- 生产接入推荐在顶层传入 `callback` 接收处理结果通知，回调格式、验签、重试和幂等规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。
- 提交任务后，可通过 `task/list` 查询任务状态；若还需要作品 ID、作品详情或播放地址，再基于 `task/list` 返回的任务 ID 调用 `/work/status`。后续任务要复用已有作品结果时，把 `/work/status` 返回的 `body.content[].id` 填进 `workDto.materialWorkIds`。

## 认证与签名

译制出海剪辑 API 使用 `AppKey` + `AppSign` 鉴权。

请求头：

```http
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

签名规则：

```text
body_str = 请求 JSON 字符串
body_md5hex = md5(body_str).hexdigest()
AppSign = md5(body_md5hex + AppSecret).hexdigest()
```

注意：用于签名的 `body_str` 必须和实际发送的请求体完全一致。建议在同一段代码中生成 `body_str`、计算 `AppSign` 并发送请求。

## 模块文档

| 文档 | 说明 |
| --- | --- |
| [通用任务结构](./52-series-edit-common-task-structure.md) | 说明 `idSeries`、`items[]`、`workDto`、`videoEditParamsDto`、`customer_input` 和 `wyVoiceParam`。 |
| [任务查询](./53-series-edit-task-list.md) | 说明 `task/list` 查询接口、分页参数和任务计数字段。 |
| [异步任务、轮询和回调机制](./15-async-and-callbacks.md) | 说明 callback 回调格式、验签、重试、幂等和补偿轮询。 |
| [字幕提取](./54-series-subtitle-extract.md) | 说明 ASR 和 OCR 两种字幕提取任务。 |
| [字幕擦除](./55-series-subtitle-inpaint.md) | 说明基础、Lite、Pro 字幕擦除任务。 |
| [AI 配音](./56-series-dubbing.md) | 说明经典模式、手动音色选择、超真实音色和情感克隆模式。 |
| [字幕压制](./57-series-subtitle-burn.md) | 说明基于原视频或去文字后视频压制字幕。 |
| [音频分离](./58-series-audio-separate.md) | 说明生成去 BGM 后视频的任务。 |
| [错误与检查清单](./59-series-edit-errors-and-checklist.md) | 说明通用返回、失败示例和发起任务前检查项。 |
| [项目与视频素材](./60-series-project-and-video-materials.md) | 说明项目创建、项目查询、视频上传、视频导入、视频查询和素材替换。 |
| [字幕素材管理](./61-series-subtitle-materials.md) | 说明 SRT 上传、字幕内容创建、字幕列表查询、`slInfo` 解析、字幕更新、删除和复制。 |
| [字幕翻译任务](./62-series-subtitle-translation.md) | 说明专家版 Agent 字幕翻译、翻译任务查询、人工审核推进和译后字幕获取。 |
| [翻译术语库](./63-series-translation-glossary.md) | 说明角色名、称谓和专有名词术语的创建、查询、更新和删除。 |

## 支持的任务

| 任务 | 接口路径 |
| --- | --- |
| 字幕提取 | `gateway/ve/series/edit/task/subtitle/extract` |
| 字幕擦除 | `gateway/ve/series/edit/task/subtitle/inpaint` |
| AI 配音 | `gateway/ve/series/edit/task/dubbing` |
| 字幕压制 | `gateway/ve/series/edit/task/subtitle/burn` |
| 音频分离 | `gateway/ve/series/edit/task/audio/separate` |
| 查询任务 | `gateway/ve/series/edit/task/list` |

## 准备与辅助接口

| 能力 | 接口路径 | 说明 |
| --- | --- | --- |
| 创建项目 | `gateway/ve/series/create` | 获得 `idSeries`。 |
| 查询项目 | `gateway/ve/series/list` | 按项目名、ID、删除状态等查询项目。 |
| 导入视频 URL | `gateway/ve/series/video/import` | 获得 `idMaterialVideo`。 |
| 查询视频素材 | `gateway/ve/series/video/list` | 确认 `downloadStatus`、`processStatus` 和素材元信息。 |
| 创建字幕素材 | `gateway/ve/series/srt/create` | 用 SRT/VTT 内容创建字幕素材。 |
| 查询字幕素材 | `gateway/ve/series/srt/list` | 获得 `idVeMaterialSrt`，读取 `slInfo`。 |
| 字幕翻译 | `gateway/ve/translate/subtitle` | 翻译源字幕并生成新字幕素材。 |
| 术语库 | `gateway/ve/translate/*TranslateGlossary2` | 维护项目级翻译术语。 |

## 使用流程

1. **准备剧集和素材**
   先通过 [项目与视频素材](./60-series-project-and-video-materials.md) 创建或查询项目，拿到 `idSeries`。每个视频素材都要上传、导入或查询到 `idMaterialVideo`，并确认 `downloadStatus=1`、`processStatus=1`。

2. **准备字幕素材**
   如果任务要使用已有字幕，先通过 [字幕素材管理](./61-series-subtitle-materials.md) 上传、创建或查询字幕，拿到 `idVeMaterialSrt`。如果字幕来自 ASR/OCR/翻译任务，也要通过字幕列表确认字幕结果。

3. **可选：翻译字幕和术语库**
   如果目标只是生成译后字幕，使用 [字幕翻译任务](./62-series-subtitle-translation.md)。如果要固定角色名、称谓或专有名词，先维护 [翻译术语库](./63-series-translation-glossary.md)。

4. **选择剪辑任务类型**
   根据用户目标选择字幕提取、字幕擦除、AI 配音、字幕压制或音频分离。

5. **组装通用任务结构**
   顶层传 `idSeries`、`projectName`、`sourceLang`、`lang`、`callback` 和 `items[]`。每个 `items[]` 元素对应一个视频。

6. **填充每个视频的任务参数**
   每个 `items[]` 中至少包含 `idMaterialVideo`、`workDto` 和 `videoEditParamsDto`。具体字段按任务文档填写。

7. **提交任务**
   调用对应的 `gateway/ve/series/edit/task/...` 接口。外层 `code=200` 表示请求被接受，不等于所有视频都处理完成。

8. **接收回调或查询任务**
   生产接入推荐通过 `callback` 接收结果；也可调用 [任务查询](./53-series-edit-task-list.md)，根据 `idSeries`、`ids`、语言、分页等条件查询任务列表，关注 `successWorkCount`、`errorWorkCount` 和 `processingWorkCount`，并从返回结构中读取处理结果。

9. **复用前置任务结果**
   如果后续任务要基于“去文字后视频”，先通过 `task/list` 查询前序任务，拿到对应任务的 `body[].id`。这个字段是任务 ID；再按 [视频任务状态查询](./11-work-status-query.md) 的方式调用 `/v-w-c/gateway/ve/work/status`，从返回的 `body.content[].id` 读取作品 ID，并填入后续任务的 `workDto.materialWorkIds`。

## 任务选择规则

| 用户目标 | 使用文档 | 关键参数 |
| --- | --- | --- |
| 从音频人声提取字幕 | [字幕提取](./54-series-subtitle-extract.md) | `needWanyin=1`、`wyTaskType=ONLY_ASR` |
| 从画面硬字幕提取字幕 | [字幕提取](./54-series-subtitle-extract.md) | `needChineseOcclude=14`、`videoInpaintMasks` |
| 擦除字幕或文字 | [字幕擦除](./55-series-subtitle-inpaint.md) | `needChineseOcclude=1` 或 `2` |
| 翻译并重新配音 | [AI 配音](./56-series-dubbing.md) | 经典模式：`wyTaskType=FULL`、`wyVoiceParam.character_voices[]` |
| 情感克隆配音 | [AI 配音](./56-series-dubbing.md) | `wyTaskType=VOICE_CLONE_PRO`，不手动传 `character_voices[]`，但仍必须提供字幕输入 |
| 把字幕压到视频画面 | [字幕压制](./57-series-subtitle-burn.md) | `wyTaskType=NO_TTS`、`wyNeedText=1` |
| 生成去 BGM 后的视频 | [音频分离](./58-series-audio-separate.md) | `removeBgAudio=2` |
| 只翻译字幕并生成新字幕素材 | [字幕翻译任务](./62-series-subtitle-translation.md) | `taskSubType=agent`、`translateOptions` |
| 固定人名、称谓或专有名词译法 | [翻译术语库](./63-series-translation-glossary.md) | `idSeries`、`idParent`、`lang` |

## Agent 决策规则

- 用户提到“译制出海”“剧集”“项目素材”“idSeries”“idMaterialVideo”时，优先使用本模块。
- 没有 `idSeries` 时，先读 [项目与视频素材](./60-series-project-and-video-materials.md)，不要直接组装剪辑任务。
- 没有 `idMaterialVideo` 时，先上传、导入或查询视频素材，并确认素材可用。
- 选择字幕素材输入方式时，先读 [字幕素材管理](./61-series-subtitle-materials.md) 获取 `idVeMaterialSrt`，不要猜字幕 ID；选择 `customer_input` 时不要再传 `idVeMaterialSrt`。
- 本模块提交任务时使用 `items[]`、`workDto`、`videoEditParamsDto`，不要使用普通单视频接口的扁平请求体。
- 提交任务的语言字段是 `sourceLang`、`lang`；查询任务的语言过滤字段是 `sourceLanguage`、`targetLanguage`。
- 每个视频素材都要有一个 `items[]` 元素，不要把多个视频塞进同一个 `workDto`。
- 需要基于前序处理结果继续处理时，先通过 `task/list` 取得前序任务 ID，再通过 `/work/status` 查询该任务下的作品详情，把 `body.content[].id` 作为后续 `workDto.materialWorkIds`。
- 配音模式不要和音色类型混用：`voice_type=CLONE` 表示超真实音色，仍属于经典模式；情感克隆模式通过 `wyTaskType=VOICE_CLONE_PRO` 区分。
- 译制出海 `/series/edit/task/dubbing` 的经典模式和情感克隆模式都必须提供字幕输入；不要把普通单视频配音的默认 ASR 规则套用到本模块。
- 外层 `code=200` 只表示接口请求成功；生产接入推荐通过 `callback` 接收最终结果，任务是否完成也可通过 [任务查询](./53-series-edit-task-list.md) 判断。
