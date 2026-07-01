# 视频处理状态枚举

> 本文档整理 GhostCut 视频处理结果 `processStatus` 的枚举值、公共错误码和排查建议。普通单视频任务的 `/v-w-c/gateway/ve/work/status` 查询方法见[视频任务状态查询](./11-work-status-query.md)。

## 查询枚举接口

GhostCut 提供统一枚举查询接口，用于获取状态码、语种列表等动态数据。该接口无需签名。

```http
POST https://api.zhaoli.com/v-w-c/enum/query2
Content-Type: application/json
```

请求体只需要传入 `text` 字段，大小写不敏感：

```json
{
  "text": "ProcessStatus"
}
```

支持的枚举名称：

| 枚举名称 | 说明 |
| --- | --- |
| `ProcessStatus` | 视频处理结果状态码 |
| `musicRegion` | 智能配乐支持的音乐区域 |
| `sourceLang` | 视频翻译源语言支持列表 |
| `Lang` | 视频翻译目标语言支持列表 |
| `ImageTaskStatus` | 图片任务状态码 |

响应中的每个枚举项通常包含：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `code` | `number` | 枚举码 |
| `description` | `string` | 中文说明 |
| `descriptionEn` | `string` | 英文说明 |
| `descriptionPt` | `string` | 葡萄牙语说明 |

## 公共错误码

所有接口响应体中的 `code` 表示请求结果。`code=1000` 仅表示接口请求成功，业务逻辑仍需继续检查 `body` 里的任务状态或结果字段。

| `code` | 名称 | 错误信息 | 说明 |
| --- | --- | --- | --- |
| `1000` | `SUCCESS` | `success` | 请求成功，但仍需进一步检查 `body` 内容。 |
| `2001` | `KEY_SIGN_REQUISITE` | `Requires Http header AppKey & AppSign` | 缺少请求头中的签名信息。 |
| `2002` | `POST_ONLY` | `HttpMethod must be POST` | 请求方法必须为 POST。 |
| `2003` | `KEY_INVALID` | `AppKey is invalid` | `AppKey` 错误。 |
| `2004` | `SIGN_INVALID` | `AppSign is invalid` | `AppSign` 签名错误。 |
| `3001` | `DATA_SAVE_ERROR` | `Data process failure` | 数据处理失败。 |
| `3002` | `DATA_UPDATE_ERROR` | `Data update failure` | 数据更新失败。 |
| `3003` | `AE_ID_NOT_EXISTED` | `Id not existed` | ID 不存在。 |
| `3006` | `LIMIT_ERROR` | `Data process Limit` | 超过处理限制。 |
| `3007` | `DATA_ERROR` | `At least one identity is required` | 开户至少需要一个身份标识。 |
| `3008` | `URLS_ERROR` | `urls is required` | 缺少 `urls` 参数。 |
| `4001-4004` | 业务错误 | 多种 | 参数非法、未选择接口或功能、需要创建用户等业务问题。 |
| `9999` | `SYSTEM_ERROR` | `System error` | 系统错误，请联系技术支持。 |

## `processStatus` 处理规则

普通单视频任务按[视频任务状态查询](./11-work-status-query.md)读取 `body.content[]` 后，通常判断：

```python
content = result["body"]["content"][0]
status = content["processStatus"]
```

通用判断：

| 判断 | 含义 | 建议 |
| --- | --- | --- |
| `processStatus == 1` | 任务成功 | 读取 `videoUrl`、`srcSrtUrl`、`tgtSrtUrl` 等结果字段，具体字段取决于功能。 |
| `processStatus < 1` | 任务尚未最终完成 | 继续等待并轮询；具体轮询策略见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。生产接入优先推荐 `callback`。 |
| `processStatus > 1` | 任务失败或资源异常 | 按下方状态表排查；可自查的问题修复后重新提交，平台或算法问题联系 GhostCut。 |

## 视频处理状态表

| `processStatus` | 描述 | 英文描述 | 排查与处理建议 |
| --- | --- | --- | --- |
| `-3` | 草稿处理成功，等待后续处理 | `succeed in generating draft, waiting for video synthesis` | 中间状态，继续轮询。 |
| `-2` | 素材准备中 | `Material in preparation` | 中间状态，继续轮询。 |
| `-1` | 默认，需要进行处理 | `requires processing` | 中间状态，继续轮询。 |
| `0` | 工程文件构建完成，处理中 | `Project file construction completed, processing` | 中间状态，继续轮询。 |
| `1` | 成功 | `Successful` | 处理成功，读取结果 URL。 |
| `2` | URL 解析失败 | `url resolution failure` | 检查视频链接是否仍有效、是否是直接可访问的视频链接。图集页、登录态页面、重定向异常都可能失败。修复后重新提交。 |
| `3` | 下载失败 | `Download failure` | 检查视频链接或上传视频是否损坏。常见问题包括无法播放、播放一段后中断、音频流和视频流长度差异过大。修复后重新提交。 |
| `5` | 视频时长超过设定限制 | `The video length exceeds the set limit` | 当前素材时长上限为 15 分钟。超长视频需先分段，建议每段略小于 15 分钟，例如 14 分 59 秒。 |
| `6` | 视频语音翻译调用失败 | `Video speech translation call failed` | 联系 GhostCut 处理。 |
| `7` | 视频语音翻译处理失败 | `Description Failed to process video speech translation` | 联系 GhostCut 处理。 |
| `13` | 配乐处理失败 | `Card processing failed. Procedure` | 联系 GhostCut 处理。 |
| `14` | 素材 `osskey` 不存在 | `The asset osskey does not exist` | 先检查传给 GhostCut 的 URL 是否可访问；如可访问仍失败，联系 GhostCut。 |
| `16` | 视频可能存在损坏 | `The last 0.2 seconds of the video can't be read. There may be corruption` | 平台下载后检测到视频编解码异常。检查素材能否完整播放，必要时重新导出或重新上传后再提交。 |
| `18` | 视频处理超时 | `Video processing timeout` | 可能与服务器、网络传输或算法处理有关。可先重试；重试仍失败后联系 GhostCut。 |
| `20` | 视频擦除处理失败 | `The video erasing process failed` | 联系 GhostCut 处理。 |
| `21` | 语音分离失败 | `Speech separation failure` | 联系 GhostCut 处理。 |
| `22` | 远程服务任务发送失败 | `Failed to send the remote service task` | 联系 GhostCut 处理。 |
| `23` | 远程处理超时 | `processing timeout` | 可先自行排查并重试；重试仍失败后联系 GhostCut。 |
| `24` | 克隆声音不存在，可能未完成克隆 | `Clone sound does not exist. Clone may not be complete` | 检查克隆声音是否已完成、是否可用，以及传入的声音 ID 是否正确。 |
| `26` | 数据格式验证失败 | `Data supplied did not pass validation` | 根据 `error_detail` 检查参数格式并修复后重新提交。API 用户通常需要重点关注此错误。 |
| `27` | 用户提供的字幕文件比视频长，可能不匹配 | `Duration of subtitle supplied by customer is longer than the material video.` | 检查字幕是否匹配视频、字幕时间轴是否正确、视频音频流和视频流时长是否差异过大。修复后重新提交。 |
| `28` | 审核错误，请检查译文字幕内容 | `The translated subtitles violate the content policy` | 检查译文字幕是否存在涉黄、暴力、侵害儿童等违规内容。修改后重新提交。 |
| `29` | 没有为某些配音角色配置声音 | `No voice is configured for some roles` | 检查角色与声音配置，确保所有 `character` 都在 `wyVoiceParam.character_voices` 中绑定了声音。 |
| `30` | 用户给定的句子过短，小于 0.1 秒 | `Sentence supplied by customer is too short, less than 0.1 seconds` | 检查自定义字幕或时间轴，避免单句时长小于 0.1 秒。 |
| `31` | TTS 音频损坏，请检查用来配音的文本 | `TTS audio is corrupt, please check the text used for TTS` | 检查 TTS 文本内容，修复异常文本后重新提交。 |
| `32` | 视频没有音频流也没有提供字幕 | `Video does not contain audio and no subtitle supplied by customer, please check` | 检查视频是否含音频；若无音频，需要提供字幕文件或台词时间轴。 |
| `43` | 未知错误 | `Unknown error` | 可能由多种原因造成，部分重试可恢复。重试仍失败后联系 GhostCut。 |
| `73` | 点卡资源不足，处理未开始 | `Insufficient point card resources, processing has not begun` | 点数不足，视频未开始处理。充值后重试处理。 |
| `83` | 点卡资源不足，处理已完成 | `Insufficient point card resources, processing completed` | 视频已处理成功，但因点数不足被锁住。充值后解锁视频。 |
| `98` | 存储空间资源耗尽 | `Storage space resources are used up. Procedure` | 用户存储空间不足，可删除历史素材后重试。 |
| `99` | 超出素材时长限制 | `The duration limit of the footage is exceeded` | 当前素材时长上限为 15 分钟。超长视频需先分段，建议每段略小于 15 分钟。 |
| `100` | 超出素材大小限制 | `The footage size limit is exceeded` | 单文件要求小于 1000M。请先压缩视频，降低文件大小后重新提交。 |
| `111` | 处理超时 | `Processing timeout` | 可先重试；重试仍失败后联系 GhostCut。 |
| `1000` | success | `success` | 枚举项中的成功值。实际任务成功通常以 `processStatus == 1` 为准。 |

## 按处理方式分组

### 继续轮询

`-3`、`-2`、`-1`、`0`

这些值表示任务尚未最终完成。调用方应继续等待并轮询，不应判定为失败。

### 成功

`1`

任务已成功。根据功能读取对应结果字段：

| 功能 | 常见结果字段 |
| --- | --- |
| 视频处理、擦除、翻译、配音、背景音乐分离 | `videoUrl` |
| OCR 字幕提取、ASR 字幕提取 | `srcSrtUrl`、`tgtSrtUrl` |

### 用户可自查后重试

`2`、`3`、`5`、`14`、`16`、`24`、`26`、`27`、`28`、`29`、`30`、`31`、`32`、`73`、`83`、`98`、`99`、`100`

这些状态通常与输入 URL、素材质量、字幕文件、配音配置、资源额度或文件限制有关。应先按状态表修复输入或资源问题，再重新提交。

### 可重试，失败后联系 GhostCut

`18`、`23`、`43`、`111`

这些状态可能是临时处理超时或未知异常。可以先重试；重试仍失败后联系 GhostCut。

### 建议直接联系 GhostCut

`6`、`7`、`13`、`20`、`21`、`22`

这些状态更偏平台服务或算法处理失败，建议联系 GhostCut 排查。

## Python 状态处理示例

```python
def handle_process_status(content: dict) -> str:
    status = content.get("processStatus")

    if status == 1:
        return "success"

    if isinstance(status, int) and status < 1:
        return "processing"

    retry_after_fix = {2, 3, 5, 14, 16, 24, 26, 27, 28, 29, 30, 31, 32, 73, 83, 98, 99, 100}
    retry_then_contact = {18, 23, 43, 111}
    contact_support = {6, 7, 13, 20, 21, 22}

    if status in retry_after_fix:
        return "failed_fix_input_or_resource_then_retry"

    if status in retry_then_contact:
        return "failed_retry_then_contact_support"

    if status in contact_support:
        return "failed_contact_support"

    return "failed_unknown_status"
```

## Agent 决策规则

- 不要只检查接口外层 `code == 1000`。创建任务和查询任务都可能外层成功，但视频任务仍在处理中或失败。
- 对视频任务，优先读取 `processStatus`。`1` 才是任务成功；小于 `1` 继续轮询；大于 `1` 按状态表处理。
- 如果失败原因与 URL、视频损坏、时长、大小、字幕时间轴、角色音色、点数或存储空间有关，应提示用户修复输入或资源后重新提交。
- 如果失败原因属于平台处理、算法处理、远程服务发送失败或多次重试仍失败，应提示联系 GhostCut。
- OCR/ASR 字幕提取成功后通常读取 `srcSrtUrl` / `tgtSrtUrl`；视频类处理成功后通常读取 `videoUrl`。

## 相关文档

- [API 总览](./00-api-overview.md)：查看异步任务的通用调用流程。
- [视频任务状态查询](./11-work-status-query.md)：查看 `/work/status` 的请求体、响应路径和轮询建议。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试和幂等规则。
- [视频去字幕](./21-erase-video-subtitle.md)：擦除任务成功后通常读取 `videoUrl`。
- [为视频压制字幕](./23-burn-subtitles.md)：字幕压制任务成功后通常读取 `videoUrl`。
- [OCR 提取视频字幕](./24-ocr-subtitle-extraction.md)：OCR 成功后通常读取 `srcSrtUrl` / `tgtSrtUrl`。
- [ASR 提取视频字幕](./25-asr-subtitle-extraction.md)：ASR 成功后通常读取 `srcSrtUrl` / `tgtSrtUrl`。
- [视频语音翻译与重新配音](./31-video-voice-translation.md)：视频翻译成功后通常读取 `videoUrl`，必要时再读取字幕 URL。
