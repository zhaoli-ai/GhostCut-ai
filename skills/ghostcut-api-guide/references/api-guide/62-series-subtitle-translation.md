# 译制出海字幕翻译任务

> 本文补充译制出海的字幕翻译任务。该接口用于把已有字幕翻译成目标语种，并生成新的字幕素材。API 只支持专家版 Agent 字幕翻译流程；产品中的非 Agent 免费字幕翻译流程当前没有开放 API。

## 使用流程

1. 准备项目，拿到 `idSeries` 和项目名称 `seriesName`。
2. 准备视频素材，拿到每集的 `idMaterialVideo`；在本接口的 `subtitleList[].idVeMaterialVideo` 字段中填写该视频素材 ID。
3. 准备源字幕，拿到源字幕 ID，并通过 `slInfo` 或 SRT 内容组装 `sourceSubtitleData[]`。
4. 可选：维护项目术语库，提升角色名、称谓和专有名词一致性。
5. 调用字幕翻译接口创建任务。
6. 调用翻译任务查询接口查看 `processStatus` 和 `stage`。
7. 如果 `auto_translate_on=false`，任务进入 `stage=3` 时需要人工审核术语库，然后调用推进接口传 `stage=4`。
8. 翻译完成后，通过字幕列表查询 `subtitleFrom=4` 的字幕素材，拿到新的 `idVeMaterialSrt`。

## 创建字幕翻译任务

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/translate/subtitle
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

该接口成功后会返回翻译任务 ID 列表。源文档定价说明为 `5` 点 / `30` 秒，其中提取术语表 `2` 点，翻译字幕 `3` 点。

### 请求字段

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idSeries` | `Long` | 是 | 项目 ID。 |
| `seriesName` | `String` | 是 | 项目名称。 |
| `taskList` | `List<Object>` | 是 | 翻译任务列表。一次调用视为一个批次。 |

`taskList[]` 字段：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `sourceLang` | `String` | 是 | 源字幕语种 code。 |
| `lang` | `String` | 是 | 目标语种 code。 |
| `taskSubType` | `String` | 是 | 固定传 `agent`。 |
| `projectName` | `String` | 是 | 视频任务名称，例如 `翻译为英文`。 |
| `projectVideoCount` | `Integer` | 是 | 本任务包含的视频数量，通常等于 `subtitleList.length`。 |
| `translateOptions` | `String` | 是 | 翻译配置，注意是 JSON 字符串，不是对象。 |
| `subtitleList` | `List<Object>` | 是 | 待翻译字幕列表。 |

`translateOptions` 常用字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `adjust_speed_on` | `Boolean` | 是否开启自动调速。 |
| `auto_translate_on` | `Boolean` | 是否自动翻译；`false` 时需要人工审核术语库后再推进。 |

`subtitleList[]` 字段：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `materialName` | `String` | 是 | 字幕对应的视频标题。 |
| `fileName` | `String` | 是 | 字幕文件名。 |
| `idVeMaterialVideo` | `Long` | 是 | 字幕对应的视频素材 ID，取自视频素材管理中的 `idMaterialVideo`。 |
| `idSource` | `Long` | 是 | 源字幕 ID。 |
| `sourceSubtitleData` | `List<Object>` | 是 | 源字幕行数据。 |

`sourceSubtitleData[]` 字段：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `start` | `Number` | 是 | 开始时间，单位秒。 |
| `end` | `Number` | 是 | 结束时间，单位秒。 |
| `source` | `String` | 是 | 原文文本。 |
| `translation` | `String` | 是 | 初始译文；源文档示例中可先填原文。 |
| `character` | `String` | 否 | 角色标记名。 |

从字幕素材的 `slInfo.sl[]` 组装 `sourceSubtitleData[]` 时，按以下映射处理：

| `sourceSubtitleData` 字段 | `slInfo.sl[]` 取值 |
| --- | --- |
| `start` | `sl[]._start`，缺失时取 `sl[].starting_time` 或 `sl[]._starting_time`。 |
| `end` | `sl[]._end`，缺失时用开始时间加 `sl[].duration`。 |
| `source` | `sl[].src`，缺失时取 `sl[].text`。 |
| `translation` | 创建翻译任务前可先填同 `source`。 |
| `character` | `sl[].character`。 |

`slInfo` 的完整解析规则见 [译制出海字幕素材管理](./61-series-subtitle-materials.md)。不要把 `_color`、`_display`、`_mask_top` 等前端编辑字段放进 `sourceSubtitleData[]`。

如果输入数据中出现 `sourceSubtitleData[].use_for_clone`，组装字幕翻译请求时不要依赖该字段，也不要用它判断后续配音是否为情感克隆模式。情感克隆模式以配音任务中的 `wyTaskType=VOICE_CLONE_PRO` 为准。

### 请求示例

```json
{
  "idSeries": 124756,
  "seriesName": "卡提西娅",
  "taskList": [
    {
      "sourceLang": "zh",
      "lang": "en",
      "taskSubType": "agent",
      "projectName": "翻译为英文",
      "projectVideoCount": 2,
      "translateOptions": "{\"adjust_speed_on\": false, \"auto_translate_on\": true}",
      "subtitleList": [
        {
          "materialName": "第一集",
          "fileName": "第一集.srt",
          "idVeMaterialVideo": 64138000,
          "idSource": 2643558,
          "sourceSubtitleData": [
            {
              "start": 13,
              "end": 15.02,
              "source": "告诉我我是谁？",
              "translation": "告诉我我是谁？",
              "character": "默认角色0"
            }
          ]
        },
        {
          "materialName": "第二集",
          "fileName": "第二集.srt",
          "idVeMaterialVideo": 64138001,
          "idSource": 2643559,
          "sourceSubtitleData": [
            {
              "start": 11,
              "end": 13.02,
              "source": "告诉我我是谁2？",
              "translation": "告诉我我是谁2？",
              "character": "默认角色0"
            }
          ]
        }
      ]
    }
  ]
}
```

响应示例：

```json
{
  "body": [3000408],
  "code": 1000,
  "count": 0,
  "msg": "success"
}
```

## 查询翻译任务列表

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/translate/subtitle/queryTask
```

常用请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idSeriesList` | `List<Long>` | 否 | 项目 ID 列表。 |
| `ids` | `List<Long>` | 否 | 翻译任务 ID 列表。 |
| `deleted` | `Byte` | 否 | 是否删除，`0` 否，`1` 是。 |
| `stage` | `Byte` | 否 | 任务阶段，完整枚举见下方 `stage` 枚举。 |
| `page` | `Integer` / `null` | 否 | 页码，从 `0` 开始；不需要分页时传 `null`，默认返回最新 `200` 条。 |
| `pageSize` | `Integer` / `null` | 否 | 每页数量；不需要分页时传 `null`，最大 `2000`，超过 `2000` 只返回 `2000` 条。 |

请求示例：

```json
{
  "idSeriesList": [124756],
  "ids": [3000408],
  "page": 0,
  "pageSize": 20
}
```

关键响应字段：

| 字段 | 说明 |
| --- | --- |
| `id` | 翻译任务 ID。 |
| `idSeries` | 所属项目 ID。 |
| `processStatus` | 处理状态，`1` 表示成功。 |
| `stage` | 翻译阶段，完整枚举见下方 `stage` 枚举。 |
| `srcLang` | 源语种。 |
| `tgtLang` | 目标语种。 |
| `inputData` | 输入数据快照，包含 episode 信息和生成的字幕素材信息。 |
| `translateOptions` | 翻译配置。 |
| `paidPoint` | 消耗点数。 |
| `count` | 总条数。 |

### `stage` 枚举

| 值 | 枚举名 | 含义 |
| --- | --- | --- |
| `0` | `DEFAULT` | 初始。 |
| `1` | `ANALYZING` | 分析剧情。 |
| `2` | `REPORT_GENERATING` | 生成词表与翻译指南。 |
| `3` | `GLOSSARY_WAITING_MODIFY` | 等待词表编辑。 |
| `4` | `GLOSSARY_MODIFIED` | 词表编辑完成。 |
| `5` | `TRANSLATING` | 翻译中。 |
| `6` | `FINISHED` | 完成。 |

`queryTask` 查询翻译任务时使用 `idSeriesList`、`ids`、`deleted`、`stage`、`page`、`pageSize`。不要把术语库接口里的 `veTranslateGlossary2Dto` 放到本接口请求体中。

## 推进或重试翻译任务

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/translate/subtitle/confirmTask
```

适用场景：

- 创建任务时 `auto_translate_on=false`，术语库审核后继续推进。
- 翻译任务失败后发起重试。

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `Long` | 是 | 翻译任务 ID。 |
| `stage` | `Byte` | 审核推进时必填 | 待审核任务为 `stage=3`；调用本接口时传 `stage=4` 表示词表编辑完成并继续推进。 |

请求示例：

```json
{
  "id": 3005798,
  "stage": 4
}
```

响应中 `body=1` 表示发起成功，`body=0` 表示发起失败。

## 翻译结果获取

翻译任务成功后会生成新的字幕素材。Agent 应通过 [字幕素材管理](./61-series-subtitle-materials.md) 查询：

```json
{
  "idSeries": 124756,
  "subtitleFrom": 4,
  "sourceLang": "en",
  "page": 0,
  "pageSize": 20
}
```

如果要把译后字幕用于配音或字幕压制，把查询到的字幕 `id` 作为 `workDto.idVeMaterialSrt`，或把字幕内容转换成 `workDto.extraOptions.customer_input.content[]`。两种输入方式必须二选一，不能同时传。

## 相关文档

- [译制出海剪辑 API 总览](./51-series-overview.md)：查看完整生命周期。
- [译制出海字幕素材管理](./61-series-subtitle-materials.md)：准备源字幕并获取译后字幕。
- [译制出海翻译术语库](./63-series-translation-glossary.md)：维护角色名、称谓和专有名词。
- [译制出海 AI 配音](./56-series-dubbing.md)：使用译后字幕和角色音色发起配音。
- [译制出海字幕压制](./57-series-subtitle-burn.md)：把译后字幕压制到视频画面。

## Agent 决策规则

- 译制出海字幕翻译 API 只支持专家版 Agent 字幕翻译；不要为非 Agent 免费字幕翻译流程编造 API 调用方式。
- 用户要“翻译字幕”但不是立刻合成视频时，使用本文接口，不要直接调用配音任务。
- 一个目标语种对应 `taskList[]` 中一个独立元素；多语种不要混在同一个任务项里。
- `translateOptions` 必须是字符串化 JSON。
- `auto_translate_on=false` 会产生人工审核节点；查到 `stage=3` 后，需要用户或业务系统审核术语库，再调用 `confirmTask` 传 `stage=4`。
- 不要把翻译任务 ID 当作字幕 ID；译后字幕 ID 应通过 `series/srt/list` 查询。
