> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# GhostCut API 总览

> 本文是 GhostCut API 文档的入口页，用于帮助人或 Agent 判断应该调用哪个功能、先阅读哪个文档，以及哪些公共规则需要在所有功能中复用。具体参数、请求示例和响应字段以各功能文档为准。

## 文档编号

| 编号 | 范围 |
| --- | --- |
| `00` | 总览入口。 |
| `10-11` | 通用准备和状态查询能力。 |
| `20-32` | 普通单视频处理能力。 |
| `40-52` | 译制出海模块。 |
| `90-91` | 参考附录。 |
| `99` | 文档维护。 |

## 快速选择功能

| 用户目标 | 优先阅读 | 常用关联文档 |
| --- | --- | --- |
| 本地视频、本地 SRT 或本地图片需要先传给 GhostCut | [文件上传](./10-file-upload.md) | 后续再进入具体功能文档 |
| 查询普通单视频任务是否完成、读取结果 URL | [视频任务状态查询](./11-work-status-query.md) | [视频处理状态枚举](./91-video-process-status.md) |
| 去掉视频中的字幕、文字、角标、logo 或固定区域 | [视频去字幕](./20-erase-video-subtitle.md) | [字幕 mask 补充说明](./21-inpaint-masks-supplement.md)、[视频任务状态查询](./11-work-status-query.md) |
| 解释擦除模型版本差异、手动画框坐标、`videoInpaintMasks` | [字幕 mask 补充说明](./21-inpaint-masks-supplement.md) | [视频去字幕](./20-erase-video-subtitle.md) |
| 把已有 SRT 字幕硬压制到视频画面里 | [为视频压制字幕](./22-burn-subtitles.md) | [字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md)、[文件上传](./10-file-upload.md) |
| 从画面硬字幕中识别并导出 SRT | [OCR 提取视频字幕](./23-ocr-subtitle-extraction.md) | [字幕 mask 补充说明](./21-inpaint-masks-supplement.md)、[语言列表](./90-language-support.md) |
| 从视频音频的人声中识别并导出 SRT | [ASR 提取视频字幕](./24-asr-subtitle-extraction.md) | [语言列表](./90-language-support.md) |
| 配置字幕字体、描边、阴影、背景、样式模板 | [字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md) | [为视频压制字幕](./22-burn-subtitles.md)、[视频语音翻译与重新配音](./31-video-voice-translation.md) |
| 去掉或分离视频背景音乐，保留人声和环境声 | [背景音乐去除/分离](./30-background-music-separation.md) | [文件上传](./10-file-upload.md)、[视频任务状态查询](./11-work-status-query.md) |
| 翻译视频并生成新配音，或重新配音 | [视频语音翻译与重新配音](./31-video-voice-translation.md) | [公共音色查询接口](./32-public-voice-characters.md)、[字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md)、[语言列表](./90-language-support.md) |
| 为视频配音功能选择公共音色 | [公共音色查询接口](./32-public-voice-characters.md) | [视频语音翻译与重新配音](./31-video-voice-translation.md) |
| 处理译制出海剧集、项目素材或批量视频任务 | [译制出海剪辑 API 模块](./40-series-overview.md) | [译制出海项目与视频素材](./49-series-project-and-video-materials.md)、[译制出海字幕素材管理](./50-series-subtitle-materials.md)、[译制出海通用任务结构](./41-series-edit-common-task-structure.md) |
| 翻译译制出海字幕、维护术语库或审核翻译 | [译制出海字幕翻译任务](./51-series-subtitle-translation.md) | [译制出海翻译术语库](./52-series-translation-glossary.md)、[译制出海字幕素材管理](./50-series-subtitle-materials.md) |
| 查询不同功能支持哪些语种 | [不同功能支持的语言列表](./90-language-support.md) | 需要语种参数的具体功能文档 |
| 判断 `processStatus` 状态值、失败原因是什么 | [视频处理状态枚举](./91-video-process-status.md) | [视频任务状态查询](./11-work-status-query.md) |
| 维护本文档项目的写作规则和 Cursor 配置 | [Cursor 配置](./99-cursor.md) | [完整文档索引](./llms.txt) |

## 通用调用流程

本节适用于普通单视频处理能力，也就是 `10-32` 编号范围内的文档。译制出海模块使用 `idSeries`、`items[]` 和 `task/list`，不要套用本节的 `/work/status` 流程。

普通单视频处理功能通常是异步任务，通用流程如下：

1. 准备素材 URL。
   如果素材只有本地文件，先使用[文件上传](./10-file-upload.md)获得临时 URL。
2. 准备 `AppKey` 和 `AppSecret`。
   可在鬼手剪辑网站的账号设置或账户信息中查看。
3. 根据功能文档组装请求体。
   常见创建任务接口为 `/v-w-c/gateway/ve/work/free`。
4. 用请求体生成 `AppSign`。
5. 发送创建任务请求。
   成功后通常从 `body.dataList[0].id` 获取作品 ID。
6. 按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status` 查询任务状态。
7. 当 `processStatus == 1` 时读取结果 URL。
   如果 `processStatus < 1`，继续等待并轮询；如果 `processStatus > 1`，参考[视频处理状态枚举](./91-video-process-status.md)排查。

## 认证与签名

GhostCut 业务接口通常使用 `AppKey` + `AppSign` 鉴权。

请求头：

```http
Content-Type: application/json
AppKey: <your_app_key>
AppSign: <generated_sign>
```

签名规则：

```text
body_str = 请求 JSON 字符串
body_md5hex = md5(body_str).hexdigest()
AppSign = md5(body_md5hex + AppSecret).hexdigest()
```

注意事项：

- 用于签名的 `body_str` 必须和实际发送的请求体完全一致。
- 不要先用一种 JSON 字符串生成签名，再发送另一种格式化后的 JSON。
- 建议在同一段代码中生成 `body_str`、计算 `AppSign` 并发送请求。
- 文件上传到 OSS 的 `multipart/form-data` 请求本身不使用该签名；获取上传凭证等 GhostCut 业务接口仍需要签名。

## 常见接口路径

| 接口 | 用途 | 相关文档 |
| --- | --- | --- |
| `POST /v-w-c/gateway/ve/work/free` | 创建视频处理任务，如擦除、字幕压制、OCR/ASR、背景音乐分离、视频语音翻译 | 各功能文档 |
| `POST /v-w-c/gateway/ve/work/status` | 查询普通单视频处理任务状态和结果 URL | [视频任务状态查询](./11-work-status-query.md) |
| `POST /v-w-c/gateway/ve/file/upload/policy/apply` | 获取本地文件上传凭证 | [文件上传](./10-file-upload.md) |
| `POST /v-w-c/enum/query2` | 查询枚举，如 `ProcessStatus`、语言列表等 | [视频处理状态枚举](./91-video-process-status.md) |
| `POST /v-w-c/gateway/ve/voicecharacter/aggregate/list` | 查询公共音色角色、语言试听和标签 | [公共音色查询接口](./32-public-voice-characters.md) |
| `POST /v-w-c/gateway/ve/series/create` | 创建译制出海项目并获得 `idSeries` | [译制出海项目与视频素材](./49-series-project-and-video-materials.md) |
| `POST /v-w-c/gateway/ve/series/video/import` | 将视频 URL 导入译制出海项目并获得 `idMaterialVideo` | [译制出海项目与视频素材](./49-series-project-and-video-materials.md) |
| `POST /v-w-c/gateway/ve/series/srt/list` | 查询译制出海字幕素材并获得 `idVeMaterialSrt` | [译制出海字幕素材管理](./50-series-subtitle-materials.md) |
| `POST /v-w-c/gateway/ve/series/edit/task/...` | 创建译制出海剧集/项目级批量任务 | [译制出海剪辑 API 模块](./40-series-overview.md) |
| `POST /v-w-c/gateway/ve/series/edit/task/list` | 查询译制出海任务列表和处理进度 | [译制出海任务查询](./42-series-edit-task-list.md) |
| `POST /v-w-c/gateway/ve/translate/subtitle` | 创建译制出海字幕翻译任务 | [译制出海字幕翻译任务](./51-series-subtitle-translation.md) |

## 重要参数关系

| 参数或字段 | 常见含义 | 应查看 |
| --- | --- | --- |
| `videoUrl` / `urls` | 待处理视频、图片或素材 URL | 具体功能文档、[文件上传](./10-file-upload.md) |
| `idWorks` | 查询普通单视频任务状态时使用的作品 ID 列表 | [视频任务状态查询](./11-work-status-query.md) |
| `processStatus` | 视频处理状态 | [视频处理状态枚举](./91-video-process-status.md) |
| `videoInpaintMasks` | 擦除或 OCR 的画面区域框 | [字幕 mask 补充说明](./21-inpaint-masks-supplement.md) |
| `sourceLang` | 源语言 | [不同功能支持的语言列表](./90-language-support.md) |
| `videoInpaintLang` | 画面文字识别或擦除语言 | [不同功能支持的语言列表](./90-language-support.md) |
| `lang` | 目标语言 | [不同功能支持的语言列表](./90-language-support.md) |
| `wyVoiceParam` | 字幕压制、配音、字幕样式等复杂配置 | [视频语音翻译与重新配音](./31-video-voice-translation.md)、[字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md) |
| `font_param` | 新字幕的字体、描边、阴影和背景样式 | [字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md) |
| `id_ve_voice_character` | 经典模式下的配音音色角色 ID。`voice_type=TTS` 和 `voice_type=CLONE` 均使用该字段。 | [公共音色查询接口](./32-public-voice-characters.md) |
| `idSeries` | 译制出海剧集 ID | [译制出海项目与视频素材](./49-series-project-and-video-materials.md) |
| `idMaterialVideo` | 译制出海素材视频 ID | [译制出海项目与视频素材](./49-series-project-and-video-materials.md) |
| `idVeMaterialSrt` | 译制出海字幕素材 ID | [译制出海字幕素材管理](./50-series-subtitle-materials.md) |
| `items[]` | 译制出海批量任务中每个视频的任务元素 | [译制出海通用任务结构](./41-series-edit-common-task-structure.md) |
| `workDto` / `videoEditParamsDto` | 译制出海任务的作品参数和剪辑参数 | [译制出海通用任务结构](./41-series-edit-common-task-structure.md) |

## 组合场景

### 去掉旧字幕后压制新字幕

1. 如果视频是本地文件，先读[文件上传](./10-file-upload.md)。
2. 用[视频去字幕](./20-erase-video-subtitle.md)去掉旧字幕。
3. 如需手动指定区域或选择擦除版本，读[字幕 mask 补充说明](./21-inpaint-masks-supplement.md)。
4. 用[为视频压制字幕](./22-burn-subtitles.md)压制新的 SRT。
5. 如需控制字体样式，读[字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md)。

### 从视频中提取字幕

如果字幕已经显示在画面里，优先使用[OCR 提取视频字幕](./23-ocr-subtitle-extraction.md)。

如果字幕没有显示在画面里，但视频有清晰人声，使用[ASR 提取视频字幕](./24-asr-subtitle-extraction.md)。

OCR 依赖画面区域和文字语言；ASR 依赖音频语言。语种代码参考[不同功能支持的语言列表](./90-language-support.md)。

### 视频翻译并重新配音

1. 先读[视频语音翻译与重新配音](./31-video-voice-translation.md)。
2. 根据源语言和目标语言查[不同功能支持的语言列表](./90-language-support.md)。
3. 如果未指定音色，调用[公共音色查询接口](./32-public-voice-characters.md)获取 `id_ve_voice_character`。
4. 如果要压制译后字幕，使用[字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md)配置 `font_param`。
5. 创建任务后通过[视频任务状态查询](./11-work-status-query.md)查询处理结果；如失败，再按[视频处理状态枚举](./91-video-process-status.md)判断失败原因。

### 译制出海剧集批量任务

如果用户提到“译制出海”“剧集”“项目素材”“idSeries”或“idMaterialVideo”，优先读[译制出海剪辑 API 模块](./40-series-overview.md)。

译制出海任务使用独立流程：

1. 通过[译制出海项目与视频素材](./49-series-project-and-video-materials.md)创建或查询项目，拿到 `idSeries`。
2. 上传、导入或查询视频素材，拿到 `idMaterialVideo`，并确认 `downloadStatus=1`、`processStatus=1`。
3. 如需字幕素材，通过[译制出海字幕素材管理](./50-series-subtitle-materials.md)上传、创建或查询字幕，拿到 `idVeMaterialSrt`。
4. 如需先翻译字幕，使用[译制出海字幕翻译任务](./51-series-subtitle-translation.md)，必要时配合[译制出海翻译术语库](./52-series-translation-glossary.md)。
5. 根据目标选择字幕提取、字幕擦除、AI 配音、字幕压制或音频分离。
6. 按[译制出海通用任务结构](./41-series-edit-common-task-structure.md)组装 `items[]`。
7. 调用对应的 `gateway/ve/series/edit/task/...` 接口。
8. 通过[译制出海任务查询](./42-series-edit-task-list.md)轮询 `successWorkCount`、`errorWorkCount`、`processingWorkCount`。

## Agent 决策规则

- 用户不知道该调用哪个功能时，先读本文，再根据“快速选择功能”跳转。
- 用户给的是本地文件路径，而目标功能需要 URL 时，先调用[文件上传](./10-file-upload.md)。
- 创建普通单视频处理任务后，不要把 `code=1000` 当作最终成功；必须按[视频任务状态查询](./11-work-status-query.md)继续查询 `processStatus`。
- 涉及语言代码时，先查[不同功能支持的语言列表](./90-language-support.md)，不要凭常识猜测。
- 涉及擦除区域、OCR 区域或坐标时，读[字幕 mask 补充说明](./21-inpaint-masks-supplement.md)。
- 涉及新字幕外观时，读[字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md)。
- 涉及视频重新配音且没有音色 ID 时，先查[公共音色查询接口](./32-public-voice-characters.md)。
- 涉及译制出海、剧集、项目素材、批量视频任务、`idSeries` 或 `idMaterialVideo` 时，先查[译制出海剪辑 API 模块](./40-series-overview.md)。
- 本文只做路由和公共规则说明；具体请求体字段和完整代码示例以功能文档为准。
