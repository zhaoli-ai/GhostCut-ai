> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# GhostCut API 总览

> 本文是 GhostCut API 文档的入口页，用于帮助人或 Agent 判断应该调用哪个功能、先阅读哪个文档，以及哪些公共规则需要在所有功能中复用。具体参数、请求示例和响应字段以各功能文档为准。

首次接入或刚安装 skill 的用户，建议先读[5 分钟快速上手](./01-quickstart.md)，用最小示例跑通凭证、签名、创建视频去文字任务和查询结果。

## 文档编号

| 编号 | 范围 |
| --- | --- |
| `00-20` | 通用基础能力。 |
| `21-50` | 视频 AI 处理能力。 |
| `51-80` | 译制出海模块。 |
| `81-90` | 图片 AI 处理能力。 |
| `91-98` | 参考附录。 |
| `99` | 维护资料。 |

## 快速选择功能

| 用户目标 | 优先阅读 | 常用关联文档 |
| --- | --- | --- |
| 本地视频、本地 SRT 或本地图片需要先传给 GhostCut | [文件上传](./10-file-upload.md) | 后续再进入具体功能文档 |
| 查询普通单视频任务是否完成、读取结果 URL | [视频任务状态查询](./11-work-status-query.md) | [视频处理状态枚举](./14-video-process-status.md) |
| 了解异步任务、轮询策略、callback 回调、回调验签、重试和幂等 | [异步任务、轮询和回调机制](./15-async-and-callbacks.md) | [视频任务状态查询](./11-work-status-query.md)、[AI 图片处理](./81-image-processing.md) |
| 基础剪辑、截取视频片段、调整分辨率、调色锐化、滤镜、镜像、缩放或画面移动 | [视频基础处理](./27-video-basic-processing.md) | [文件上传](./10-file-upload.md)、[视频任务状态查询](./11-work-status-query.md) |
| 去掉视频中的字幕、文字、角标、logo 或固定区域 | [视频去字幕](./21-erase-video-subtitle.md) | [字幕 mask 补充说明](./22-inpaint-masks-supplement.md)、[视频任务状态查询](./11-work-status-query.md) |
| 解释擦除模型版本差异、手动画框坐标、`videoInpaintMasks` | [字幕 mask 补充说明](./22-inpaint-masks-supplement.md) | [视频去字幕](./21-erase-video-subtitle.md) |
| 把已有 SRT 字幕硬压制到视频画面里 | [为视频压制字幕](./23-burn-subtitles.md) | [字幕样式和字体配置补充](./26-subtitle-style-and-fonts.md)、[文件上传](./10-file-upload.md) |
| 从画面硬字幕中识别并导出 SRT | [OCR 提取视频字幕](./24-ocr-subtitle-extraction.md) | [字幕 mask 补充说明](./22-inpaint-masks-supplement.md)、[语言列表](./13-language-support.md) |
| 从视频音频的人声中识别并导出 SRT | [ASR 提取视频字幕](./25-asr-subtitle-extraction.md) | [语言列表](./13-language-support.md) |
| 配置字幕字体、描边、阴影、背景、样式模板 | [字幕样式和字体配置补充](./26-subtitle-style-and-fonts.md) | [为视频压制字幕](./23-burn-subtitles.md)、[视频语音翻译与重新配音](./31-video-voice-translation.md) |
| 去掉或分离视频背景音乐，保留人声和环境声 | [背景音乐去除/分离](./30-background-music-separation.md) | [文件上传](./10-file-upload.md)、[视频任务状态查询](./11-work-status-query.md) |
| 翻译视频并生成新配音，或重新配音 | [视频语音翻译与重新配音](./31-video-voice-translation.md) | [公共音色查询接口](./32-public-voice-characters.md)、[字幕样式和字体配置补充](./26-subtitle-style-and-fonts.md)、[语言列表](./13-language-support.md) |
| 为视频配音功能选择公共音色 | [公共音色查询接口](./32-public-voice-characters.md) | [视频语音翻译与重新配音](./31-video-voice-translation.md) |
| 擦除图片文字、翻译图片并回填到图中、调整图片翻译结果 | [AI 图片处理](./81-image-processing.md) | [文件上传](./10-file-upload.md)、[语言列表](./13-language-support.md) |
| 处理译制出海剧集、项目素材或批量视频任务 | [译制出海剪辑 API 模块](./51-series-overview.md) | [译制出海项目与视频素材](./60-series-project-and-video-materials.md)、[译制出海字幕素材管理](./61-series-subtitle-materials.md)、[译制出海通用任务结构](./52-series-edit-common-task-structure.md) |
| 翻译译制出海字幕、维护术语库或审核翻译 | [译制出海字幕翻译任务](./62-series-subtitle-translation.md) | [译制出海翻译术语库](./63-series-translation-glossary.md)、[译制出海字幕素材管理](./61-series-subtitle-materials.md) |
| 查询不同功能支持哪些语种 | [不同功能支持的语言列表](./13-language-support.md) | 需要语种参数的具体功能文档 |
| 判断 `processStatus` 状态值、失败原因是什么 | [视频处理状态枚举](./14-video-process-status.md) | [视频任务状态查询](./11-work-status-query.md) |
| 维护本文档项目的写作规则和 Cursor 配置 | [Cursor 配置](./99-cursor.md) | [完整文档索引](./llms.txt) |

## 公共基础文档

| 目标 | 优先阅读 |
| --- | --- |
| 新用户先跑通一个最小示例 | [5 分钟快速上手](./01-quickstart.md) |
| 获取 `AppKey`、`AppSecret`、生成 `AppSign` | [API 凭证与签名](./02-auth-and-sign.md) |
| 确认视频、图片、SRT 的 URL 与格式要求 | [素材 URL 与格式要求](./03-media-requirements.md) |
| 上传本地视频、图片或 SRT | [文件上传](./10-file-upload.md) |
| 查询普通视频处理任务结果 | [视频任务状态查询](./11-work-status-query.md) |
| 理解异步任务、callback、轮询和回调验签 | [异步任务、轮询和回调机制](./15-async-and-callbacks.md) |

## 主要调用流程

普通视频处理能力通常使用 `/v-w-c/gateway/ve/work/free` 创建任务，并用 `/v-w-c/gateway/ve/work/status` 查询结果：

1. 按[素材 URL 与格式要求](./03-media-requirements.md)准备视频 URL；本地文件先读[文件上传](./10-file-upload.md)。
2. 按[API 凭证与签名](./02-auth-and-sign.md)准备 `AppKey`、`AppSecret` 和 `AppSign`。
3. 根据具体功能文档组装请求体并创建任务。
4. 创建成功后通常从 `body.dataList[0].id` 获取作品 ID。
5. 生产环境推荐创建任务时传入 `callback`；轮询作为主动查询和补偿兜底，规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。
6. 需要主动查询时，按[视频任务状态查询](./11-work-status-query.md)读取 `processStatus` 和结果 URL；失败排查见[视频处理状态枚举](./14-video-process-status.md)。

图片处理使用 `/image/translate/query` 查询 `status` 和 `result`，不要套用普通视频的 `/work/status` 流程。译制出海模块使用 `idSeries`、`items[]` 和 `task/list`，入口见[译制出海剪辑 API 模块](./51-series-overview.md)。

## 常见接口路径

| 接口 | 用途 | 相关文档 |
| --- | --- | --- |
| `POST /v-w-c/gateway/ve/work/free` | 创建视频处理任务，如擦除、字幕压制、OCR/ASR、背景音乐分离、视频语音翻译 | 各功能文档 |
| `POST /v-w-c/gateway/ve/work/status` | 查询普通单视频处理任务状态和结果 URL | [视频任务状态查询](./11-work-status-query.md) |
| `POST /v-w-c/gateway/ve/file/upload/policy/apply` | 获取本地文件上传凭证 | [文件上传](./10-file-upload.md) |
| `POST /v-w-c/gateway/ve/image/translate` | 创建图片文字擦除或图片翻译任务 | [AI 图片处理](./81-image-processing.md) |
| `POST /v-w-c/gateway/ve/image/translate/query` | 查询图片处理任务状态和结果 URL | [AI 图片处理](./81-image-processing.md) |
| `POST /v-w-c/gateway/ve/image/translate/auth/apply` | 为图片翻译结果生成官方 Web 精修编辑器授权码 | [AI 图片处理](./81-image-processing.md) |
| `POST /v-w-c/gateway/ve/image/translate/redo` | 提交修改后的图片翻译 `result` 并重新合成 | [AI 图片处理](./81-image-processing.md) |
| `POST /v-w-c/enum/query2` | 查询枚举，如 `ProcessStatus`、语言列表等 | [视频处理状态枚举](./14-video-process-status.md) |
| `POST /v-w-c/gateway/ve/voicecharacter/aggregate/list` | 查询公共音色角色、语言试听和标签 | [公共音色查询接口](./32-public-voice-characters.md) |
| `POST /v-w-c/gateway/ve/series/create` | 创建译制出海项目并获得 `idSeries` | [译制出海项目与视频素材](./60-series-project-and-video-materials.md) |
| `POST /v-w-c/gateway/ve/series/video/import` | 将视频 URL 导入译制出海项目并获得 `idMaterialVideo` | [译制出海项目与视频素材](./60-series-project-and-video-materials.md) |
| `POST /v-w-c/gateway/ve/series/srt/list` | 查询译制出海字幕素材并获得 `idVeMaterialSrt` | [译制出海字幕素材管理](./61-series-subtitle-materials.md) |
| `POST /v-w-c/gateway/ve/series/edit/task/...` | 创建译制出海剧集/项目级批量任务 | [译制出海剪辑 API 模块](./51-series-overview.md) |
| `POST /v-w-c/gateway/ve/series/edit/task/list` | 查询译制出海任务列表和处理进度 | [译制出海任务查询](./53-series-edit-task-list.md) |
| `POST /v-w-c/gateway/ve/translate/subtitle` | 创建译制出海字幕翻译任务 | [译制出海字幕翻译任务](./62-series-subtitle-translation.md) |

## 重要参数关系

| 参数或字段 | 常见含义 | 应查看 |
| --- | --- | --- |
| `videoUrl` / `urls` | 待处理视频、图片或素材 URL | 具体功能文档、[文件上传](./10-file-upload.md) |
| `downloadInfo` | 图片处理任务中的图片 URL JSON 字符串 | [AI 图片处理](./81-image-processing.md)、[文件上传](./10-file-upload.md) |
| `idWorks` | 查询普通单视频任务状态时使用的作品 ID 列表 | [视频任务状态查询](./11-work-status-query.md) |
| `processStatus` | 视频处理状态 | [视频处理状态枚举](./14-video-process-status.md) |
| `status` | 图片处理状态 | [AI 图片处理](./81-image-processing.md) |
| `callback` | 异步任务完成后的回调 URL | [异步任务、轮询和回调机制](./15-async-and-callbacks.md) |
| `Callback-Sign` | GhostCut 回调请求头中的验签值 | [异步任务、轮询和回调机制](./15-async-and-callbacks.md) |
| `resolution` | 普通视频处理任务的输出分辨率 | [视频基础处理](./27-video-basic-processing.md) |
| `needTrim` / `needMask` / `needMirror` / `needRescale` / `needShift` | 视频基础处理、特效、镜像、缩放和画面移动参数 | [视频基础处理](./27-video-basic-processing.md) |
| `extraOptions.range` / `write_options.crf` / `extra_trim_config` | 截取时间段、画质压缩率和智能基础优化微调配置 | [视频基础处理](./27-video-basic-processing.md) |
| `videoInpaintMasks` | 擦除或 OCR 的画面区域框 | [字幕 mask 补充说明](./22-inpaint-masks-supplement.md) |
| `sourceLang` | 源语言 | [不同功能支持的语言列表](./13-language-support.md) |
| `videoInpaintLang` | 画面文字识别或擦除语言 | [不同功能支持的语言列表](./13-language-support.md) |
| `lang` | 目标语言 | [不同功能支持的语言列表](./13-language-support.md) |
| `wyVoiceParam` | 字幕压制、配音、字幕样式等复杂配置 | [视频语音翻译与重新配音](./31-video-voice-translation.md)、[字幕样式和字体配置补充](./26-subtitle-style-and-fonts.md) |
| `font_param` | 新字幕的字体、描边、阴影和背景样式 | [字幕样式和字体配置补充](./26-subtitle-style-and-fonts.md) |
| `id_ve_voice_character` | 经典模式下的配音音色角色 ID。`voice_type=TTS` 和 `voice_type=CLONE` 均使用该字段。 | [公共音色查询接口](./32-public-voice-characters.md) |
| `idSeries` | 译制出海剧集 ID | [译制出海项目与视频素材](./60-series-project-and-video-materials.md) |
| `idMaterialVideo` | 译制出海素材视频 ID | [译制出海项目与视频素材](./60-series-project-and-video-materials.md) |
| `idVeMaterialSrt` | 译制出海字幕素材 ID | [译制出海字幕素材管理](./61-series-subtitle-materials.md) |
| `items[]` | 译制出海批量任务中每个视频的任务元素 | [译制出海通用任务结构](./52-series-edit-common-task-structure.md) |
| `workDto` / `videoEditParamsDto` | 译制出海任务的作品参数和剪辑参数 | [译制出海通用任务结构](./52-series-edit-common-task-structure.md) |

## Agent 决策规则

- 用户不知道该调用哪个功能时，先读本文，再根据“快速选择功能”跳转。
- 用户给的是本地文件路径，而目标功能需要 URL 时，先调用[文件上传](./10-file-upload.md)。
- 创建普通视频处理任务前，先按[素材 URL 与格式要求](./03-media-requirements.md)检查视频格式、URL 字符和批量数量约束。
- 用户问 API Key、`AppKey`、`AppSecret`、凭证在哪里获取或如何鉴权时，先读[API 凭证与签名](./02-auth-and-sign.md)。
- 用户提到异步任务、轮询策略、callback 回调、`Callback-Sign`、回调重试或幂等时，先查[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。生产接入优先推荐 `callback`，轮询作为查询和补偿兜底，初始轮询间隔建议 300 秒。
- 创建普通单视频处理任务后，不要把 `code=1000` 当作最终成功；必须按[视频任务状态查询](./11-work-status-query.md)继续查询 `processStatus`。
- 涉及基础剪辑、分辨率、截取、调色、锐化、片头片尾裁剪、加速、滤镜、镜像、缩放或画面移动时，先查[视频基础处理](./27-video-basic-processing.md)。
- 涉及语言代码时，先查[不同功能支持的语言列表](./13-language-support.md)，不要凭常识猜测。
- 涉及擦除区域、OCR 区域或坐标时，读[字幕 mask 补充说明](./22-inpaint-masks-supplement.md)。
- 涉及新字幕外观时，读[字幕样式和字体配置补充](./26-subtitle-style-and-fonts.md)。
- 涉及视频重新配音且没有音色 ID 时，先查[公共音色查询接口](./32-public-voice-characters.md)。
- 涉及图片文字擦除、图片翻译、Image Redo 或图片翻译精修时，先查[AI 图片处理](./81-image-processing.md)。
- 涉及译制出海、剧集、项目素材、批量视频任务、`idSeries` 或 `idMaterialVideo` 时，先查[译制出海剪辑 API 模块](./51-series-overview.md)。
- 本文只做路由和公共规则说明；具体请求体字段和完整代码示例以功能文档为准。
