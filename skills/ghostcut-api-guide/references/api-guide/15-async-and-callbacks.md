> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 异步任务、轮询和回调机制

> GhostCut 视频和图片处理接口均为异步任务。创建接口成功只表示任务已经提交或进入队列，不代表处理已经完成；调用方需要通过轮询或 `callback` 获取最终状态和结果，并按回调验签、重试和幂等规则处理重复推送。

## 适用范围

本文用于说明跨功能复用的异步任务规则。具体请求体字段、任务类型和结果字段仍以各功能文档为准。

| 场景 | 查询方式 | 状态字段 | 相关文档 |
| --- | --- | --- | --- |
| 普通单视频处理 | `POST /v-w-c/gateway/ve/work/status` | `body.content[].processStatus` | [视频任务状态查询](./11-work-status-query.md)、[视频处理状态枚举](./14-video-process-status.md) |
| 图片 AI 处理 | `POST /v-w-c/gateway/ve/image/translate/query` | `body.status` | [AI 图片处理](./81-image-processing.md) |
| 译制出海任务 | `POST /v-w-c/gateway/ve/series/edit/task/list`；必要时再查 `/work/status` | `successWorkCount`、`errorWorkCount`、`processingWorkCount`；作品详情使用 `processStatus` | [译制出海任务查询](./53-series-edit-task-list.md) |

## 异步任务模型

提交任务时，GhostCut 会先创建任务记录，再异步处理视频或图片素材。常见 ID 关系如下：

| ID | 含义 | 使用方式 |
| --- | --- | --- |
| `idProject` | 任务批次 ID。一次提交可包含多个视频 URL，这些视频可共享同一个 `idProject`。 | 用于识别同一批次或同一项目下的任务。 |
| `id` / `idWorks` | 作品 ID。普通视频任务中，每个视频 URL 通常对应一个独立作品 ID。 | 查询普通视频任务结果时，把作品 ID 放入 `idWorks`。 |
| 图片任务 ID | 图片处理创建接口返回的 `body`。 | 查询图片任务时传给 `/image/translate/query` 的 `id` 字段。 |
| `task/list.body[].id` | 译制出海任务 ID，也可理解为 project/task ID。 | 译制出海先用它查询任务或继续调用 `/work/status`。不要直接当作后续 `materialWorkIds`。 |
| `/work/status.body.content[].id` | `/work/status` 返回的作品 ID。 | 译制出海后续任务需要复用前序作品时，填入 `workDto.materialWorkIds`。 |

外层接口返回 `code=1000` 或 `code=200` 只表示请求被接受或查询接口调用成功。任务最终是否成功，必须继续检查任务状态字段。

## 状态判断

视频任务以 `processStatus` 为准，完整枚举见[视频处理状态枚举](./14-video-process-status.md)。图片任务状态可通过枚举接口查询 `ImageTaskStatus`，图片接口常用状态读取方式见[AI 图片处理](./81-image-processing.md)。

通用判断规则：

| 状态判断 | 含义 | 下一步 |
| --- | --- | --- |
| `< 1` | 处理中或等待处理 | 继续等待并轮询，或等待回调。 |
| `== 1` | 处理成功 | 读取对应结果字段，如 `videoUrl`、`srcSrtUrl`、`tgtSrtUrl`、`result.output_url`、`result.inpaint_url`。 |
| `> 1` | 处理失败或资源异常 | 读取 `processStatusEnum`、`taskStatusEnum`、`errorDetail` 等错误信息，并按功能文档排查。 |

## 轮询策略

推荐轮询方式：

1. 创建任务后，先保存任务 ID、作品 ID、用户业务单号和提交时间。
2. 初始轮询间隔建议设为 300 秒；如果任务耗时较长，应逐步拉长间隔，避免高频请求。
3. 普通视频任务优先使用 `idWorks` 精确查询单个作品状态，效率更高。
4. 图片任务使用图片任务 ID 查询 `/image/translate/query`。
5. 译制出海任务优先轮询 `task/list`；如果需要作品 ID、作品详情或播放地址，再用任务 ID 查询 `/work/status`。
6. 查询到成功或失败后停止轮询。失败后不要继续无意义轮询，应根据错误信息决定修复输入、重试或联系 GhostCut。

补偿扫描或批量排查时，可在支持的查询接口中结合分页参数，以及 `createTimeGreaterThanOrEqualTo`、`createTimeLessThan` 等创建时间范围字段筛选任务。精确查询结果时，仍优先使用任务 ID 或作品 ID。

## 回调机制

创建任务时，如果接口支持 `callback` 参数，可传入一个公网可访问的回调 URL。任务进入最终状态后，GhostCut 会以 HTTP POST 方式把结果推送到该地址。由于 GhostCut 大部分视频和图片处理功能都是异步任务，生产接入推荐优先使用 `callback` 接收结果，轮询用于主动查询、补偿扫描和兜底确认。

接入建议：

- 回调地址应可被 GhostCut 服务端直接访问，不应依赖浏览器登录态或内网访问。
- 回调处理应尽量快速完成。复杂业务逻辑建议先验签、去重、落库或入队，再异步处理。
- 即使使用回调，也建议保留轮询或补偿扫描能力，用于处理网络故障、服务重启或业务系统短暂不可用。
- 如果同一任务被重新合成或重试成功，GhostCut 可能再次触发回调；当视频内容变化时，结果 URL 也可能变化。

## 回调格式

回调请求规则：

| 项目 | 说明 |
| --- | --- |
| 请求方法 | `POST` |
| 请求体 | JSON |
| 视频回调体 | 通常与 `/work/status` 响应中的 `body.content[]` 单项一致，不包含外层 `code`、`msg` 包装。 |
| 图片回调体 | 以图片查询接口返回的任务结果结构为准，不应假设存在视频任务的 `body.content[]` 外层结构。 |
| 成功响应 | 接入方返回 HTTP `200` 且响应内容非空；否则 GhostCut 会视为回调失败。 |

视频任务成功回调示例：

```json
{
  "id": 488026661,
  "idProject": 230953994,
  "url": "https://example.com/source.mp4",
  "processStatus": 1,
  "processStatusEnum": {
    "code": 1,
    "description": "成功"
  },
  "processProgress": 100.0,
  "paidPoint": 1.0,
  "duration": 12.0,
  "sourceLang": "zh",
  "lang": "th",
  "videoUrl": "https://example.com/result.mp4",
  "srcSrtUrl": "https://example.com/source.srt",
  "tgtSrtUrl": "https://example.com/target.srt",
  "errorDetail": ""
}
```

视频任务失败回调示例：

```json
{
  "id": 480000000,
  "idProject": 22000000,
  "url": "https://example.com/source.mp4",
  "processStatus": 3,
  "processStatusEnum": {
    "code": 3,
    "description": "下载失败"
  },
  "processProgress": 100.0,
  "paidPoint": 0.0,
  "srcSrtUrl": "",
  "tgtSrtUrl": "",
  "errorDetail": ""
}
```

不同任务返回字段会有差异。视频类处理通常读取 `videoUrl`，OCR/ASR 字幕提取通常读取 `srcSrtUrl` / `tgtSrtUrl`，图片处理读取 `result.output_url` 或 `result.inpaint_url`。

## 回调验签

GhostCut 发起回调时，会在 HTTP Header 中附加签名：

```http
Callback-Sign: 86376328b7a9dce9e5b1691aa660a8e0
```

验签算法与 API 请求的 `AppSign` 规则一致，但签名输入必须使用收到的原始 HTTP Request Body：

```text
body_md5hex = md5(raw_request_body).hexdigest()
Callback-Sign = md5(body_md5hex + AppSecret).hexdigest()
```

注意事项：

- 必须使用原始请求体字节计算签名，不要先解析 JSON 再重新序列化。
- 将计算结果与 Header 中的 `Callback-Sign` 做严格比对。
- 验签失败时，不应执行业务逻辑。
- 强烈建议生产环境开启验签，防止恶意伪造回调。

## Python 回调验签示例

```python
import hashlib
import hmac


def make_callback_sign(raw_body: bytes, app_secret: str) -> str:
    body_md5hex = hashlib.md5(raw_body).hexdigest()
    return hashlib.md5((body_md5hex + app_secret).encode("utf-8")).hexdigest()


def verify_callback_sign(raw_body: bytes, callback_sign: str, app_secret: str) -> bool:
    expected = make_callback_sign(raw_body, app_secret)
    return hmac.compare_digest(expected, callback_sign or "")
```

Flask 接收回调示例：

```python
import hashlib
import hmac

from flask import Flask, request

app = Flask(__name__)
APP_SECRET = "your_app_secret"


def make_callback_sign(raw_body: bytes, app_secret: str) -> str:
    body_md5hex = hashlib.md5(raw_body).hexdigest()
    return hashlib.md5((body_md5hex + app_secret).encode("utf-8")).hexdigest()


def verify_callback_sign(raw_body: bytes, callback_sign: str, app_secret: str) -> bool:
    expected = make_callback_sign(raw_body, app_secret)
    return hmac.compare_digest(expected, callback_sign or "")


@app.post("/ghostcut/callback")
def ghostcut_callback():
    raw_body = request.get_data()
    callback_sign = request.headers.get("Callback-Sign", "")

    if not verify_callback_sign(raw_body, callback_sign, APP_SECRET):
        return "invalid sign", 403

    payload = request.get_json(force=True)
    work_id = str(payload.get("id") or payload.get("task_id") or "")
    status = payload.get("processStatus", payload.get("status"))

    # 这里应按 work_id 做幂等落库或入队，避免重复回调触发重复业务动作。
    print({"work_id": work_id, "status": status})

    return "ok", 200
```

## 重试机制

如果接入方没有按要求返回成功响应，GhostCut 会把本次回调视为失败。系统会每 30 分钟自动对 24 小时内创建且回调失败的作品再次尝试回调。

接入方应确保：

- 回调 URL 长期可用。
- 回调服务能在短时间内返回 HTTP `200` 和非空内容。
- 业务系统异常时不要误返回成功，否则 GhostCut 不会继续重试。
- 部分失败作品可通过对应 API 重试，或微调信息后重新合成；成功合成后仍会触发回调。

## 幂等性建议

由于网络抖动、服务超时或 GhostCut 自动重试，同一作品可能收到多次相同或相近回调。接入方应按业务主键做幂等处理：

- 普通视频任务优先使用 `id` 作为作品 ID 去重。
- 图片任务使用图片任务 ID 去重。
- 译制出海批量任务应结合任务 ID、作品 ID 和业务侧视频 ID 建立映射。
- 对同一作品的重复回调，不要重复扣费、重复发通知或重复创建业务记录。
- 如果重新合成导致结果 URL 变化，应按业务规则更新结果记录，而不是简单忽略所有后续成功回调。

## Agent 决策规则

- 用户提到异步任务、轮询、`callback`、回调验签、`Callback-Sign`、重试或幂等时，先读本文。
- 创建任务接口返回成功后，不要把外层 `code=1000` 或 `code=200` 当作最终处理成功。
- 普通视频任务查询结果优先用 [视频任务状态查询](./11-work-status-query.md)，并按 [视频处理状态枚举](./14-video-process-status.md) 判断 `processStatus`。
- 图片任务查询结果按 [AI 图片处理](./81-image-processing.md) 读取 `status` 和 `result`。
- 译制出海任务先查 [译制出海任务查询](./53-series-edit-task-list.md)，需要作品详情时再查 `/work/status`。
- 生成回调接收代码时，必须使用原始 HTTP Body 计算 `Callback-Sign`，不要用重新序列化后的 JSON。
- 生产集成推荐优先设计 `callback`、幂等落库和补偿轮询，避免只依赖单次网络推送；补偿轮询的初始间隔建议为 300 秒。

## 相关文档

- [API 总览](./00-api-overview.md)：查看公共调用流程和文档路由。
- [API 凭证与签名](./02-auth-and-sign.md)：查看 API 请求签名规则；回调验签使用同类规则但必须基于原始回调请求体。
- [视频任务状态查询](./11-work-status-query.md)：查询 `/work/status` 并读取视频处理结果。
- [视频处理状态枚举](./14-video-process-status.md)：查看 `processStatus` 状态值、错误码和排查建议。
- [AI 图片处理](./81-image-processing.md)：查看图片处理创建、查询和结果读取方式。
- [译制出海任务查询](./53-series-edit-task-list.md)：查询译制出海任务列表和处理进度。
