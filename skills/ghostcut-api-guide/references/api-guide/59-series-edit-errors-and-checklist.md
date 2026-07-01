# 译制出海错误与检查清单

> 本文整理译制出海剪辑 API 的通用返回结构、常见失败示例和 Agent 提交任务前的检查清单。

## 通用返回结构

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `code` | `Integer` | 剪辑任务接口通常 `200` 表示请求成功；项目、素材、字幕和翻译管理接口通常 `1000` 表示成功。 |
| `msg` | `String` | 响应信息。 |
| `body` | `Object` | 业务返回内容。 |
| `count` | `Long` | 列表总数，列表接口返回。 |
| `trace` | `String` | 请求追踪号，排查问题时请一并提供。 |

成功返回示例：

```json
{
  "code": 200,
  "msg": "success",
  "body": {},
  "count": 0,
  "trace": "8d7f4f3b6a2f4b9a9e3c1d2f8a7b6c5d"
}
```

失败返回示例：

```json
{
  "code": 500,
  "msg": "参数错误或业务校验失败",
  "body": null,
  "count": 0,
  "trace": "8d7f4f3b6a2f4b9a9e3c1d2f8a7b6c5d"
}
```

## 常见失败示例

### 缺少必要参数

```json
{
  "code": 500,
  "msg": "参数错误：缺少必填字段 items",
  "body": null,
  "count": 0,
  "trace": "bfebb7a8e2a44f699091bb0d8a855701"
}
```

处理建议：

- 检查顶层是否存在 `items`。
- 检查 `items` 是否为非空数组。
- 检查每个 `items[]` 是否包含 `idMaterialVideo`、`workDto`、`videoEditParamsDto`。

### 配音参数不合法

```json
{
  "code": 500,
  "msg": "业务校验失败：角色音色与目标语种不匹配",
  "body": null,
  "count": 0,
  "trace": "7f9e38b912614ddba2f4d6bc0a2a4c8e"
}
```

处理建议：

- 检查 `lang` 是否为目标语种。
- 检查 `wyVoiceParam.character_voices[]` 中的音色是否支持该目标语种。
- 检查 `character` 和 `id_ve_character` 是否与 `customer_input.content[]` 对应。

### 复用作品结果不合法

```json
{
  "code": 500,
  "msg": "业务校验失败：materialWorkIds 对应作品不可用",
  "body": null,
  "count": 0,
  "trace": "997d2ce3a97e4a6ea7bdfd0b3a3c8c1e"
}
```

处理建议：

- 检查 `workDto.materialWorkIds` 是否为已有任务生成的可用作品 ID；应先通过 `task/list` 拿到对应任务 ID，再通过 `/work/status` 查询该任务下的作品详情，并从 `body.content[].id` 读取作品 ID。
- 确认对应任务已经成功，而不是仍在处理中或失败。
- 确认已有作品属于同一剧集；跨剧集复用不要自行假设可用。

## 提交前检查清单

### 通用检查

1. 是否已经有 `idSeries`。
2. 每个待处理视频是否已经有 `idMaterialVideo`。
3. 视频素材是否属于当前 `idSeries`。
4. 视频素材是否已查询确认 `downloadStatus=1`、`processStatus=1`。
5. 如果任务选择字幕素材输入方式，是否已经通过字幕列表确认 `idVeMaterialSrt`、`sourceLang` 和关联的 `idVeMaterialVideo`。
6. 顶层是否传入 `items[]`，且每个视频一个元素。
7. 每个 `items[]` 是否包含 `workDto` 和 `videoEditParamsDto`。
8. `videoEditParamsDto.type` 是否固定为 `WORK`。
9. 顶层 `sourceLang`、`lang` 是否符合任务语义。
10. 是否已为生产接入设置 `callback`；如设置，是否为可公网访问的回调地址，且已按[异步任务、轮询和回调机制](./15-async-and-callbacks.md)设计验签、重试和幂等处理。

### 字幕提取检查

- ASR 是否传 `needWanyin=1`、`wyTaskType=ONLY_ASR`。
- OCR 是否传 `needChineseOcclude=14` 和 `videoInpaintMasks`。
- OCR 的 `videoInpaintMasks[].type` 是否为 `trans_only_ocr`。

### 字幕擦除检查

- 基础去字是否传 `needChineseOcclude=1`。
- Lite/Pro 是否传 `needChineseOcclude=2` 和 `videoInpaintMasks`。
- Lite 是否使用 `model=advanced_lite`。
- Pro 是否使用 `model=advanced`。

### AI 配音检查

- 经典模式是否传 `wyTaskType=FULL`。
- 经典模式是否为需要配音的角色传了 `wyVoiceParam.character_voices[]`。
- 情感克隆模式是否传 `wyTaskType=VOICE_CLONE_PRO`。
- 情感克隆模式是否避免手动传 `wyVoiceParam.character_voices[]`。
- 情感克隆模式是否仍然提供了字幕输入；`/series/edit/task/dubbing` 不允许完全不传字幕。
- 是否没有把 `voice_type=CLONE` 误当成情感克隆模式；它只表示超真实音色。
- 如果基于已有字幕配音，`workDto.idVeMaterialSrt` 是否来自同一项目下的字幕素材。
- `workDto.idVeMaterialSrt` 和 `workDto.extraOptions.customer_input` 是否只传了一种；两者不能同时传。
- `customer_input.content[]` 与 `wyVoiceParam.character_voices[]` 的角色是否匹配。
- `wyNeedText=1` 时，`font_param.subtitleLang` 是否与目标语言一致。
- `wyNeedText=0` 时，是否确认本任务只重新配音、不压制新字幕。
- 是否传了 `removeBgAudio` 作为原音处理参数。
- 是否传了 `needWyEdit=0`。
- `overwriteLang` 是否与目标语言一致；如果 `wyNeedText=1`，还要与新字幕语言一致。
- 是否没有主动生成 `needChineseOcclude`、`videoInpaintMasks_lite`、`videoInpaintMasks_pro` 等去字幕字段；需要去字幕时应先单独创建字幕擦除任务。

### 字幕压制检查

- 是否传 `wyTaskType=NO_TTS`。
- 是否传 `wyNeedText=1`。
- 是否提供字幕文本和时间轴。
- 如果使用字幕素材，是否已确认 `idVeMaterialSrt` 可用。
- `workDto.idVeMaterialSrt` 和 `workDto.extraOptions.customer_input` 是否只传了一种；两者不能同时传。
- 基于去字后视频压制时，是否传 `workDto.materialWorkIds`，且取值是否来自 `/work/status` 的 `body.content[].id`。

### 音频分离检查

- 是否传 `wyTaskType=NO_TTS`。
- 是否传 `removeBgAudio=2`。
- 是否传 `wyNeedText=0`。
- 是否确认本任务处理结果是去 BGM 后的视频。

### 字幕翻译检查

- 是否已经有源字幕 ID 和 `sourceSubtitleData[]`。
- `taskList[].taskSubType` 是否为 `agent`。
- `translateOptions` 是否是 JSON 字符串，而不是对象。
- `projectVideoCount` 是否与 `subtitleList` 数量一致。
- `auto_translate_on=false` 时，是否准备好人工审核术语库并在 `stage=3` 后调用推进接口。

## 相关文档

- [译制出海剪辑 API 总览](./51-series-overview.md)：查看模块流程和任务选择规则。
- [通用任务结构](./52-series-edit-common-task-structure.md)：查看请求体结构。
- [任务查询](./53-series-edit-task-list.md)：提交后查询任务处理进度。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试、幂等和补偿轮询规则。
- [项目与视频素材](./60-series-project-and-video-materials.md)：检查 `idSeries`、`idMaterialVideo` 和素材准备状态。
- [字幕素材管理](./61-series-subtitle-materials.md)：检查 `idVeMaterialSrt` 和字幕内容。
- [字幕翻译任务](./62-series-subtitle-translation.md)：检查翻译任务和人工审核流程。

## Agent 决策规则

- 外层 `code=200` 表示请求成功，不表示任务内所有视频都已处理成功。
- 译制出海剪辑任务为异步处理；生产接入推荐通过 `callback` 接收结果，任务查询作为主动查询、补偿兜底和排查入口。
- 项目、素材、字幕和翻译管理接口通常以 `code=1000` 表示成功；剪辑任务接口通常以 `code=200` 表示请求成功。
- 外层 `code=500` 时，优先读取 `msg` 和 `trace`。
- 任何失败排查都应保留 `trace`，并同时记录 `idSeries`、任务接口、请求体摘要。
- 素材未准备完成、缺少 `items`、字幕 ID 不属于当前项目、音色语种不匹配、`materialWorkIds` 不可用是本模块最常见的失败原因。
- 如果用户要串联任务，先通过 `task/list` 确认前序任务已成功，再拿到对应任务的 `body[].id`，并继续调用 `/work/status` 查询该任务下的作品详情；填入 `materialWorkIds` 的作品 ID 来自 `/work/status` 的 `body.content[].id`。
