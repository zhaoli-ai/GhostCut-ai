> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 译制出海音频分离

> 音频分离用于在译制出海项目中去除背景音乐，处理结果是去 BGM 后的视频。当前已确认任务参数为 `removeBgAudio=2`。可基于原视频，也可基于字幕擦除后的结果视频。

## 接口信息

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/edit/task/audio/separate
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

接口路径：

```text
gateway/ve/series/edit/task/audio/separate
```

## 最小可用请求检查清单

| 检查项 | 要求 |
| --- | --- |
| 项目和视频 | 已准备 `idSeries` 和 `items[].idMaterialVideo`，且视频素材已满足 `downloadStatus=1`、`processStatus=1`。 |
| 音频分离参数 | 固定传 `wyTaskType=NO_TTS`、`removeBgAudio=2`、`wyNeedText=0`。 |
| 字幕和音色 | 本任务不需要字幕输入，不需要 `font_param`，也不需要 `character_voices[]`。 |
| 基于擦除后视频 | 如果要基于字幕擦除后的作品分离音频，`workDto.materialWorkIds` 必须来自 `/work/status.body.content[].id`。 |
| 结果查询 | 提交后先查 [任务查询](./42-series-edit-task-list.md)，需要作品 ID 或播放地址时再查 [视频任务状态查询](./11-work-status-query.md)。 |

## 原视频音频分离

本任务的处理结果是去 BGM 后的视频。提交后通过 [任务查询](./42-series-edit-task-list.md) 查看任务状态和处理结果。

关键参数：

| 字段 | 位置 | 值 |
| --- | --- | --- |
| `needWanyin` | `videoEditParamsDto` | `1` |
| `wyTaskType` | `videoEditParamsDto` | `NO_TTS` |
| `removeBgAudio` | `videoEditParamsDto` | `2` |
| `wyNeedText` | `videoEditParamsDto` | `0` |

请求示例：

```json
{
  "idSeries": 10001,
  "projectName": "demo.mp4",
  "callback": "https://example.com/callback",
  "sourceLang": "zh",
  "lang": "zh",
  "items": [
    {
      "idMaterialVideo": 30001,
      "workDto": {
        "idSeries": 10001,
        "resolution": "1080p",
        "workName": "demo.mp4",
        "duration": 33.43,
        "fileSize": 3521
      },
      "videoEditParamsDto": {
        "type": "WORK",
        "needWanyin": 1,
        "wyTaskType": "NO_TTS",
        "removeBgAudio": 2,
        "wyNeedText": 0
      }
    }
  ]
}
```

Python 调用示例：

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
    data = response.json()
    if data.get("code") not in (1000, 200):
        raise RuntimeError(f"GhostCut API failed: {data}")
    return data


payload = {
    "idSeries": 10001,
    "projectName": "demo.mp4",
    "callback": "https://example.com/callback",
    "sourceLang": "zh",
    "lang": "zh",
    "items": [
        {
            "idMaterialVideo": 30001,
            "workDto": {
                "idSeries": 10001,
                "resolution": "1080p",
                "workName": "demo.mp4",
                "duration": 33.43,
                "fileSize": 3521
            },
            "videoEditParamsDto": {
                "type": "WORK",
                "needWanyin": 1,
                "wyTaskType": "NO_TTS",
                "removeBgAudio": 2,
                "wyNeedText": 0
            }
        }
    ]
}

result = api_post(
    "/v-w-c/gateway/ve/series/edit/task/audio/separate",
    payload,
)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## 去文字后视频音频分离

如果音频分离要基于字幕擦除后的结果视频，在原视频音频分离请求基础上，在 `workDto` 中增加 `materialWorkIds`：

```json
{
  "workDto": {
    "materialWorkIds": "50001"
  }
}
```

`materialWorkIds` 用于复用已有作品结果，不是视频素材 ID 或字幕擦除任务 ID。先通过 [任务查询](./42-series-edit-task-list.md) 的 `task/list` 查询前一步任务结果，找到对应的最新字幕擦除任务，读取 `body[].id` 作为任务 ID；再按[视频任务状态查询](./11-work-status-query.md)的方式调用 `/work/status` 查询该任务下的作品详情，从响应的 `body.content[].id` 读取作品 ID，并填入 `workDto.materialWorkIds`。

## 相关文档

- [译制出海剪辑 API 总览](./40-series-overview.md)：查看模块流程和任务选择规则。
- [通用任务结构](./41-series-edit-common-task-structure.md)：查看 `workDto`、`videoEditParamsDto` 和 Python 提交通用模板。
- [字幕擦除](./44-series-subtitle-inpaint.md)：先擦除字幕，再基于结果视频分离音频。
- [任务查询](./42-series-edit-task-list.md)：提交后查询任务处理进度。
- [项目与视频素材](./49-series-project-and-video-materials.md)：确认素材准备状态。

## Agent 决策规则

- 用户要“分离背景音乐”“去掉 BGM”或“生成去 BGM 后的视频”时，用本接口。
- 音频分离固定传 `removeBgAudio=2`。
- 本任务不需要字幕文本，传 `wyNeedText=0`。
- 如果要基于去字后结果处理，必须传 `workDto.materialWorkIds`；取值来自 `/work/status` 的 `body.content[].id`。
- 不要用 `idMaterialVideo` 直接代替 `materialWorkIds`。
