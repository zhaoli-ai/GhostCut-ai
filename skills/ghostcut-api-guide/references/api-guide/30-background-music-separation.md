# 背景音乐去除/分离

> 鬼手剪辑 API 可用于精准提取并去除原视频背景音中的音乐旋律部分，同时保留视频中的人声和其他环境效果音。

## 调用流程

一次完整的背景音乐去除/分离流程包含以下步骤：

1. **准备视频资源**
   视频 URL、格式和本地上传要求见[素材 URL 与格式要求](./03-media-requirements.md)；本地视频先按[文件上传](./10-file-upload.md)获取临时 URL。

2. **创建背景音乐去除/分离任务**
   调用 `/v-w-c/gateway/ve/work/free`，传入待处理视频 URL 以及音频处理参数。接口返回成功后，从 `body.dataList[0].id` 中获取作品 ID。

3. **查询任务状态**
   按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`，传入作品 ID 列表 `idWorks`。处理成功后，响应中会返回 `processStatus` 和结果视频 URL。

4. **下载处理后的视频**
   当 `processStatus` = `1` 时，表示任务处理成功，可以使用返回的视频 URL 下载结果。结果视频会去除原背景音乐旋律，并保留人声和环境效果音。

## 认证

本接口使用 `AppKey` + `AppSign` 鉴权；规则见[API 凭证与签名](./02-auth-and-sign.md)。

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

### 2. 创建背景音乐去除/分离任务

调用 `/v-w-c/gateway/ve/work/free` 创建任务。核心触发参数是 `removeBgAudio=2`。

```python
task_payload = {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "needWanyin": 1,
    "wyTaskType": "NO_TTS",
    "wyNeedText": 0,
    "removeBgAudio": 2,
}

task = api_post("/v-w-c/gateway/ve/work/free", task_payload)

work_id = task["body"]["dataList"][0]["id"]
print(f"任务创建成功，Work ID: {work_id}")
```

常用参数：

| 参数 | 类型 | 必填 | 固定传值 | 说明 |
| --- | --- | --- | --- | --- |
| `urls` | `string[]` | 是 | - | 待处理视频 URL 列表。若视频在本地，应先通过文件上传接口拿到临时 URL。 |
| `needWanyin` | `number` | 是 | `1` | 语音模块开关，必须传 `1`。 |
| `wyTaskType` | `string` | 是 | `NO_TTS` | 声明不重新配音，保留原声轨道。 |
| `wyNeedText` | `number` | 是 | `0` | 关闭字幕展示，表示纯处理音频。 |
| `removeBgAudio` | `number` | 是 | `2` | 背景音乐去除/分离触发器。系统会去除原始背景音中的音乐旋律部分，仅保留人声和效果音。 |

### 3. 查询任务状态

创建任务拿到 `work_id` 后，按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`。本功能在 `processStatus == 1` 时读取 `videoUrl`；如果 `processStatus > 1`，按[视频处理状态枚举](./14-video-process-status.md)排查失败原因。生产接入推荐使用 `callback` 接收结果，轮询作为查询和补偿兜底，规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。

## 完整示例

以下示例展示了从创建背景音乐去除/分离任务到轮询获取结果视频的完整流程。

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
    "wyTaskType": "NO_TTS",
    "wyNeedText": 0,
    "removeBgAudio": 2,
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
        print(f"处理成功，视频下载链接: {content.get('videoUrl')}")
        break

    if status > 1:
        print(f"处理失败: {content.get('errorDetail', '未知错误')}")
        break

    print("处理中，等待 5 分钟后重试...")
    time.sleep(300)
```

## Agent 决策规则

- 用户要去除视频背景音乐、分离 BGM、保留人声和环境音时，使用本功能。
- 本功能为异步任务；生产接入推荐使用 `callback` 接收结果，轮询作为查询和补偿兜底。
- 固定传 `needWanyin=1`、`wyTaskType=NO_TTS`、`wyNeedText=0`、`removeBgAudio=2`。
- 本功能会输出处理后的视频结果；查询结果时优先读取 `videoUrl`。
- 如果用户只想全局静音，不是分离背景音乐，不应使用 `removeBgAudio=2`；全局静音对应 `removeBgAudio=1`。

## 相关文档

- [API 总览](./00-api-overview.md)：查看功能选择入口和主要调用流程。
- [API 凭证与签名](./02-auth-and-sign.md)：查看公共签名规则和常见鉴权错误。
- [文件上传](./10-file-upload.md)：本地视频需要先上传并获得临时 URL。
- [视频语音翻译与重新配音](./31-video-voice-translation.md)：如果用户还需要翻译、重新配音或压制译后字幕，使用视频语音翻译能力。
- [视频任务状态查询](./11-work-status-query.md)：查询作品处理状态并读取 `videoUrl`。
- [视频处理状态枚举](./14-video-process-status.md)：根据 `processStatus` 判断是否成功、继续轮询或失败。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试和幂等规则。
