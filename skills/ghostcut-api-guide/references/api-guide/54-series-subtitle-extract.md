# 译制出海字幕提取

> 字幕提取包含 ASR 和 OCR 两种模式。ASR 从音频人声中转写字幕，OCR 从视频画面中的硬字幕识别字幕。

## 接口信息

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/edit/task/subtitle/extract
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

接口路径：

```text
gateway/ve/series/edit/task/subtitle/extract
```

## 最小可用请求检查清单

| 检查项 | 要求 |
| --- | --- |
| 项目和视频 | 已准备 `idSeries` 和 `items[].idMaterialVideo`，且视频素材已满足 `downloadStatus=1`、`processStatus=1`。 |
| 提取模式 | ASR 和 OCR 二选一；ASR 用 `wyTaskType=ONLY_ASR`，OCR 用 `needChineseOcclude=14`。 |
| 语言 | ASR 传 `sourceLang` 和 `lang`；OCR 传 `videoInpaintLang`，不翻译时 `lang` 与识别语言一致。 |
| OCR 框选 | OCR 必须传 `videoInpaintMasks[]`，坐标为 `0` 到 `1` 的相对坐标。 |
| 结果获取 | 生产接入推荐通过 `callback` 接收结果；也可查 [任务查询](./53-series-edit-task-list.md)，任务成功后再查 [字幕素材管理](./61-series-subtitle-materials.md) 获取字幕素材 ID。 |

## ASR 字幕提取

ASR 适合视频里有清晰人声、需要从音频生成字幕的场景。

关键参数：

| 字段 | 位置 | 值 |
| --- | --- | --- |
| `needWanyin` | `videoEditParamsDto` | `1` |
| `wyTaskType` | `videoEditParamsDto` | `ONLY_ASR` |
| `wyNeedText` | `videoEditParamsDto` | `0` |
| `needWyEdit` | `videoEditParamsDto` | `0` |
| `sourceLang` | 顶层 / `videoEditParamsDto` | 原语种 code |
| `lang` | 顶层 / `videoEditParamsDto` | 不翻译时与 `sourceLang` 相同 |

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
        "originalDuration": 33.43,
        "fileSize": 3521,
        "extraOptions": {
          "asr_speaker_detect_on": true
        }
      },
      "videoEditParamsDto": {
        "type": "WORK",
        "needWanyin": 1,
        "wyTaskType": "ONLY_ASR",
        "sourceLang": "zh",
        "lang": "zh",
        "wyNeedText": 0,
        "needWyEdit": 0
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
                "extraOptions": {
                    "asr_speaker_detect_on": True
                }
            },
            "videoEditParamsDto": {
                "type": "WORK",
                "needWanyin": 1,
                "wyTaskType": "ONLY_ASR",
                "sourceLang": "zh",
                "lang": "zh",
                "wyNeedText": 0,
                "needWyEdit": 0
            }
        }
    ]
}

result = api_post(
    "/v-w-c/gateway/ve/series/edit/task/subtitle/extract",
    payload,
)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## OCR 字幕提取

OCR 适合视频画面中已经有硬字幕，需要识别并提取字幕的场景。

关键参数：

| 字段 | 位置 | 值 |
| --- | --- | --- |
| `needChineseOcclude` | `videoEditParamsDto` | `14` |
| `videoInpaintLang` | `videoEditParamsDto` | 画面字幕语言，例如 `zh` |
| `videoInpaintMasks` | `videoEditParamsDto` | OCR 识别区域 |
| `videoInpaintMasks[].type` | `videoEditParamsDto` | OCR 框类型。框选、坐标和时间规则与普通单视频 OCR 完全一致；当前译制出海示例使用 `trans_only_ocr`。 |

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
        "fileSize": 3521,
        "extraOptions": {
          "extra_inpaint_config": {
            "auto_correct_on": false,
            "strip_last_punct_on": false,
            "scene_filter_on": true
          }
        }
      },
      "videoEditParamsDto": {
        "type": "WORK",
        "needChineseOcclude": 14,
        "sourceLang": "zh",
        "videoInpaintLang": "zh",
        "lang": "zh",
        "videoInpaintMasks": [
          {
            "type": "trans_only_ocr",
            "start": 0,
            "end": 99999,
            "region": [[0, 0.65], [1, 0.65], [1, 1], [0, 1]]
          }
        ]
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
                "extraOptions": {
                    "extra_inpaint_config": {
                        "auto_correct_on": False,
                        "strip_last_punct_on": False,
                        "scene_filter_on": True
                    }
                }
            },
            "videoEditParamsDto": {
                "type": "WORK",
                "needChineseOcclude": 14,
                "sourceLang": "zh",
                "videoInpaintLang": "zh",
                "lang": "zh",
                "videoInpaintMasks": [
                    {
                        "type": "trans_only_ocr",
                        "start": 0,
                        "end": 99999,
                        "region": [[0, 0.65], [1, 0.65], [1, 1], [0, 1]]
                    }
                ]
            }
        }
    ]
}

result = api_post(
    "/v-w-c/gateway/ve/series/edit/task/subtitle/extract",
    payload,
)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## OCR 框选规则

译制出海 OCR 的框选规则与 [OCR 提取视频字幕](./24-ocr-subtitle-extraction.md) 和 [字幕 mask 补充说明](./22-inpaint-masks-supplement.md) 中的规则完全一致：使用相对坐标、四点矩形框和可选时间字段。差异是普通单视频接口里的 `videoInpaintMasks` 需要传 JSON 字符串，而译制出海任务示例中直接传数组对象。

`videoInpaintMasks` 对象结构：

```json
[
  {
    "type": "trans_only_ocr",
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
| `type` | `String` | OCR 识别框类型。当前译制出海示例使用 `trans_only_ocr`；框选坐标规则与普通单视频 OCR 的 `remove_only_ocr` 一致。 |
| `start` | `Number` | 框开始生效的时间点，单位秒。不传时通常表示从视频开头开始。 |
| `end` | `Number` | 框结束生效的绝对时间点，单位秒。和 `to_end` 二选一。 |
| `to_end` | `Number` | 距离视频结尾多少秒前停止生效。`to_end: 10` 表示跳过最后 10 秒。 |
| `region` | `number[][]` | 四点相对坐标，按左上、右上、右下、左下顺时针排列。 |

坐标规则：

- 原点在视频左上角。
- `x` 从左到右递增，范围 `0` 到 `1`。
- `y` 从上到下递增，范围 `0` 到 `1`。
- `region` 不使用像素坐标；像素坐标需换算为 `relative_x = pixel_x / video_width`、`relative_y = pixel_y / video_height`。
- 点顺序固定为左上、右上、右下、左下。

常用参考框：

| 场景 | `region` |
| --- | --- |
| 竖版 9:16 下方字幕区 | `[[0,0.56],[1,0.56],[1,0.76],[0,0.76]]` |
| 横版 16:9 底部字幕区 | `[[0,0.8],[1,0.8],[1,1],[0,1]]` |
| 竖版右上角剧情提示区 | `[[0.85,0.02],[1,0.02],[1,0.33],[0.85,0.33]]` |
| 竖版左上角剧情提示区 | `[[0,0.01],[0.15,0.01],[0.15,0.33],[0,0.33]]` |

只在片头或片尾出现的文字，建议设置 `start`、`end` 或 `to_end`，避免同一区域后续画面被误识别。

## ASR 与 OCR 选择

| 用户输入 | 选择 |
| --- | --- |
| “根据视频声音生成字幕”“提取台词” | ASR |
| “识别画面上已有字幕”“提取硬字幕” | OCR |
| 视频没有清晰人声但有画面字幕 | OCR |
| 视频有多角色人声，需要区分说话人 | ASR，并考虑 `asr_speaker_detect_on=true` |

## 查询结果

提交后生产接入推荐通过 `callback` 接收结果；也可通过 [任务查询](./53-series-edit-task-list.md) 查看任务状态。任务成功后，通过 [字幕素材管理](./61-series-subtitle-materials.md) 查询产出的字幕素材：

| 提取方式 | 查询条件 |
| --- | --- |
| ASR | `subtitleFrom=2`，并按 `idSeries`、`idVeMaterialVideo`、`sourceLang` 过滤。 |
| OCR | `subtitleFrom=3`，并按 `idSeries`、`idVeMaterialVideo`、`sourceLang` 过滤。 |

查询到的字幕 `id` 可作为后续任务中的 `idVeMaterialSrt`。

## 相关文档

- [译制出海剪辑 API 总览](./51-series-overview.md)：查看模块流程和任务选择规则。
- [通用任务结构](./52-series-edit-common-task-structure.md)：查看 `items[]`、`workDto`、`videoEditParamsDto` 和 Python 提交通用模板。
- [任务查询](./53-series-edit-task-list.md)：提交后查询任务处理进度。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试、幂等和补偿轮询规则。
- [字幕素材管理](./61-series-subtitle-materials.md)：查询 ASR/OCR 产出的字幕素材。
- [错误与检查清单](./59-series-edit-errors-and-checklist.md)：排查参数缺失或业务校验失败。

## Agent 决策规则

- 用户要从音频人声转写字幕时，用 ASR。
- 本功能为异步任务；生产接入推荐传入 `callback` 接收结果，轮询作为查询和补偿兜底。
- 用户要从画面硬字幕识别字幕时，用 OCR。
- OCR 必须提供 `videoInpaintMasks`。框选坐标、点序、时间字段与普通单视频 OCR 规则完全一致。
- 不需要翻译时，`lang` 与 `sourceLang` 或 `videoInpaintLang` 保持一致。
- 本模块的 `videoInpaintMasks` 示例是数组对象，不要默认转成 JSON 字符串。
- 字幕提取完成后不要只停在任务成功状态；继续查询字幕素材列表获得 `idVeMaterialSrt`。
