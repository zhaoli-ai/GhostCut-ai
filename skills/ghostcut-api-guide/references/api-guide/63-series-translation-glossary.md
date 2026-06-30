> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 译制出海翻译术语库

> 术语库用于提升译制出海字幕翻译的一致性，特别适合角色名、称谓、专有名词、世界观名词和固定译法。字幕翻译任务会参考同一 `idSeries` 下的术语。

## 术语关系

术语使用 `idParent` 表示原文和译文之间的关系：

| 条目 | `idParent` | 说明 |
| --- | --- | --- |
| 原文术语 | `0` | 例如中文原名。 |
| 译文术语 | 原文术语的 `id` | 例如英文、泰文、日文译名。 |

示例：

| 语言 | `id` | `idParent` | `original` |
| --- | --- | --- | --- |
| `zh` | `123` | `0` | `谢艳玲` |
| `en` | `456` | `123` | `Xie Yanling` |
| `th` | `789` | `123` | `เซี่ยเยี่ยนหลิง` |

## 插入术语

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/translate/createTranslateGlossary2
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `veTranslateGlossary2Dto` | `Object` | 是 | 术语信息。 |

`veTranslateGlossary2Dto` 常用字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `original` | `String` | 是 | 术语文本。 |
| `category` | `String` | 否 | 分类，例如 `角色`、`称谓/贬称`。 |
| `lang` | `String` | 是 | 术语语种 code。 |
| `idSeries` | `Long` | 是 | 所属项目 ID。 |
| `sourceType` | `Integer` | 否 | 来源类型，源文档示例传 `0`。 |
| `idParent` | `Long` | 否 | 原文和译文关联 ID；原文通常传 `0`。 |

请求示例：

```json
{
  "veTranslateGlossary2Dto": {
    "original": "谢艳玲",
    "category": "角色",
    "lang": "zh",
    "idSeries": 124756,
    "sourceType": 0,
    "idParent": 0
  }
}
```

响应 `body.id` 是新术语 ID。创建译文术语时，把原文术语 ID 填入 `idParent`：

```json
{
  "veTranslateGlossary2Dto": {
    "original": "Xie Yanling",
    "category": "角色",
    "lang": "en",
    "idSeries": 124756,
    "sourceType": 0,
    "idParent": 344339
  }
}
```

## 更新或删除术语

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/translate/updateTranslateGlossary2
```

请求示例：

```json
{
  "veTranslateGlossary2Dto": {
    "id": 344339,
    "original": "谢艳玲",
    "category": "角色",
    "lang": "zh",
    "idSeries": 124756
  }
}
```

删除术语时传 `deleted=1`：

```json
{
  "veTranslateGlossary2Dto": {
    "id": 344339,
    "idSeries": 124756,
    "deleted": 1
  }
}
```

响应 `body` 是更新后的术语对象。

## 查询术语表

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/translate/queryListTranslateGlossary2
```

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idSeries` | `List<Long>` | 否 | 项目 ID 列表。注意这里是列表。 |
| `deleted` | `Byte` | 否 | 是否删除，`0` 否，`1` 是。 |
| `lang` | `String` | 否 | 单个语种 code。 |
| `langList` | `List<String>` | 否 | 多个语种 code。 |
| `category` | `String` | 否 | 分类精确匹配。 |
| `categoryLike` | `String` | 否 | 分类模糊匹配。 |
| `originalLike` | `String` | 否 | 术语文本模糊查询。 |
| `page` | `Integer` | 否 | 页码，从 `0` 开始。 |
| `pageSize` | `Integer` | 否 | 每页数量，最大 `2000`。 |

请求示例：

```json
{
  "idSeries": [124756],
  "langList": ["zh", "en"],
  "deleted": 0,
  "page": 0,
  "pageSize": 200
}
```

关键响应字段：

| 字段 | 说明 |
| --- | --- |
| `id` | 术语 ID。 |
| `idParent` | 关联的原文术语 ID。 |
| `idSeries` | 所属项目 ID。 |
| `lang` | 术语语种。 |
| `original` | 术语文本。 |
| `category` | 分类。 |
| `sourceType` | 来源类型。 |
| `estimatedOccurrences` | 预估出现次数。 |
| `deleted` | 删除标记。 |

## 和字幕翻译任务的关系

- 翻译前可先写入角色名、称谓和专有名词。
- `auto_translate_on=false` 时，翻译任务会进入 `stage=3`（等待词表编辑），需要人工审核术语库后再推进。
- 审核完成后，通过 [字幕翻译任务](./62-series-subtitle-translation.md) 的 `confirmTask` 接口传 `stage=4`。

## 相关文档

- [译制出海字幕翻译任务](./62-series-subtitle-translation.md)：创建、查询、推进或重试翻译任务。
- [译制出海字幕素材管理](./61-series-subtitle-materials.md)：查询源字幕和译后字幕素材。
- [译制出海剪辑 API 总览](./51-series-overview.md)：查看完整生命周期。

## Agent 决策规则

- 用户提到“术语库”“角色名固定译法”“人名翻译一致”时，先查或维护本文接口。
- 创建译文术语前，先创建或查询原文术语，拿到原文 `id` 后再作为译文的 `idParent`。
- 查询术语表时，`idSeries` 是列表，不是单个数字。
- 删除术语不要调用物理删除接口；使用更新接口传 `deleted=1`。
- 翻译任务处于 `stage=3`（等待词表编辑）时，应先让用户或业务系统确认术语，再调用 `confirmTask` 传 `stage=4`。
