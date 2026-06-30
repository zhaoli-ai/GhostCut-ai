> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# ASR 提取视频字幕

> 鬼手剪辑 API 可通过分析视频音频轨道进行语音识别 ASR，提取台词并生成 SRT 字幕文件。该功能仅执行字幕抽取，不执行配音，也不改变视频。

## 调用流程

一次完整的 ASR 字幕提取流程包含以下步骤：

1. **准备视频资源**
   如果视频已经可以通过公网 URL 访问，可直接使用该 URL。如果只有本地视频文件，先调用[文件上传 API](./10-file-upload.md)上传视频，获取临时 URL。

2. **创建 ASR 字幕提取任务**
   调用 `/v-w-c/gateway/ve/work/free`，传入视频 URL、音频源语言以及 ASR 固定参数。接口返回成功后，从 `body.dataList[0].id` 中获取作品 ID。

3. **查询任务状态**
   按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`，传入作品 ID 列表 `idWorks`。处理成功后，响应中会返回 `srcSrtUrl` 和 `tgtSrtUrl`。

4. **下载 SRT 文件**
   当 `processStatus` = `1` 时，表示任务处理成功，可以使用返回的 SRT URL 下载字幕文件。

## 认证

鬼手剪辑 API 使用 `AppKey` + `AppSign` 进行鉴权。`AppSign` 的生成规则为双重 MD5：

1. 将请求参数序列化为 JSON 字符串。
2. 对 JSON 字符串做一次 MD5，得到 `body_md5hex`。
3. 将 `body_md5hex + AppSecret` 拼接后再次做 MD5，得到最终的 `AppSign`。

请求头需要包含：

```http
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

> 注意：用于签名的 JSON 字符串需要和实际发送的请求体保持一致，否则签名会校验失败。

## 调用示例

### 1. 封装请求方法

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
```

### 2. 创建 ASR 字幕提取任务

调用 `/v-w-c/gateway/ve/work/free` 创建任务。ASR 提取逻辑比较简单，通过固定参数组合触发：

```python
task_payload = {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "needWanyin": 1,
    "wyTaskType": "ONLY_ASR",
    "wyNeedText": 0,
    "sourceLang": "zh",
}

task = api_post("/v-w-c/gateway/ve/work/free", task_payload)

work_id = task["body"]["dataList"][0]["id"]
print(f"任务创建成功，Work ID: {work_id}")
```

常用参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `urls` | `string[]` | 是 | 待处理视频 URL 列表。若视频在本地，应先通过文件上传接口拿到临时 URL。 |
| `needWanyin` | `number` | 是 | 语音模块开关，固定传 `1`。 |
| `wyTaskType` | `string` | 是 | 任务类型，固定传 `ONLY_ASR`，表示仅执行 ASR 抽取字幕，不执行配音，不改变视频。 |
| `wyNeedText` | `number` | 是 | 新字幕展示开关，固定传 `0`。 |
| `sourceLang` | `string` | 是 | 音频源语言。可用语种见[不同功能支持的语言列表](./13-language-support.md)中的 ASR 提取字幕。 |

### 3. 查询任务状态

创建任务拿到 `work_id` 后，按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`。本功能在 `processStatus == 1` 时读取 `srcSrtUrl` / `tgtSrtUrl`；如果 `processStatus > 1`，按[视频处理状态枚举](./14-video-process-status.md)排查失败原因。生产接入推荐使用 `callback` 接收结果，轮询作为查询和补偿兜底，规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。

## 完整示例

以下示例展示了从创建 ASR 字幕提取任务到轮询获取 SRT 结果的完整流程。

```python
import hashlib
import json
import time
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


task = api_post("/v-w-c/gateway/ve/work/free", {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "needWanyin": 1,
    "wyTaskType": "ONLY_ASR",
    "wyNeedText": 0,
    "sourceLang": "zh",
})

work_id = task["body"]["dataList"][0]["id"]
print(f"任务创建成功，Work ID: {work_id}")

while True:
    result = api_post("/v-w-c/gateway/ve/work/status", {
        "idWorks": [work_id]
    })

    content = result["body"]["content"][0]
    status = content["processStatus"]

    if status == 1:
        print(f"源语言 SRT: {content.get('srcSrtUrl')}")
        print(f"目标语言 SRT: {content.get('tgtSrtUrl')}")
        break

    if status > 1:
        print(f"处理失败: {content.get('errorDetail', '未知错误')}")
        break

    print("处理中，等待 5 分钟后重试...")
    time.sleep(300)
```

## Agent 决策规则

- 用户要从音频中的人声转写字幕时，使用 ASR 字幕提取。
- 用户要从视频画面里已经存在的硬字幕提取 SRT 时，使用 [OCR 提取视频字幕](./24-ocr-subtitle-extraction.md)。
- 本功能为异步任务；生产接入推荐使用 `callback` 接收结果，轮询作为查询和补偿兜底。
- ASR 提取固定传 `needWanyin=1`、`wyTaskType=ONLY_ASR`、`wyNeedText=0`。
- ASR 提取只产出 SRT 文件，不产出处理后视频；查询结果时读取 `srcSrtUrl` / `tgtSrtUrl`，不要等待 `videoUrl`。

## 相关文档

- [API 总览](./00-api-overview.md)：查看功能选择入口和主要调用流程。
- [API 凭证与签名](./02-auth-and-sign.md)：查看公共签名规则和常见鉴权错误。
- [文件上传](./10-file-upload.md)：本地视频需要先上传并获得临时 URL。
- [OCR 提取视频字幕](./24-ocr-subtitle-extraction.md)：画面中已有硬字幕时，优先使用 OCR。
- [不同功能支持的语言列表](./13-language-support.md)：确认 `sourceLang` 在 ASR 场景下的可用值。
- [视频任务状态查询](./11-work-status-query.md)：查询作品处理状态并读取 `srcSrtUrl` / `tgtSrtUrl`。
- [视频处理状态枚举](./14-video-process-status.md)：根据 `processStatus` 判断是否成功、继续轮询或失败。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试和幂等规则。
