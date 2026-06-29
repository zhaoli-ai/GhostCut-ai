> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 视频任务状态查询

> 本文说明普通单视频任务如何调用 `/v-w-c/gateway/ve/work/status` 查询处理状态和结果 URL。状态枚举、错误码和失败排查见[视频处理状态枚举](./91-video-process-status.md)。

## 适用范围

本文适用于普通单视频处理能力，也就是创建任务后从 `body.dataList[].id` 拿到作品 ID 的功能：

| 功能 | 创建任务文档 | 成功后常读字段 |
| --- | --- | --- |
| 视频去字幕 | [视频去字幕](./20-erase-video-subtitle.md) | `videoUrl` |
| 字幕压制 | [为视频压制字幕](./22-burn-subtitles.md) | `videoUrl` |
| OCR 字幕提取 | [OCR 提取视频字幕](./23-ocr-subtitle-extraction.md) | `srcSrtUrl`、`tgtSrtUrl` |
| ASR 字幕提取 | [ASR 提取视频字幕](./24-asr-subtitle-extraction.md) | `srcSrtUrl`、`tgtSrtUrl` |
| 背景音乐去除/分离 | [背景音乐去除/分离](./30-background-music-separation.md) | `videoUrl` |
| 视频语音翻译与重新配音 | [视频语音翻译与重新配音](./31-video-voice-translation.md) | `videoUrl`，必要时再读取字幕 URL |

本文的签名方式、请求体格式和响应读取逻辑，也可用于译制出海场景下继续查询作品详情；但译制出海不能直接从提交任务接口拿作品 ID，而应先通过 `task/list` 获取任务 ID，再按本文方式调用 `/work/status`，并以该接口实际返回的作品详情为准。相关流程见[译制出海任务查询](./42-series-edit-task-list.md)。

译制出海任务串联流程中，如果后续任务需要填写 `workDto.materialWorkIds`，应使用本接口响应里的作品 ID，精确路径是 `body.content[].id`；单视频结果通常读取 `body.content[0].id`。

## 接口

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/work/status
Content-Type: application/json
AppKey: <your_app_key>
AppSign: <generated_app_sign>
```

请求体：

```json
{
  "idWorks": ["521461135"]
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `idWorks` | `string[]` / `number[]` | 查询 ID 列表。普通单视频任务中通常传作品 ID；译制出海场景下通常先传 `task/list` 返回的任务 ID，再读取本接口返回的作品详情。 |

签名规则和 `api_post` 封装方式见 [API 总览](./00-api-overview.md)。

## 响应读取

查询成功后，通常从以下路径读取任务结果：

```python
content = result["body"]["content"][0]
status = content["processStatus"]
```

示例响应：

```json
{
  "code": 1000,
  "msg": "success",
  "body": {
    "content": [
      {
        "id": "521461135",
        "processStatus": 1,
        "videoUrl": "https://example.com/result.mp4",
        "srcSrtUrl": "https://example.com/source.srt",
        "tgtSrtUrl": "https://example.com/target.srt"
      }
    ]
  }
}
```

注意：不同功能返回的结果字段不同。视频类任务通常读取 `videoUrl`；OCR/ASR 字幕提取只产出 SRT，通常读取 `srcSrtUrl` / `tgtSrtUrl`，不要等待 `videoUrl`。

如果本接口用于译制出海后续串联任务，`body.content[].id` 是作品 ID，可填入后续请求的 `workDto.materialWorkIds`。不要把 `task/list` 的 `body[].id` 直接填入 `materialWorkIds`，那个字段是任务 ID。

## 状态判断

| 判断 | 含义 | 下一步 |
| --- | --- | --- |
| `processStatus == 1` | 任务成功 | 按具体功能读取 `videoUrl`、`srcSrtUrl`、`tgtSrtUrl` 等结果字段。 |
| `processStatus < 1` | 任务仍在处理中 | 继续等待并轮询。建议间隔数分钟，避免高频请求。 |
| `processStatus > 1` | 任务失败或资源异常 | 读取 `errorDetail` 等错误信息，并按[视频处理状态枚举](./91-video-process-status.md)排查。 |

外层 `code=1000` 只表示本次查询接口调用成功，不代表视频任务已经处理成功。必须继续检查 `body.content[].processStatus`。

## Python 查询示例

```python
import hashlib
import json
import requests

APP_KEY = "your_app_key"
APP_SECRET = "your_app_secret"
BASE_URL = "https://api.zhaoli.com"


def api_post(path: str, payload: dict) -> dict:
    body_str = json.dumps(payload, ensure_ascii=False)
    sign = hashlib.md5(
        (hashlib.md5(body_str.encode("utf-8")).hexdigest() + APP_SECRET).encode("utf-8")
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "AppKey": APP_KEY,
        "AppSign": sign,
    }

    response = requests.post(
        f"{BASE_URL}{path}",
        headers=headers,
        data=body_str.encode("utf-8"),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def query_work_status(work_id: str) -> dict:
    result = api_post("/v-w-c/gateway/ve/work/status", {
        "idWorks": [work_id]
    })

    content = result["body"]["content"][0]
    status = content["processStatus"]

    if status == 1:
        return {
            "state": "success",
            "video_url": content.get("videoUrl"),
            "source_srt_url": content.get("srcSrtUrl"),
            "target_srt_url": content.get("tgtSrtUrl"),
            "raw": content,
        }

    if isinstance(status, int) and status < 1:
        return {
            "state": "processing",
            "raw": content,
        }

    return {
        "state": "failed",
        "process_status": status,
        "error_detail": content.get("errorDetail") or content.get("error_detail"),
        "raw": content,
    }
```

## 轮询建议

- 创建任务接口返回作品 ID 后，再调用本文接口查询最终状态。
- 处理类任务通常需要等待，建议间隔数分钟轮询，不要高频请求。
- 批量传多个 `idWorks` 时，应优先根据响应项中的作品 ID 匹配结果；如果响应项没有返回 ID，再结合调用方保存的请求顺序谨慎处理。
- 查询到 `processStatus > 1` 后，不要继续无意义轮询，应根据[视频处理状态枚举](./91-video-process-status.md)判断是否修复输入、重试或联系 GhostCut。

## Agent 决策规则

- 看到普通单视频任务创建成功后，必须继续查 `/work/status`，不要把创建接口的 `code=1000` 当作最终成功。
- 创建接口常见作品 ID 路径是 `body.dataList[0].id`；查询接口常见状态路径是 `body.content[0].processStatus`。
- 译制出海场景中，`/work/status` 返回的作品 ID 路径是 `body.content[].id`；单视频结果常读 `body.content[0].id`，这个值才可用于后续 `workDto.materialWorkIds`。
- 视频去字幕、字幕压制、背景音乐分离、视频语音翻译成功后通常读取 `videoUrl`。
- OCR/ASR 字幕提取成功后通常读取 `srcSrtUrl` / `tgtSrtUrl`，不要等待处理后视频。
- 译制出海模块应先查[译制出海任务查询](./42-series-edit-task-list.md)拿到任务 ID；如果还需要作品详情、作品 ID 或播放地址，再按本文方式调用 `/work/status`，并以返回的作品详情为准。

## 相关文档

- [API 总览](./00-api-overview.md)：查看通用调用流程、认证和签名规则。
- [文件上传](./10-file-upload.md)：本地文件先上传并获得临时 URL。
- [视频处理状态枚举](./91-video-process-status.md)：查看 `processStatus` 状态值、错误码和排查建议。
