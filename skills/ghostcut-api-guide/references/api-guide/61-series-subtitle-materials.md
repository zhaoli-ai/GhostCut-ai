> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 译制出海字幕素材管理

> 本文补充译制出海中的字幕素材生命周期：上传本地 SRT、用 SRT/VTT 内容创建字幕、查询字幕列表、解析 `slInfo`、更新、删除和复制字幕。字幕素材通常用于 AI 配音、字幕压制和字幕翻译。

## 字幕素材 ID 的命名

译制出海文档里会出现两个相近名称：

| 名称 | 常见来源 | 用法 |
| --- | --- | --- |
| `idMaterialSrt` | [文件上传](./10-file-upload.md) 的 `srt_series` 上传凭证响应。 | 上传接口返回的字幕素材 ID。 |
| `idVeMaterialSrt` | 字幕列表 `body[].id`、部分任务的 `workDto.idVeMaterialSrt`。 | 剪辑任务中引用字幕素材时常用的字段名。 |

`idMaterialSrt` 和 `idVeMaterialSrt` 完全等价，都是字幕素材 ID。为了拿到字幕所属项目、关联视频、语种和 `subtitleFrom` 等上下文，后续任务引用字幕前仍建议调用 `series/srt/list` 查询，并以返回对象的 `id` 填入 `workDto.idVeMaterialSrt`。

## 本地 SRT 上传到项目

本地 SRT 应使用 [文件上传](./10-file-upload.md) 的译制出海字幕上传流程：

```json
{
  "nonce": "random-string",
  "idSeries": 124756,
  "idMaterialVideo": 700435746,
  "materialFileType": "srt_series",
  "materialName": "第一集英文字幕",
  "fileName": "episode_001_en.srt",
  "sourceLang": "en"
}
```

关键规则：

- 上传字幕前必须先有 `idSeries` 和 `idMaterialVideo`。
- 字幕会关联到指定视频素材。
- 上传凭证响应中的 `body.idMaterialSrt` 是字幕素材 ID。
- 后续任务需要 `idVeMaterialSrt` 时，优先再查一次字幕列表确认。

## 用 SRT 或 VTT 内容创建字幕

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/srt/create
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idSeries` | `Long` | 是 | 项目 ID。 |
| `fileName` | `String` | 是 | 字幕文件名。 |
| `materialName` | `String` | 是 | 字幕素材名称。 |
| `idVeMaterialVideo` | `Long` | 是 | 关联的视频素材 ID。 |
| `characterStatus` | `Byte` | 否 | 是否已同步角色，`0` 否，`1` 是；默认 `0`。 |
| `proofreadStatus` | `Byte` | 否 | 是否已校对，`0` 否，`1` 是；默认 `0`。 |
| `sourceLang` | `String` | 否 | 字幕语种 code。 |
| `slInfo` | `String` | 是 | SRT 或 VTT 内容。 |

请求示例：

```json
{
  "idSeries": 203468,
  "idVeMaterialVideo": 705050848,
  "fileName": "episode_001_zh.srt",
  "materialName": "第一集中文字幕",
  "proofreadStatus": 1,
  "characterStatus": 0,
  "sourceLang": "zh",
  "slInfo": "1\n00:00:13,000 --> 00:00:15,020\n告诉我，我是谁？\n\n2\n00:00:15,960 --> 00:00:17,060\n你是\n"
}
```

响应 `body.id` 是新字幕素材 ID，可作为 `idVeMaterialSrt` 使用。

## 查询字幕列表

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/srt/list
```

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `ids` | `List<Long>` | 否 | 字幕 ID 列表。非必填；已知 ID 时建议传，可用于精确查询。 |
| `idSeries` | `Long` | 是 | 项目 ID。 |
| `deleted` | `Byte` | 否 | 是否删除，`0` 否，`1` 是，默认 `0`。 |
| `idVeMaterialVideo` | `Long` | 否 | 关联的视频素材 ID。 |
| `subtitleFrom` | `Byte` | 否 | 字幕来源：`1` 上传，`2` ASR 提取，`3` OCR 提取，`4` 翻译。 |
| `sourceLang` | `String` | 否 | 字幕语种 code。 |
| `page` | `Integer` | 否 | 页码，从 `0` 开始。 |
| `pageSize` | `Integer` | 否 | 每页数量，最大 `2000`。 |

请求示例：

```json
{
  "idSeries": 203468,
  "idVeMaterialVideo": 705050848,
  "sourceLang": "zh",
  "deleted": 0,
  "page": 0,
  "pageSize": 20
}
```

关键响应字段：

| 字段 | 说明 |
| --- | --- |
| `id` | 字幕素材 ID，即常用的 `idVeMaterialSrt`。 |
| `idSeries` | 所属项目 ID。 |
| `idVeMaterialVideo` | 关联的视频素材 ID。 |
| `ossUrl` | 原始字幕文件 URL；未编辑时可直接使用。 |
| `materialName` | 字幕素材名。 |
| `fileName` | 字幕文件名。 |
| `sourceLang` | 字幕语种 code。 |
| `subtitleFrom` | 字幕来源：上传、ASR、OCR 或翻译。 |
| `proofreadStatus` | 是否已校对。 |
| `slInfo` | 字幕最新编辑信息。通常是 JSON 字符串：编辑后包含 `sl[]`，文件化编辑历史场景可能是 OSS JSON 指针。 |

## 如何从 `slInfo` 得到字幕内容

字幕列表中的最新编辑版本不一定是一个实际 `.srt` 文件。接口返回中的 `slInfo` 是字幕编辑态的 JSON 字符串；`series/srt/create` 请求里可以传 SRT/VTT 文本，但 `series/srt/list` 返回的 `slInfo` 不应按普通 SRT/VTT 文本优先解析。

Agent 应按以下顺序处理：

1. 如果没有 `slInfo`，或 `slInfo` 不是有效 JSON，使用 `ossUrl` 作为原始字幕文件 URL。
2. 如果 `slInfo` 是 JSON，且包含 `sl[]`，说明用户在网站编辑过字幕，直接用 `sl[]` 组装 SRT。
3. 如果 `slInfo` 是 JSON，且没有 `sl[]`，但包含 `{"storage_type":"OSS"}`，说明字幕编辑态以文件形式存放，并支持编辑版本历史。用 `url_prefix + json_name` 拉取最新 JSON，再回到第 2 步解析其中的 `sl[]`。
4. 如果 `slInfo` 是 JSON，但既没有 `sl[]`，也不是 `storage_type=OSS` 指针，退回使用 `ossUrl`。

OSS 指针示例：

```json
{
  "storage_type": "OSS",
  "json_name": "sbduifhaosdjo2.json",
  "history": ["a.json", "b.json"],
  "url_prefix": "https://gc100.cdn.izhaoli.cn/srt_json/qweqedasdg/123456/"
}
```

最新编辑态 JSON 的访问地址为 `url_prefix + json_name`，例如：

```text
https://gc100.cdn.izhaoli.cn/srt_json/qweqedasdg/123456/sbduifhaosdjo2.json
```

`slInfo` 中常见的顶层字段：

| 字段 | 说明 |
| --- | --- |
| `rawResult` | 原始字幕识别或翻译结果的 JSON 字符串。有些字幕可能没有。 |
| `sl` | GhostCut 网站编辑处理后的字幕数组，是还原 SRT 时的主要数据源。 |
| `ttsMetaResult` | 配音相关元信息的 JSON 字符串。只还原字幕文件时通常不需要使用。 |

`sl[]` 中常用字段：

| 字段 | 说明 |
| --- | --- |
| `_start` | 字幕开始时间，单位秒。还原 SRT 时优先使用。 |
| `_end` | 字幕结束时间，单位秒。还原 SRT 时优先使用。 |
| `starting_time` / `_starting_time` | 开始时间辅助字段，单位秒。 |
| `duration` | 字幕时长，单位秒；没有 `_end` 时可用 `starting_time + duration`。 |
| `src` | 字幕原文文本。还原 SRT 正文时优先使用。 |
| `text` | 字幕台词文本，通常与 `src` 一致，可用于展示或兜底。 |
| `sourcetext` | 原字幕文本。 |
| `character` | 角色名。 |
| `id_ve_character` | 角色 ID。 |
| `id_ve_character_sentence` | 角色句子关联 ID。 |
| `inferedCharacterInfo` | 角色智能识别置信度等信息。 |
| `position` | 字幕渲染位置。 |
| `_color` / `_display` / `_focus` / `_mask_top` / `_left` / `_width` | 网站前端编辑和渲染字段。还原 SRT 时忽略。 |

组装 SRT 时，优先使用以下字段：

| SRT 字段 | 取值规则 |
| --- | --- |
| 开始时间 | `_start`，没有则取 `starting_time` 或 `_starting_time`。 |
| 结束时间 | `_end`，没有则取 `starting_time + duration`。 |
| 文本 | `src`，没有则取 `text`。 |

时间字段单位是秒，输出 SRT 时转成 `HH:MM:SS,mmm`。例如 `2.63` 应输出为 `00:00:02,630`。

一个最小化的 `slInfo` 示例：

```json
{
  "rawResult": "{\"sentences\":[{\"start\":2.63,\"end\":4.25,\"source\":\"Vamos dividi-los em pares\",\"translation\":\"Vamos dividi-los em pares\",\"character\":\"\"}]}",
  "sl": [
    {
      "__processed": true,
      "__src": "Vamos dividi-los em pares",
      "__text": "Vamos dividi-los em pares",
      "_color": "#6b321e",
      "_display": "none",
      "_end": 4.25,
      "_focus": false,
      "_left": 44.957264957264954,
      "_mask_top": 648.0269999999999,
      "_origin": true,
      "_start": 2.63,
      "_width": 27.692307692307697,
      "character": "",
      "duration": 1.63,
      "gender": "",
      "is_modified": false,
      "position": 0.7192308546059932,
      "src": "Vamos dividi-los em pares",
      "starting_time": 2.627,
      "text": "Vamos dividi-los em pares"
    }
  ]
}
```

对应 SRT：

```srt
1
00:00:02,630 --> 00:00:04,250
Vamos dividi-los em pares
```

不要把 `_color`、`_display`、`_focus`、`_mask_top` 等前端编辑字段当成字幕文本。

## 更新字幕

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/srt/update
```

可更新字段包括 `materialName`、`sourceLang`、`deleted`、`proofreadStatus`、`slInfo`。请求需要带 `id` 和 `idSeries`：

```json
{
  "id": 2927192,
  "idSeries": 102485,
  "materialName": "第一集英文字幕-已校对",
  "sourceLang": "en",
  "deleted": 0,
  "proofreadStatus": 1,
  "slInfo": "{\"sl\":[{\"_start\":13,\"_end\":15.02,\"starting_time\":13,\"duration\":2.02,\"src\":\"Tell me, who am I?\",\"text\":\"Tell me, who am I?\"}]}"
}
```

成功时 `body=1`。

## 删除字幕

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/srt/delete
```

请求示例：

```json
{
  "ids": [2927192]
}
```

成功时 `body` 是删除条数。

## 复制字幕

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/srt/copy
```

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idSeries` | `Long` | 是 | 项目 ID。 |
| `ids` | `List<Long>` | 是 | 要复制的字幕 ID 列表。 |
| `sourceLang` | `String` | 否 | 复制后的字幕语种 code；不传则沿用源字幕语种。 |

请求示例：

```json
{
  "idSeries": 239795,
  "ids": [17983708],
  "sourceLang": "zh-yue"
}
```

响应 `body` 是新字幕列表。新字幕的 `id` 可继续作为 `idVeMaterialSrt` 使用。

## 相关文档

- [译制出海剪辑 API 总览](./51-series-overview.md)：查看完整生命周期。
- [译制出海项目与视频素材](./60-series-project-and-video-materials.md)：先准备 `idSeries` 和 `idMaterialVideo`。
- [译制出海通用任务结构](./52-series-edit-common-task-structure.md)：查看 `workDto.idVeMaterialSrt`。
- [译制出海字幕翻译任务](./62-series-subtitle-translation.md)：翻译字幕会生成新的字幕素材。
- [GhostCut 本地文件上传 API](./10-file-upload.md)：上传本地 SRT 到译制出海项目。

## Agent 决策规则

- 用户给本地 SRT 文件时，优先用 `srt_series` 上传流程。
- 用户给的是 SRT/VTT 文本内容时，调用 `series/srt/create`。
- 用户要给 AI 配音或字幕压制指定字幕时，先通过 `series/srt/list` 找到正确的 `idVeMaterialSrt`。
- `idMaterialSrt` 和 `idVeMaterialSrt` 完全等价；后续任务通常使用字段名 `idVeMaterialSrt`，取值可用字幕列表 `body[].id`。
- 字幕提取或字幕翻译完成后，应通过 `subtitleFrom` 过滤查询产出的字幕素材。
- 需要把 `slInfo` 转成 SRT 时，优先使用 `sl[]._start`、`sl[]._end` 和 `sl[].src`；缺失时再用 `starting_time`、`duration`、`text` 兜底。不要保留前端编辑字段。
