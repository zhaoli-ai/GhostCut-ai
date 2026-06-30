> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# OCR 提取视频字幕

> 鬼手剪辑 API 可通过图像 OCR 识别视频画面中的硬字幕，并生成 SRT 字幕文件。该功能仅输出 SRT，不生成新的视频结果。

## 调用流程

一次完整的 OCR 字幕提取流程包含以下步骤：

1. **准备视频资源**
   如果视频已经可以通过公网 URL 访问，可直接使用该 URL。如果只有本地视频文件，先调用[文件上传 API](./10-file-upload.md)上传视频，获取临时 URL。

2. **创建 OCR 字幕提取任务**
   调用 `/v-w-c/gateway/ve/work/free`，传入视频 URL、源语言、目标语言以及 OCR 识别范围框。接口返回成功后，从 `body.dataList[0].id` 中获取作品 ID。

3. **查询任务状态**
   按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`，传入作品 ID 列表 `idWorks`。处理成功后，响应中会返回 `srcSrtUrl` 和 `tgtSrtUrl`。

4. **下载 SRT 文件**
   当 `processStatus` = `1` 时，表示任务处理成功，可以使用 `srcSrtUrl` 下载源语言 SRT。若发生翻译，可使用 `tgtSrtUrl` 下载目标语言 SRT。

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

### 2. 创建 OCR 字幕提取任务

调用 `/v-w-c/gateway/ve/work/free` 创建任务。`videoInpaintMasks` 是 JSON 字符串，OCR 提取模式下必须传入。

```python
video_inpaint_masks = [
    {
        "type": "remove_only_ocr",
        "start": 0,
        "end": 99999,
        "region": [
            [0, 0.56],
            [1, 0.56],
            [1, 0.76],
            [0, 0.76],
        ],
    }
]

extra_options = {
    "extra_inpaint_config": {
        "auto_correct_on": False,
        "strip_last_punct_on": False,
        "scene_filter_on": True,
    }
}

task_payload = {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "needChineseOcclude": 14,
    "videoInpaintLang": "zh",
    "lang": "zh",
    "videoInpaintMasks": json.dumps(video_inpaint_masks, ensure_ascii=False, separators=(",", ":")),
    "extraOptions": json.dumps(extra_options, ensure_ascii=False, separators=(",", ":")),
}

task = api_post("/v-w-c/gateway/ve/work/free", task_payload)

work_id = task["body"]["dataList"][0]["id"]
print(f"任务创建成功，Work ID: {work_id}")
```

常用参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `urls` | `string[]` | 是 | 待处理视频 URL 列表。若视频在本地，应先通过文件上传接口拿到临时 URL。 |
| `needChineseOcclude` | `number` | 是 | OCR 字幕提取触发器，固定传 `14`。该模式只返回 SRT 文件，不输出视频。 |
| `videoInpaintLang` | `string` | 是 | 源语言。可用语种见[不同功能支持的语言列表](./13-language-support.md)中的 OCR 提取字幕。 |
| `lang` | `string` | 是 | 目标语言。如果不需要翻译，传入与 `videoInpaintLang` 完全相同的值。 |
| `videoInpaintMasks` | `string` | 是 | JSON 字符串，OCR 识别范围框。提取模式下必填。 |
| `extraOptions` | `string` | 否 | JSON 字符串，OCR 识别调优配置。 |

#### `videoInpaintMasks` 识别范围框

OCR 提取模式下，`videoInpaintMasks` 只支持 `remove_only_ocr` 类型：

```json
[
  {
    "type": "remove_only_ocr",
    "start": 0,
    "end": 99999,
    "region": [
      [0, 0.56],
      [1, 0.56],
      [1, 0.76],
      [0, 0.76]
    ]
  }
]
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `type` | `string` | 框类型，OCR 提取模式固定传 `remove_only_ocr`。 |
| `start` | `number` | 开始时间点，单位秒。不传时默认从 `0` 开始。 |
| `end` | `number` | 结束时间点，单位秒。不传时默认到视频总时长。 |
| `to_end` | `number` | 可选，用于跳过片尾，例如 `10` 表示跳过最后 10 秒。`end` 和 `to_end` 只能二选一。 |
| `region` | `number[][]` | OCR 识别范围，相对坐标点列表。坐标规则参考[字幕 mask 补充说明](./22-inpaint-masks-supplement.md)。 |

#### `extraOptions` 识别调优配置

`extraOptions` 可用于调整 OCR 识别行为：

```json
{
  "extra_inpaint_config": {
    "auto_correct_on": false,
    "strip_last_punct_on": false,
    "scene_filter_on": true
  }
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `extra_inpaint_config.auto_correct_on` | `boolean` | 自动校准开关。默认保持 `false`；仅在识别偏差较大时开启。 |
| `extra_inpaint_config.strip_last_punct_on` | `boolean` | 是否去除字幕结尾标点符号。 |
| `extra_inpaint_config.scene_filter_on` | `boolean` | 场景文字过滤开关，默认建议 `true`。当文字阴影较大、字体过细或视频分辨率过低导致漏识别时，可关闭后重新提取。 |

### 3. 查询任务状态

创建任务拿到 `work_id` 后，按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`。本功能在 `processStatus == 1` 时读取 `srcSrtUrl` / `tgtSrtUrl`；如果 `processStatus > 1`，按[视频处理状态枚举](./14-video-process-status.md)排查失败原因。生产接入推荐使用 `callback` 接收结果，轮询作为查询和补偿兜底，规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。

## Agent 决策规则

- 用户要从视频画面里的硬字幕提取 SRT 时，优先使用 OCR 字幕提取。
- 用户要根据音频中的人声转写字幕时，使用 [ASR 提取视频字幕](./25-asr-subtitle-extraction.md)。
- 本功能为异步任务；生产接入推荐使用 `callback` 接收结果，轮询作为查询和补偿兜底。
- OCR 提取必须传 `videoInpaintMasks`，且框类型必须是 `remove_only_ocr`。
- 如果用户不需要翻译，`lang` 必须与 `videoInpaintLang` 保持一致。
- OCR 字幕提取只产出 SRT 文件，不产出处理后视频；查询结果时读取 `srcSrtUrl` / `tgtSrtUrl`，不要等待 `videoUrl`。

## 相关文档

- [API 总览](./00-api-overview.md)：查看功能选择入口和主要调用流程。
- [API 凭证与签名](./02-auth-and-sign.md)：查看公共签名规则和常见鉴权错误。
- [文件上传](./10-file-upload.md)：本地视频需要先上传并获得临时 URL。
- [字幕 mask 补充说明](./22-inpaint-masks-supplement.md)：查看 `videoInpaintMasks` 坐标、时间字段和框类型。
- [不同功能支持的语言列表](./13-language-support.md)：确认 `videoInpaintLang` 和 `lang` 的可用值。
- [视频任务状态查询](./11-work-status-query.md)：查询作品处理状态并读取 `srcSrtUrl` / `tgtSrtUrl`。
- [视频处理状态枚举](./14-video-process-status.md)：根据 `processStatus` 判断是否成功、继续轮询或失败。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试和幂等规则。
