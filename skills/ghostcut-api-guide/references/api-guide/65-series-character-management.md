# 译制出海剧集角色管理

> 本文说明如何维护译制出海剧集中的角色资料，以及如何把剧集角色 ID 映射到字幕和经典 AI 配音请求。角色管理接口统一使用 `POST`，接口前缀为 `/v-w-c/gateway/ve/series_character`。

## 适用场景

- 为剧集创建、查询或更新角色资料。
- 批量创建角色，或批量更新角色删除状态。
- 把来源剧集的角色及其关联句子复制到目标剧集。
- 为经典 AI 配音准备 `id_ve_character`，并与公共音色 ID 配对。

## 角色 ID 与音色 ID

这两个 ID 表示不同实体，不得混用：

| 字段 | 含义 | 来源 |
| --- | --- | --- |
| `id_ve_character` | 当前剧集中的业务角色 ID。 | `series_character/listCharacter` 返回角色对象的 `id`，或字幕 `slInfo.sl[].id_ve_character`。 |
| `id_ve_voice_character` | 用于生成配音的公共音色 ID。 | `voicecharacter/aggregate/list` 返回音色对象的 `id`。 |

经典 AI 配音的 `character_voices[]` 通常同时包含两个字段：前者指定“给哪个剧集角色配音”，后者指定“使用哪个公共音色”。角色名、剧集角色 ID 和字幕句子中的角色信息应保持一致。

## `VeCharacterDto` 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `Long` | 角色主键 ID；在配音和字幕上下文中对应 `id_ve_character`。 |
| `deleted` | `Byte` | `0` 未删除，`1` 已删除。 |
| `sourceType` | `Byte` | 角色来源类型。 |
| `idSeries` | `Long` | 所属剧集 ID。 |
| `characterIndex` | `Short` | 角色序号。 |
| `characterName` | `String` | 角色名。 |
| `gtCharacterName` | `String` | 标准角色名。 |
| `introduction` | `String` | 角色介绍。 |
| `frequency` | `BigDecimal` | 角色出现频次。 |
| `characterOtherNames` | `String` | 角色别名。 |
| `ossInfos` | `String` | 角色素材 OSS 信息的 JSON 字符串。 |
| `idVeAutoCharacterSubtask` | `Long` | 来源子任务 ID。 |
| `idVeAutoCharacterTask` | `Long` | 来源任务 ID。 |
| `gender` | `Byte` | `0` 男性，`1` 女性，`-1` 未设置。 |
| `company` | `String` | 公司标识，由服务端生成。 |
| `uid` | `String` | 用户标识，由服务端生成。 |

`ossInfos` 可包含 `oss_bucket`、`oss_endpoint`、`face_osskey`、`face_vertical_osskey` 和 `ref_video_osskey`。调用方不使用角色素材时不需要主动构造该字段。

## 分页规则

`listCharacter` 使用以下分页字段，与部分从 `0` 开始的剧集素材列表不同：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `pageNumber` | `Integer` | 否 | 页码，从 `1` 开始。 |
| `pageSize` | `Integer` | 否 | 每页条数，默认 `20`。 |
| `orderBy` | `String` | 否 | 排序表达式，例如 `ctime ASC` 或 `id DESC`。 |

## 创建单个角色

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series_character/createCharacter
```

请求体使用 `veCharacterDto`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `veCharacterDto` | `Object` | 是 | 单个角色对象。 |
| `veCharacterDtos` | `List<Object>` | 否 | 兼容的角色对象列表字段；创建单个角色时不需要传。 |

```json
{
  "veCharacterDto": {
    "idSeries": 10001,
    "characterName": "李明",
    "gtCharacterName": "Li Ming",
    "introduction": "主要角色",
    "gender": 0
  }
}
```

响应 `body` 是创建后的角色对象。保存 `body.id`，后续可作为该剧集角色的 `id_ve_character`。

## 批量创建角色

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series_character/createCharacterBatch
```

请求体使用 `veCharacterDtos[]`：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `veCharacterDto` | `Object` | 否 | 兼容的单个角色对象字段；批量创建时不需要传。 |
| `veCharacterDtos` | `List<Object>` | 是 | 待创建的角色对象列表。 |

```json
{
  "veCharacterDtos": [
    {
      "idSeries": 10001,
      "characterName": "李明",
      "gtCharacterName": "Li Ming"
    },
    {
      "idSeries": 10001,
      "characterName": "王雪",
      "gtCharacterName": "Wang Xue"
    }
  ]
}
```

响应 `body` 是实际创建成功的角色数量。需要获得新角色 ID 时，创建后再调用角色列表接口查询。

## 查询角色列表

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series_character/listCharacter
```

常用筛选字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `deleted` | `Byte` | 否 | 删除状态。 |
| `ids` | `List<Long>` | 否 | 角色主键 ID 列表。 |
| `idSeries` | `List<Long>` | 否 | 剧集 ID 列表；注意这里是数组。 |
| `sourceType` | `Byte` | 否 | 角色来源类型。 |
| `characterName` | `String` | 否 | 按角色名过滤。 |
| `pageNumber` | `Integer` | 否 | 页码，从 `1` 开始。 |
| `pageSize` | `Integer` | 否 | 每页条数。 |
| `orderBy` | `String` | 否 | 排序表达式。 |

`company` 和 `uid` 由服务端生成，普通调用方不应主动传入。

```json
{
  "idSeries": [10001],
  "deleted": 0,
  "pageNumber": 1,
  "pageSize": 20,
  "orderBy": "id DESC"
}
```

响应 `body[]` 是角色列表，`count` 是符合条件的总记录数。

## 更新角色

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series_character/updateCharacter
```

请求体使用 `veCharacterDto`，至少应包含待更新角色的 `id` 和所属 `idSeries`：

```json
{
  "veCharacterDto": {
    "id": 20001,
    "idSeries": 10001,
    "characterName": "李明",
    "gtCharacterName": "Li Ming",
    "introduction": "更新后的角色介绍"
  }
}
```

响应 `body` 是更新成功的记录数。

## 批量更新删除状态

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series_character/updateCharacterBatch
```

该接口通过 `deleted` 设置目标状态，可用于批量删除或恢复角色：

```json
{
  "deleted": 1,
  "ids": [20001, 20002]
}
```

响应 `body` 是更新成功的记录数。执行前应确认字幕句子和后续配音任务是否仍引用这些角色 ID。

接口模型还包含 `company` 和 `uid`，这两个字段由服务端根据当前身份生成，普通调用方不应主动传入。

## 复制剧集角色

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series_character/copyCharacter
```

```json
{
  "fromIdSeries": 10001,
  "toIdSeries": 10002
}
```

处理规则：

- 从来源剧集复制角色到目标剧集。
- 目标剧集中已有的同名角色会跳过，不重复创建。
- 成功复制角色关联的句子数据会同步复制。
- 被同名规则跳过的角色，其关联句子也会跳过。
- 响应 `body` 是实际复制成功的角色数量。

复制完成后，应查询目标剧集角色列表获取新角色 ID。不要假设来源角色 ID 在目标剧集中保持不变。

接口模型还包含 `company` 和 `uid`，这两个字段由服务端根据当前身份生成，普通调用方不应主动传入。

## 与字幕和配音的衔接

1. 调用 `listCharacter` 获取当前剧集角色及其 `id`。
2. 读取字幕素材 `slInfo.sl[]`，核对 `character` 和 `id_ve_character`。
3. 如果字幕角色信息需要修正，先更新字幕或业务侧的逐句角色映射。
4. 调用公共音色接口选择支持目标语种的 `id_ve_voice_character`。
5. 在经典配音的 `character_voices[]` 中同时填写角色名、`id_ve_character` 和 `id_ve_voice_character`。

## 提交前检查清单

- 角色属于当前 `idSeries`。
- `listCharacter.idSeries` 使用数组，不要误传单个数字。
- `pageNumber` 从 `1` 开始，不要套用剧集素材列表从 `0` 开始的规则。
- `id_ve_character` 来自剧集角色或字幕角色，不是公共音色 ID。
- `id_ve_voice_character` 来自公共音色接口，不是剧集角色 ID。
- 更新或删除角色前，确认字幕句子和配音配置是否仍在引用该角色。
- 复制角色后重新查询目标剧集角色 ID，不复用来源剧集角色 ID。

## 相关文档

- [译制出海剪辑 API 总览](./51-series-overview.md)：查看完整项目流程和两种接入模式。
- [译制出海项目与视频素材](./60-series-project-and-video-materials.md)：创建或查询剧集并获得 `idSeries`。
- [译制出海字幕素材管理](./61-series-subtitle-materials.md)：从 `slInfo.sl[]` 读取字幕角色信息。
- [译制出海 AI 配音](./56-series-dubbing.md)：把剧集角色与公共音色映射到 `character_voices[]`。
- [公共音色查询接口](./32-public-voice-characters.md)：获取 `id_ve_voice_character` 和支持语种。
- [译制出海错误与检查清单](./59-series-edit-errors-and-checklist.md)：排查项目上下文和 ID 混用问题。

## Agent 决策规则

- 用户要创建、维护、删除、恢复、复制或查询剧集角色时，使用本文接口。
- 用户只需要选择配音音色时，读取公共音色文档；不要为此创建剧集角色。
- 为经典配音组装角色音色映射时，同时读取本文、AI 配音文档和公共音色文档。
- 不要根据角色名猜测角色 ID；先查询当前剧集角色列表。
- 不要根据来源剧集角色 ID 推断复制后的目标角色 ID；复制后重新查询。
