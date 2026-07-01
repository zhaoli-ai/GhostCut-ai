# 视频基础处理

> 鬼手剪辑 API 的 `/v-w-c/gateway/ve/work/free` 是普通单视频处理工作流的核心异步网关。通过组合基础参数和画面处理参数，可创建基础剪辑、智能优化、滤镜特效、镜像、缩放、移动等视频处理任务，也可与部分擦除、翻译配音等能力组合使用。

## 调用流程

一次完整的视频基础处理流程包含以下步骤：

1. **准备视频资源**
   视频 URL、格式和本地上传要求见[素材 URL 与格式要求](./03-media-requirements.md)；本地视频先按[文件上传](./10-file-upload.md)获取临时 URL。

2. **创建视频处理任务**
   调用 `/v-w-c/gateway/ve/work/free`，传入视频 URL、基础控制参数和需要开启的画面处理参数。接口返回成功后，从 `body.dataList[0].id` 获取作品 ID。

3. **查询任务状态**
   按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`，传入作品 ID 列表 `idWorks`。处理成功后，响应中会返回 `processStatus` 和结果视频 URL。

4. **下载处理后的视频**
   当 `processStatus == 1` 时，表示任务处理成功，可以使用返回的 `videoUrl` 下载结果视频。

## 功能限制

| 限制项 | 说明 |
| --- | --- |
| 功能互斥 | 文字翻译不可与语音翻译或去文字叠加使用。 |

视频格式、URL 字符、本地文件上传和 `urls` 批量数量等通用素材约束，见[素材 URL 与格式要求](./03-media-requirements.md)。

## 认证

本接口使用 `AppKey` + `AppSign` 鉴权；规则见[API 凭证与签名](./02-auth-and-sign.md)。

## 基础请求参数

发起任何普通单视频处理任务时，都可以使用以下底层基础通信与控制参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `urls` | `string[]` | 是 | 待处理的视频 URL 数组。支持批量提交，单次请求最多不超过 20 个。 |
| `names` | `string[]` | 否 | 自定义作品名称。数组长度和顺序必须与 `urls` 严格一一对应。 |
| `resolution` | `string` | 否 | 输出视频分辨率。支持 `480p`、`720p`、`1080p`，不传则默认输出 `1080p`。 |
| `callback` | `string` | 否 | 异步回调通知地址。任务完成后，系统会向该 URL 推送 JSON 格式的结果数据；回调格式和验签见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。 |
| `uid` | `string` | 否 | 多租户或子用户标识，用于隔离不同用户的资产。不传时默认使用当前 API Key 绑定的主账户 UID。 |
| `extraOptions` | `string` | 否 | JSON 字符串，额外剪辑高级配置，用于控制视频截取、画质压缩率、外挂字幕格式或基础处理微调配置。 |

## 通用 `extraOptions`

`extraOptions` 需要先构造 JSON 对象，再使用 `json.dumps(..., separators=(",", ":"))` 转为字符串后传给接口。

```json
{
  "range": [5, 10],
  "write_options": {
    "crf": 17
  },
  "subtitle_format": ".vtt"
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `range` | `number[]` | 掐头去尾，返回指定时间范围内的视频片段，单位为秒。例如 `[5,10]` 表示截取第 5 秒到第 10 秒。 |
| `write_options.crf` | `number` | 视频编码与画质控制参数。有效范围 `10` 到 `30`，系统默认值 `17`。数值越低，压缩越少、画质越高、文件体积越大；高画质场景可传 `15` 或 `16`。 |
| `subtitle_format` | `string` | 独立字幕文件格式。支持 `.vtt`、`.ass`、`.srt`；不传默认输出 `.srt`。 |

## 视频基础处理参数

以下参数用于画面剪辑与特效包装，可按需组合使用。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `needTrim` | `number` | 否 | 智能基础优化开关。`0`：关闭；`1`：开启。开启后可涵盖颜色调整、长宽裁剪、倾斜矫正、锐化及速度等智能调整。可通过 `extraOptions.extra_trim_config` 微调。 |
| `needMask` | `number` | 否 | 特效剪辑滤镜，仅支持单选。`0`：关闭；`1`：扫光；`2`：泛光开幕；`3`：下降开幕；`4`：书单模式；`5`：溶图模式；`6`：横版视频分三屏显示；`7`：好物模式；`8`：影视模式；`9`：短剧模式；`10`：探店模式。 |
| `needMirror` | `number` | 否 | 镜像翻转开关。`0`：关闭；`1`：全局镜像；`2`：随机镜像，即在视频中随机分段，每段镜像方向随机。 |
| `needRescale` | `number` | 否 | 画面缩放开关。`0`：关闭；`1`：随机拉伸 y 轴；`2`：随机压缩 y 轴；`3`：动态缩放。 |
| `needShift` | `number` | 否 | 画面智能移动开关。`0`：关闭；`1`：开启。 |
| `extraOptions` | `string` | 否 | JSON 字符串，基础处理的高级微调配置。例如控制调色、锐化、智能裁剪片头片尾、随机加速等。 |

> 注意：当同时使用文字翻译功能时，`needMirror=2` 随机镜像不生效，将强制退化为全局镜像。

## `extra_trim_config` 微调智能基础优化

如果开启了 `needTrim=1`，且希望控制系统默认的智能基础优化细节，可在 `extraOptions` 中传入 `extra_trim_config`。

```json
{
  "extra_trim_config": {
    "adjust_color_on": true,
    "adjust_sharpness_on": true,
    "crop_trailer_on": true,
    "speedup_on": true
  }
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `adjust_color_on` | `boolean` | 智能调色开关。 |
| `adjust_sharpness_on` | `boolean` | 画面锐化增强开关。 |
| `crop_trailer_on` | `boolean` | 掐头去尾，智能裁剪多余片头片尾。 |
| `speedup_on` | `boolean` | 随机视频加速处理。 |

> 前置生效条件：`extra_trim_config` 中的所有配置项，必须在 `needTrim=1` 的前提下才会生效。若 `needTrim=0`，这些配置会被忽略。

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
    body_str = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
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

### 2. 创建视频基础处理任务

以下示例表示：对视频截取第 5 秒到第 10 秒，输出 `1080p`，开启智能基础优化、好物模式滤镜、全局镜像、动态缩放和智能移动，并微调智能基础优化细节。

```python
extra_options = {
    "range": [5, 10],
    "write_options": {
        "crf": 17,
    },
    "subtitle_format": ".srt",
    "extra_trim_config": {
        "adjust_color_on": True,
        "adjust_sharpness_on": True,
        "crop_trailer_on": True,
        "speedup_on": True,
    },
}

task_payload = {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "names": ["基础处理示例"],
    "resolution": "1080p",
    "needTrim": 1,
    "needMask": 7,
    "needMirror": 1,
    "needRescale": 3,
    "needShift": 1,
    "extraOptions": json.dumps(extra_options, ensure_ascii=False, separators=(",", ":")),
}

task = api_post("/v-w-c/gateway/ve/work/free", task_payload)

work_id = task["body"]["dataList"][0]["id"]
print(f"任务创建成功，Work ID: {work_id}")
```

### 3. 查询任务状态

创建任务拿到 `work_id` 后，按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`。本功能在 `processStatus == 1` 时读取 `videoUrl`；如果 `processStatus > 1`，按[视频处理状态枚举](./14-video-process-status.md)排查失败原因。

## 完整示例

以下示例展示了从创建视频基础处理任务到轮询获取结果视频的完整流程。

```python
import hashlib
import json
import time
import requests

APP_KEY = "your_app_key"
APP_SECRET = "your_app_secret"
BASE_URL = "https://api.zhaoli.com"


def api_post(path: str, payload: dict) -> dict:
    body_str = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
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


extra_options = {
    "range": [5, 10],
    "write_options": {
        "crf": 17,
    },
    "extra_trim_config": {
        "adjust_color_on": True,
        "adjust_sharpness_on": True,
        "crop_trailer_on": True,
        "speedup_on": True,
    },
}

task = api_post("/v-w-c/gateway/ve/work/free", {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "names": ["基础处理示例"],
    "resolution": "1080p",
    "needTrim": 1,
    "needMask": 7,
    "needMirror": 1,
    "needRescale": 3,
    "needShift": 1,
    "extraOptions": json.dumps(extra_options, ensure_ascii=False, separators=(",", ":")),
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

## Agent 决策规则

- 用户要做基础剪辑、截取视频片段、调整分辨率、智能优化、调色、锐化、裁剪片头片尾、随机加速、镜像、缩放、画面移动或添加基础滤镜特效时，使用本功能。
- 创建任务前，按[素材 URL 与格式要求](./03-media-requirements.md)检查视频格式、URL 字符、本地文件上传和 `urls` 批量数量。
- 传 `names` 时，`names` 数组长度和顺序必须与 `urls` 一一对应。
- `extraOptions` 是 JSON 字符串，不要把对象直接传给接口。
- `extra_trim_config` 只有在 `needTrim=1` 时生效。
- `needMask` 只支持单选；不要同时为同一个任务传多个滤镜编号。
- 文字翻译不可与语音翻译或去文字叠加使用；如果用户同时提出这些目标，应拆分为多个任务或提醒其功能互斥。
- 创建任务成功只表示异步任务已提交，不代表视频处理已经完成；生产接入推荐使用 `callback` 接收结果，轮询按[视频任务状态查询](./11-work-status-query.md)作为查询和补偿兜底。

## 相关文档

- [API 总览](./00-api-overview.md)：查看功能选择入口和主要调用流程。
- [API 凭证与签名](./02-auth-and-sign.md)：查看公共签名规则和鉴权错误。
- [素材 URL 与格式要求](./03-media-requirements.md)：查看视频格式、URL 字符、本地上传和批量数量要求。
- [文件上传](./10-file-upload.md)：本地视频需要先上传并获得临时 URL。
- [视频任务状态查询](./11-work-status-query.md)：查询作品处理状态并读取 `videoUrl`。
- [视频处理状态枚举](./14-video-process-status.md)：根据 `processStatus` 判断是否成功、继续轮询或失败。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试和幂等规则。
- 鬼手剪辑 API 域名：`https://api.zhaoli.com`
