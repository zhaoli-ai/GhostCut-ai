# 译制出海项目与视频素材

> 本文补充译制出海任务提交前的准备环节：创建或查询项目，获得 `idSeries`；上传、导入、查询和替换视频素材，获得可用于 `items[].idMaterialVideo` 的素材 ID。

## 适用场景

- 用户要新建一个译制出海项目或剧集。
- 用户已有项目名称，但还没有 `idSeries`。
- 用户要把本地视频或公网视频 URL 加入某个项目。
- 用户要确认视频素材是否已完成云端预处理。
- 用户要更新素材名称、标记源语言，或替换素材文件。

## 接口返回规则

项目管理和素材管理接口的成功响应通常是：

```json
{
  "code": 1000,
  "msg": "success",
  "body": {},
  "count": 0,
  "trace": "trace-id"
}
```

注意：`code=1000` 表示管理接口调用成功；译制出海剪辑任务提交接口通常使用 `code=200`。不要把两类接口的成功码混用。

## 项目管理

### 创建项目

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/create
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

请求示例：

```json
{
  "seriesDto": {
    "seriesName": "项目名称",
    "remark": "备注",
    "callback": "https://yourdomain.com/callback",
    "isDongman": 0
  }
}
```

`seriesDto` 字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `seriesName` | `String` | 是 | 项目或剧集名称。 |
| `remark` | `String` | 否 | 备注。 |
| `callback` | `String` | 否 | 本剧集下作品合成后的默认回调地址。生产接入推荐设置；回调格式、验签、重试和幂等规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。 |
| `isDongman` | `Integer` | 否 | 剧种：`0` 真人剧，`1` AI 漫剧，`2` AI 真人剧，`3` 其它。 |

响应中 `body.id` 就是 `idSeries`：

```json
{
  "body": {
    "id": 159001,
    "seriesName": "项目名称",
    "remark": "备注"
  },
  "code": 1000,
  "msg": "success"
}
```

### 查询项目列表

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/list
```

常用请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `ids` | `List<Long>` | 否 | 项目 ID 列表。已知 ID 时优先使用。 |
| `deleted` | `Byte` | 否 | 是否删除，`0` 未删除，`1` 已删除；不传则不区分。 |
| `seriesName` | `String` | 否 | 项目名称精确匹配。 |
| `seriesNameLike` | `String` | 否 | 项目名称模糊匹配。 |
| `remark` | `String` | 否 | 备注精确匹配。 |
| `remarkLike` | `String` | 否 | 备注模糊匹配。 |
| `needFileSize` | `Byte` / `Boolean` | 否 | 是否返回文件大小信息，常用 `1` 或 `true`。 |
| `cleanUp` | `Byte` | 否 | 是否清理，`0` 否，`1` 是。 |
| `page` | `Integer` | 否 | 页码，从 `0` 开始；不分页可传 `null`。 |
| `pageSize` | `Integer` | 否 | 每页数量，最大 `2000`。 |

请求示例：

```json
{
  "deleted": 0,
  "needFileSize": true,
  "seriesNameLike": "项目",
  "page": 0,
  "pageSize": 20
}
```

### 更新项目

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/update
```

目前主要用于更新 `remark`：

```json
{
  "seriesDto": {
    "id": 159001,
    "remark": "新的备注"
  }
}
```

成功时 `body=1`。

### 删除项目

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/delete
```

请求示例：

```json
{
  "ids": [159001]
}
```

成功时 `body` 是删除条数。

## 视频素材管理

### 本地视频上传到项目

本地视频不直接传给剪辑任务。应先使用 [文件上传](./10-file-upload.md) 的译制出海视频素材上传流程：

```json
{
  "nonce": "random-string",
  "idSeries": 159001,
  "materialFileType": "video_series",
  "materialName": "第一集"
}
```

获取上传凭证并完成 OSS 上传后，上传凭证响应中的 `body.idMaterialVideo` 是视频素材 ID。后续剪辑任务把它填入：

```json
{
  "items": [
    {
      "idMaterialVideo": 700435746
    }
  ]
}
```

上传后仍建议调用“查询项目内视频素材列表”，确认 `downloadStatus=1` 且 `processStatus=1` 后再提交剪辑任务。

### 导入视频 URL 到项目

如果视频已经是可公网访问 URL，使用导入接口：

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/video/import
```

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idSeries` | `Long` | 是 | 项目 ID。 |
| `url` | `String` | 是 | 可直接访问的视频 URL。 |
| `materialName` | `String` | 是 | 素材标题。 |
| `fileName` | `String` | 否 | 素材文件名。 |
| `callback` | `String` | 否 | 素材预处理进入最终状态时回调最新素材对象。生产接入推荐设置。 |

请求示例：

```json
{
  "idSeries": 124756,
  "url": "https://gc100.cdn.izhaoli.cn/ve_material_video/example/input.mp4",
  "materialName": "第一集",
  "fileName": "episode_001.mp4",
  "callback": "https://yourdomain.com/material-callback"
}
```

响应中 `body.id` 就是 `idMaterialVideo`。刚创建时素材可能不可用：

| 字段 | 含义 |
| --- | --- |
| `processStatus=-1` | 预处理中，暂不可用于任务。 |
| `processStatus=1` | 预处理完成，可用。 |
| `processStatus>1` | 预处理失败。 |

如果没有传 `callback`，应通过素材列表接口轮询。补偿轮询规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。

### 查询项目内视频素材列表

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/video/list
```

常用请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idSeries` | `Long` | 是 | 项目 ID。 |
| `ids` | `List<Long>` | 否 | 视频素材 ID 列表。非必填；已知 ID 时建议传，可用于精确查询。 |
| `downloadStatus` | `Byte` | 否 | 素材下载状态，`1` 可用，`<1` 准备中，`>1` 失败。 |
| `statusSubtitle` | `Byte` | 否 | 是否已提取字幕，`0` 否，`1` 是。 |
| `statusInpaint` | `Byte` | 否 | 是否已去文字，`0` 否，`1` 是。 |
| `statusSuppression` | `Byte` | 否 | 是否已字幕压制，`0` 否，`1` 是。 |
| `statusTransTts` | `Byte` | 否 | 是否已配音，`0` 否，`1` 是。 |
| `materialNameLike` | `String` | 否 | 素材名称模糊查询。 |
| `sourceLang` | `String` | 否 | 素材标记的源语言。 |
| `orderBy` | `String` | 否 | 例如 `id DESC`、`ctime DESC`、`lutime DESC`。 |
| `page` | `Integer` | 否 | 页码，从 `0` 开始。 |
| `pageSize` | `Integer` | 否 | 每页数量，最大 `2000`。 |

请求示例：

```json
{
  "idSeries": 124756,
  "ids": [700435746],
  "page": 0,
  "pageSize": 20
}
```

关键响应字段：

| 字段 | 说明 |
| --- | --- |
| `id` | 视频素材 ID，即 `idMaterialVideo`。 |
| `idSeries` | 所属项目 ID。 |
| `downloadStatus` | 下载或云端准备状态。`1` 才可用。 |
| `processStatus` | 预处理状态。`1` 才可用。 |
| `ossUrl` / `ossUrlTranscoding` | 素材可访问 URL。 |
| `duration` | 视频时长，单位秒。 |
| `fileSize` | 文件大小。 |
| `width` / `height` | 视频宽高。 |
| `sourceLang` | 素材源语言标记。 |
| `statusSubtitle` / `statusInpaint` / `statusSuppression` / `statusTransTts` | 素材在项目中的处理标记。 |

### 更新视频素材

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/video/update
```

目前主要用于更新 `materialName` 和 `sourceLang`，并且必须传 `idSeries`：

```json
{
  "materialVideoDto": {
    "id": 700435746,
    "idSeries": 124756,
    "materialName": "第一集新标题",
    "sourceLang": "zh"
  }
}
```

成功时 `body=1`。

### 删除视频素材

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/video/delete
```

请求示例：

```json
{
  "ids": [700435746]
}
```

删除视频素材时，会同时删除该素材对应的字幕文件。执行前应确认下游任务不再依赖这些素材。

### 替换视频素材文件

如果已经有视频素材 ID，但需要替换其对应的视频文件，有两种方式：

| 替换方式 | 做法 |
| --- | --- |
| 本地文件替换 | 使用 [文件上传](./10-file-upload.md) 中 `materialFileType=video_series_replace` 的上传凭证流程，传 `idMaterialVideo`。 |
| URL 替换 | 调用视频替换接口，传素材 ID 和新视频 URL。 |

URL 替换接口地址如下：

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/video/replace
```

请求示例：

```json
{
  "id": 700435746,
  "url": "https://example.com/new-video.mp4"
}
```

成功时 `body=1`，失败时 `body=0`。替换后应重新查询素材列表，等待 `downloadStatus=1` 且 `processStatus=1`。

## 提交剪辑任务前的素材检查

1. 项目存在，且已拿到 `idSeries`。
2. 每个视频素材都已拿到 `idMaterialVideo`。
3. 视频素材属于当前 `idSeries`。
4. `downloadStatus == 1`。
5. `processStatus == 1`。
6. `duration`、`width`、`height`、`fileSize` 等字段已返回，说明素材元信息可用。
7. 如任务依赖源语言，素材 `sourceLang` 或任务请求中的 `sourceLang` 已明确。

## 相关文档

- [译制出海剪辑 API 总览](./51-series-overview.md)：查看完整生命周期。
- [译制出海通用任务结构](./52-series-edit-common-task-structure.md)：查看 `idSeries`、`items[]` 和 `idMaterialVideo` 的使用位置。
- [GhostCut 本地文件上传 API](./10-file-upload.md)：上传本地视频、字幕和替换素材文件。
- [译制出海字幕素材管理](./61-series-subtitle-materials.md)：上传、创建、查询和更新字幕素材。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试、幂等和补偿轮询规则。
- [译制出海错误与检查清单](./59-series-edit-errors-and-checklist.md)：提交前排查常见问题。

## Agent 决策规则

- 用户只有项目名称，没有 `idSeries` 时，先查项目列表；查不到再创建项目。
- 创建项目、导入视频或提交处理任务时，生产接入推荐设置 `callback`；轮询用于素材状态查询和补偿兜底。
- 用户给本地视频路径时，走 `video_series` 上传；用户给公网视频 URL 时，走 `series/video/import`。
- 不要把普通上传返回的临时视频 URL 当成 `idMaterialVideo`；译制出海任务需要素材 ID。
- 创建或替换视频素材后，不要立刻提交剪辑任务；先查询素材状态，等 `downloadStatus=1` 且 `processStatus=1`。
- `items[].idMaterialVideo` 必须与顶层 `idSeries` 属于同一个项目。
