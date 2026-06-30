> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 译制出海任务查询

> 提交译制出海任务后，生产接入推荐优先通过 `callback` 接收最终结果；本接口用于查询任务列表、处理进度和补偿兜底。若需要进一步查询作品详情、作品 ID 或播放地址，应先从本接口拿到任务 ID，再调用 `/v-w-c/gateway/ve/work/status`。后续任务需要 `materialWorkIds` 时，使用 `/work/status` 返回的 `body.content[].id`。

## 接口信息

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/edit/task/list
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

接口路径：

```text
gateway/ve/series/edit/task/list
```

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idSeries` | `Long` | 否 | 剧集 ID。 |
| `ids` | `List<Long>` | 否 | 任务 ID 列表。 |
| `taskName` | `String` | 否 | 任务名称。 |
| `taskType` | `String` | 否 | 任务类型，枚举见下方 `taskType` 枚举。 |
| `taskTypeIn` | `List<String>` | 否 | 多任务类型过滤；数组，支持一次查询多个 `taskType`。 |
| `sourceLanguage` | `String` | 否 | 原语种。注意查询字段名不是 `sourceLang`。 |
| `targetLanguage` | `String` | 否 | 目标语种。注意查询字段名不是 `lang`。 |
| `pageNumber` | `Integer` | 否 | 页码，从 `1` 开始。 |
| `pageSize` | `Integer` | 否 | 每页条数。 |
| `returnAll` | `Boolean` | 否 | 是否返回全部。 |
| `deleted` | `Byte` | 否 | 删除状态，常用 `0` 查询未删除任务。 |

## 请求示例

```json
{
  "idSeries": 10001,
  "sourceLanguage": "zh",
  "targetLanguage": "en",
  "pageNumber": 1,
  "pageSize": 20,
  "deleted": 0
}
```

## `taskType` 枚举

| 值 | 含义 |
| --- | --- |
| `SERIES_CLIP1` | 译制出海 + 提取字幕。 |
| `SERIES_CLIP2` | 译制出海 + 字幕擦除。 |
| `SERIES_CLIP3` | 译制出海 + 翻译配音。 |
| `SERIES_CLIP4` | 译制出海 + 解说短剧。 |
| `SERIES_CLIP5` | 译制出海 + 字幕压制。 |
| `SERIES_CLIP6` | 译制出海 + 音乐分离。 |
| `SERIES_CLIP10` | 译制出海 + 上传字幕。 |
| `SERIES_CLIP55` | 译制出海 + 字幕翻译。 |
| `SERIES_CLIP66` | 译制出海 + 长视频合成。 |
| `SERIES_CLIP77` | 译制出海 + 智能识别角色。 |
| `SERIES_CLIP80` | 译制出海 + 一键译配主任务。 |
| `SERIES_CLIP88` | 译制出海 + 一键译配。 |

如果只查单个任务类型，传 `taskType`。如果要同时查询多个任务类型，传 `taskTypeIn` 数组，例如：

```json
{
  "idSeries": 10001,
  "taskTypeIn": ["SERIES_CLIP1", "SERIES_CLIP2", "SERIES_CLIP5"],
  "pageNumber": 1,
  "pageSize": 20,
  "deleted": 0
}
```

## 返回结构

通用返回结构：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `code` | `Integer` | 响应码，`200` 表示请求成功。 |
| `msg` | `String` | 响应信息。 |
| `body` | `Array` | 任务列表；每个元素是一个任务对象。 |
| `count` | `Long` | 列表总数。 |
| `trace` | `String` | 请求追踪号，排查问题时请一并提供。 |

响应结构示例：

```json
{
  "body": [
    {
      "id": 243753894,
      "idSeries": 249305,
      "projectName": "auto_519733024_dub_ms",
      "taskType": "SERIES_CLIP3",
      "sourceLang": "zh",
      "lang": "ms",
      "successWorkCount": 1,
      "errorWorkCount": 0,
      "processingWorkCount": 0,
      "videoCount": 1
    },
    {
      "id": 243753893,
      "idSeries": 249305,
      "projectName": "auto_519733024_translate_ms",
      "taskType": "SERIES_CLIP55",
      "sourceLang": "zh",
      "lang": "ms",
      "successWorkCount": 0,
      "errorWorkCount": 0,
      "processingWorkCount": 0,
      "videoCount": 1
    }
  ],
  "code": 1000,
  "count": 2,
  "msg": "success",
  "trace": "63c3ec35988d4a1ea5c954147dc94f1b"
}
```

`body` 中常见任务字段：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `Long` | 任务 ID，也可理解为 project id。需要继续查询作品详情、作品 ID 或播放地址时，使用该字段再调用 `/v-w-c/gateway/ve/work/status`，并以该接口返回结果为准。 |
| `batchNo` | `String` | 批次号，同一批自动任务通常相同。 |
| `idSeries` | `Long` | 剧集 ID。 |
| `projectName` | `String` | 任务名称。 |
| `taskType` | `String` | 任务类型。 |
| `sourceLang` | `String` | 原语种。 |
| `lang` | `String` | 目标语种。 |
| `successWorkCount` | `Integer` | 成功的视频数量。 |
| `errorWorkCount` | `Integer` | 失败的视频数量。 |
| `processingWorkCount` | `Integer` | 处理中的视频数量。 |
| `videoCount` | `Integer` | 任务内视频数量。 |

关键路径：

| 路径 | 含义 |
| --- | --- |
| `body[]` | 任务列表。 |
| `body[].id` | 任务 ID。 |
| `/work/status` 的 `body.content[].id` | 作品 ID。需要串联后续任务时，填入 `workDto.materialWorkIds`。 |

如果需要查询作品详情、作品 ID、播放地址或任务结果，先从 `task/list` 读取 `body[].id`，再按[视频任务状态查询](./11-work-status-query.md)的方式调用 `/v-w-c/gateway/ve/work/status`，并以返回的作品详情为准。作品 ID 的精确路径是 `/work/status` 响应中的 `body.content[].id`；单视频结果通常读取 `body.content[0].id`。

## 状态判断

| 判断 | 含义 | 建议 |
| --- | --- | --- |
| `processingWorkCount > 0` | 仍有视频处理中 | 等待 `callback`，或继续轮询 `task/list`；补偿轮询的初始间隔建议 300 秒。 |
| `errorWorkCount > 0` | 有视频失败 | 记录 `trace` 和任务信息，结合 [错误与检查清单](./59-series-edit-errors-and-checklist.md) 排查。 |
| `successWorkCount > 0` 且 `processingWorkCount == 0` 且 `errorWorkCount == 0` | 当前任务内视频均成功 | 进入后续任务或读取结果。 |

## 结果定位

`task/list` 可用于判断任务级进度，也可提供后续查询所需的任务 ID。不要只凭计数字段推断具体作品 ID；应先读取 `body[].id`，再通过 `/work/status` 查作品详情，并以该接口实际返回结果为准。

| 任务类型 | 结果定位方式 |
| --- | --- |
| 字幕提取 | 成功后通过 [字幕素材管理](./61-series-subtitle-materials.md) 查询 `subtitleFrom=2` ASR 或 `subtitleFrom=3` OCR 的字幕素材。 |
| 字幕翻译 | 通过 [字幕翻译任务](./62-series-subtitle-translation.md) 查询翻译任务，再通过字幕列表查询 `subtitleFrom=4` 的译后字幕。 |
| 字幕擦除 | 需要后续复用或查看结果时，先通过 `task/list` 查询前序任务结果，找到对应的最新字幕擦除任务，拿到 `body[].id`。再按[视频任务状态查询](./11-work-status-query.md)调用 `/work/status` 查询该任务下的作品详情，从 `body.content[].id` 读取作品 ID。 |
| AI 配音 / 字幕压制 / 音频分离 | 先用 `task/list` 判断完成，再从任务对象读取 `body[].id`；如果要查看作品 ID、播放地址或作品详情，再按[视频任务状态查询](./11-work-status-query.md)调用 `/work/status`，从 `body.content[].id` 读取作品 ID。 |

如果响应中没有可用于后续查询的任务 ID，应保留任务 ID、`idSeries`、`trace` 和请求摘要，不要凭命名规则拼接 ID。

## 查询策略

- 已知任务 ID 时，优先传 `ids` 精确查询。
- 生产接入推荐通过 `callback` 接收最终结果；本接口适合作为主动查询、后台补偿扫描和问题排查入口。
- 只知道剧集时，传 `idSeries`、`deleted=0` 和分页参数。
- 按语言过滤时，查询接口使用 `sourceLanguage`、`targetLanguage`，不要写成提交任务时的 `sourceLang`、`lang`。
- 按任务类型过滤时，使用本文 `taskType` 枚举；单类型用 `taskType`，多类型用 `taskTypeIn`。

## 相关文档

- [译制出海剪辑 API 总览](./51-series-overview.md)：查看整体调用流程。
- [通用任务结构](./52-series-edit-common-task-structure.md)：查看提交任务的请求结构。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试、幂等和补偿轮询规则。
- [字幕素材管理](./61-series-subtitle-materials.md)：字幕提取和翻译完成后查询字幕素材。
- [字幕翻译任务](./62-series-subtitle-translation.md)：查询、推进或重试字幕翻译任务。
- [错误与检查清单](./59-series-edit-errors-and-checklist.md)：查看失败排查建议。

## Agent 决策规则

- 提交译制出海任务后，生产接入优先通过 `callback` 接收结果；本接口用于主动查询、补偿兜底和问题排查。如果还需要作品详情、作品 ID 或播放地址，再继续调用 `/work/status`。
- 外层 `code=200` 只是查询请求成功，还要继续看任务里的 `successWorkCount`、`errorWorkCount`、`processingWorkCount`。
- 如果用户问“任务是否完成”，优先按任务计数字段判断。
- 如果用户问“字幕结果在哪里”，优先查字幕素材列表；如果用户问“视频结果在哪里”，先读取 `task/list` 返回的 `body[].id`，再按[视频任务状态查询](./11-work-status-query.md)查询作品详情。
- `task/list` 的 `body[].id` 是任务 ID，不是作品 ID；作品 ID 或播放地址需要通过 `/work/status` 继续查询。
- 需要把已有视频结果传给后续任务时，取 `/work/status` 返回的 `body.content[].id`，填入后续 `workDto.materialWorkIds`。
- 按多个任务类型查询时，使用 `taskTypeIn` 数组，不要把多个枚举拼成一个字符串。
- 如果失败，回答时带上 `trace`、`idSeries`、任务 ID、任务名称和语言方向，便于排查。
