> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 视频去字幕

> 鬼手剪辑 API 可用于创建视频字幕擦除任务，并通过作品 ID 轮询处理状态，最终获取处理后的视频下载地址。

## 调用流程

一次完整的去文字处理流程包含以下步骤：

1. **准备视频资源**
   如果你的视频存储在云上，可以通过链接访问并下载可以跳过这一步。如果只有本地的视频文件，可以调用[文件上传 API](./10-file-upload.md)上传视频，获取 URL。

2. **创建去文字任务**
   调用 `/v-w-c/gateway/ve/work/free`，传入待处理视频 URL 以及去文字参数。接口返回成功后，从 `body.dataList[0].id` 中获取作品ID。

3. **查询任务状态**
   按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`，传入作品 ID 列表 `idWorks`。处理成功后，响应中会返回 `processStatus` 和 `videoUrl`。

4. **下载处理后的视频**
   当 `processStatus` = `1` 时，表示任务处理成功，可以使用返回的 `videoUrl` 下载结果视频。
   当 `processStatus` < `1` 时，表示任务处理尚未完成。
   当 `processStatus` > `1` 时，表示任务处理失败。

## 认证

鬼手剪辑 API 使用 `AppKey` + `AppSign` 进行鉴权。`AppSign` 的生成规则为双重 MD5：

1. 将请求参数序列化为 JSON 字符串。
2. 对 JSON 字符串做一次 MD5，得到 `body_md5hex`。
3. 将 `body_md5hex + AppSecret` 拼接后再次做 MD5，得到最终的 `AppSign`。

Python 示例：

```python
import hashlib
import json

APP_SECRET = "your_app_secret"

payload = {
    "idWorks": ["521461135"]
}

body_str = json.dumps(payload, ensure_ascii=False)
body_md5hex = hashlib.md5(body_str.encode("utf-8")).hexdigest()
app_sign = hashlib.md5((body_md5hex + APP_SECRET).encode("utf-8")).hexdigest()

print(app_sign)
```

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

### 2. 创建去文字任务

调用 `/v-w-c/gateway/ve/work/free` 创建任务。`urls` 为待处理视频地址列表。

```python
task = api_post("/v-w-c/gateway/ve/work/free", {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "needChineseOcclude": 1,
    "videoInpaintLang": "zh",
})

work_id = task["body"]["dataList"][0]["id"]
print(f"任务创建成功，Work ID: {work_id}")
```

常用参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `urls` | `string[]` | 待处理的视频 URL 列表 |
| `needChineseOcclude` | `number` | 必传，视频擦除功能模式，1：全屏自动擦除（仅支持基础模型） 2：按照 videoInpaintMasks 指定擦除区域（支持多种模型） |
| `videoInpaintLang` | `string` | 必传，需要去除的文字语言。目前支持 all, zh, en, ja, ko, ar。 |
| `videoInpaintMasks` | `string` | JSON 字符串形式的视频区域框配置。`needChineseOcclude=2` 时必传，使用方式参考[字幕 mask 补充说明](./22-inpaint-masks-supplement.md)。 |
| `extraOptions` | `string` | (JSON字符串) 擦除模型。结构如下，{"extra_inpaint_config": {"model": "advanced_lite"}}|

### 3. 查询任务状态

创建任务拿到 `work_id` 后，按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`。本功能在 `processStatus == 1` 时读取 `videoUrl`；如果 `processStatus > 1`，按[视频处理状态枚举](./14-video-process-status.md)排查失败原因。生产接入推荐使用 `callback` 接收结果，轮询作为查询和补偿兜底，规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。

## 完整示例

以下示例展示了从创建任务到轮询获取结果视频的完整流程。

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


# 1. 创建去文字任务
task = api_post("/v-w-c/gateway/ve/work/free", {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "needChineseOcclude": 1,
    "videoInpaintLang": "zh",
})

work_id = task["body"]["dataList"][0]["id"]
print(f"任务创建成功，Work ID: {work_id}")


# 2. 轮询任务结果；生产接入推荐 callback，补偿轮询初始间隔建议 300 秒
while True:
    result = api_post("/v-w-c/gateway/ve/work/status", {
        "idWorks": [work_id]
    })

    content = result["body"]["content"][0]
    status = content["processStatus"]

    if status == 1:
        print(f"处理成功，视频下载链接: {content['videoUrl']}")
        break

    if status > 1:
        print(f"处理失败: {content.get('errorDetail', '未知错误')}")
        break

    print("处理中，等待 5 分钟后重试...")
    time.sleep(300)
```

## 单独查询任务状态

如果你已经有作品 ID，可以直接按[视频任务状态查询](./11-work-status-query.md)查询任务状态。本功能成功后读取 `body.content[].videoUrl`。

## 响应示例

创建任务后，接口会返回作品 ID。实际字段以线上接口返回为准：

```json
{
  "body": {
    "dataList": [
      {
        "id": "521461135"
      }
    ]
  }
}
```

查询任务成功时，响应中会包含处理后的视频地址：

```json
{
  "body": {
    "content": [
      {
        "processStatus": 1,
        "videoUrl": "https://example.com/result.mp4"
      }
    ]
  }
}
```

## 推荐阅读

- [API 总览](./00-api-overview.md)：查看功能选择入口和主要调用流程。
- [API 凭证与签名](./02-auth-and-sign.md)：查看公共签名规则和常见鉴权错误。
- [文件上传](./10-file-upload.md)：本地视频需要先上传并获得临时 URL。
- [字幕 mask 补充说明](./22-inpaint-masks-supplement.md)：查看去字幕模型版本、遮罩框类型和相对坐标规则。
- [不同功能支持的语言列表](./13-language-support.md)：确认 `videoInpaintLang` 可用值。
- [视频任务状态查询](./11-work-status-query.md)：查询作品处理状态并读取 `videoUrl`。
- [视频处理状态枚举](./14-video-process-status.md)：根据 `processStatus` 判断是否成功、继续轮询或失败。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试和幂等规则。
- 鬼手剪辑 API 域名：`https://api.zhaoli.com`
