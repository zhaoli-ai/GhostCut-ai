> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 为视频压制字幕

> 鬼手剪辑 API 可用于创建视频字幕压制任务，并通过作品 ID 轮询处理状态，最终获取处理后的视频下载地址。

## 调用流程

一次完整的压制字幕处理流程包含以下步骤：

1. **准备视频资源**
   如果你的视频已经存储在云上，并且可以通过 URL 访问，可跳过这一步。如果只有本地视频文件，可以调用[文件上传 API](./10-file-upload.md)上传视频，获取 URL。

2. **创建字幕压制任务**
   调用 `/v-w-c/gateway/ve/work/free`，传入待处理视频 URL、字幕文件 URL 以及字幕压制参数。接口返回成功后，从 `body.dataList[0].id` 中获取作品 ID。

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

### 2. 创建字幕压制任务

调用 `/v-w-c/gateway/ve/work/free` 创建任务。`urls` 为待处理视频地址列表。

```python
task = api_post("/v-w-c/gateway/ve/work/free", {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "sourceLang": "zh",
    "lang": "en",
    "needWanyin": 1,
    "wyTaskType": "NO_TTS",
    "wyNeedText": 1,
    "removeBgAudio": 0,
    "wyVoiceParam": '{"font_param":{"style":"tpl-31-1-T","font_size":32,"position":0.8}}',
    "extraOptions": '{"customer_input_srt":{"source":"https://.../source.srt","translation":"https://.../trans.srt"}}'
})

work_id = task["body"]["dataList"][0]["id"]
print(f"任务创建成功，Work ID: {work_id}")
```

常用参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `urls` | `string[]` | 是 | 待处理视频 URL 列表。若视频在本地，应先通过文件上传接口拿到临时 URL。 |
| `sourceLang` | `string` | 是 | 源语言，填写视频原语种代码，例如 `zh`。 |
| `lang` | `string` | 是 | 目标语言。即使已经通过文件提供译文字幕，也必须传入译文对应的语种代码，例如英文译文传 `en`。 |
| `needWanyin` | `number` | 是 | 语音模块开关，字幕压制场景固定传 `1`。 |
| `wyTaskType` | `string` | 是 | 任务类型，固定传 `NO_TTS`，表示不生成 AI 配音，结果视频使用原视频声音。 |
| `wyNeedText` | `number` | 是 | 字幕展示开关，固定传 `1`，表示开启画面字幕渲染。 |
| `removeBgAudio` | `number` | 否 | 原声音处理策略。`0`：保留原声及背景音；`1`：全局静音；`2`：仅去除音乐旋律，保留人声和效果音。 |
| `wyVoiceParam` | `string` | 是 | JSON 字符串，配置压制到画面上的字幕样式、字号和位置。 |
| `extraOptions` | `string` | 是 | JSON 字符串，配置自定义字幕文件 URL。 |

#### `wyVoiceParam` 字幕样式配置

`wyVoiceParam` 必须以 JSON 字符串形式传入，常用结构如下：

```json
{
  "font_param": {
    "style": "tpl-31-1-T",
    "font_size": 32,
    "position": 0.8
  }
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `font_param.style` | `string` | 字幕样式 code，例如 `tpl-31-1-T`。 |
| `font_param.font_size` | `number` | 字幕字号，推荐范围 `30` 到 `50`，基于 720p 基准等比缩放。 |
| `font_param.position` | `number` | 字幕在 Y 轴的相对位置，范围 `0` 到 `1`，推荐下沉到 `0.8`。 |

Python 中建议先构造对象，再用 `json.dumps(..., ensure_ascii=False, separators=(",", ":"))` 转成字符串，避免手写 JSON 字符串时漏转义。

#### `extraOptions` 外挂字幕文件配置

`extraOptions` 必须以 JSON 字符串形式传入，用来指定 SRT 文件 URL：

```json
{
  "customer_input_srt": {
    "source": "https://example.com/source.srt",
    "translation": "https://example.com/trans.srt"
  }
}
```

字幕文件覆盖逻辑：

| 传入方式 | 系统行为 |
| --- | --- |
| 只传 `source`，不传 `translation` | 系统会根据 `sourceLang` 和 `lang` 执行 AI 翻译，并将译文压制进视频。 |
| 同时传 `source` 和 `translation` | 系统不会执行翻译，直接使用 `translation` 中的台词压制进画面。两份字幕的句子数量必须一一对应。 |
| 只有译文字幕，没有原文字幕 | 将译文字幕 URL 填入 `source` 字段，同时 `lang` 仍填写该译文对应的语种代码。 |

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


wy_voice_param = {
    "font_param": {
        "style": "tpl-31-1-T",
        "font_size": 32,
        "position": 0.8,
    }
}

extra_options = {
    "customer_input_srt": {
        "source": "https://example.com/source.srt",
        "translation": "https://example.com/trans.srt",
    }
}


# 1. 创建字幕压制任务
task_payload = {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "sourceLang": "zh",
    "lang": "en",
    "needWanyin": 1,
    "wyTaskType": "NO_TTS",
    "wyNeedText": 1,
    "removeBgAudio": 0,
    "wyVoiceParam": json.dumps(wy_voice_param, ensure_ascii=False, separators=(",", ":")),
    "extraOptions": json.dumps(extra_options, ensure_ascii=False, separators=(",", ":")),
}

task = api_post("/v-w-c/gateway/ve/work/free", task_payload)

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
- [文件上传](./10-file-upload.md)：本地视频或本地 SRT 需要先上传并获得临时 URL。
- [字幕样式和字体配置补充](./26-subtitle-style-and-fonts.md)：进一步配置 `wyVoiceParam.font_param`。
- [视频去字幕](./21-erase-video-subtitle.md)：如果原视频已有硬字幕，可先擦除再压制新字幕。
- [视频任务状态查询](./11-work-status-query.md)：查询作品处理状态并读取 `videoUrl`。
- [视频处理状态枚举](./14-video-process-status.md)：根据 `processStatus` 判断是否成功、继续轮询或失败。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试和幂等规则。
- 鬼手剪辑 API 域名：`https://api.zhaoli.com`
