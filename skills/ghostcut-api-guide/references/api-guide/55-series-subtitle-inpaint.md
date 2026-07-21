# 译制出海字幕擦除

> 字幕擦除用于去掉视频画面里的字幕、文字或指定区域。译制出海模块支持基础去字、Lite 去字和 Pro 去字。

## 接口信息

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/edit/task/subtitle/inpaint
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

接口路径：

```text
gateway/ve/series/edit/task/subtitle/inpaint
```

## 最小可用请求检查清单

| 检查项 | 要求 |
| --- | --- |
| 项目和视频 | 已准备 `idSeries` 和 `items[].idMaterialVideo`，且视频素材已满足 `downloadStatus=1`、`processStatus=1`。 |
| 擦除模式 | 基础全屏用 `needChineseOcclude=1`；框选、Lite、Pro 用 `needChineseOcclude=2` 并传 `videoInpaintMasks[]`。 |
| 语言 | `videoInpaintLang` 按画面字幕语言传；Lite/Pro 通常传 `all`。 |
| 框选坐标 | `videoInpaintMasks[].region` 使用 `0` 到 `1` 的相对坐标，点序为左上、右上、右下、左下。 |
| Pro 面积 | `advanced` 单框面积小于 `20%`；大框使用 `advanced_large_box` 且小于 `40%`。 |
| 后续复用 | 若后续任务要基于擦除后视频，先查 `task/list` 再用 `/work/status` 取 `body.content[].id`，填入后续 `materialWorkIds`。 |

## 模式选择

| 模式 | 关键参数 | 适用场景 |
| --- | --- | --- |
| 基础去字 | `needChineseOcclude=1`，可不传 `extra_inpaint_config.model` | 全屏自动处理指定语言字幕或文字。 |
| 基础框选 | `needChineseOcclude=2`、`videoInpaintMasks` | 手动指定区域，可用于字幕、文字、logo、贴纸等。 |
| Lite 去字 | `needChineseOcclude=2`、`model=advanced_lite`、`videoInpaintMasks` | 手动指定一个或多个字幕区域，速度和成本更适中。 |
| Pro 框选去字 | `needChineseOcclude=2`、`model=advanced` 或 `advanced_large_box`、`videoInpaintMasks` | 单个字幕区域，追求更高质量。 |
| Pro 全屏去字 | `needChineseOcclude=1`、`model=advanced_full` | 全屏自动高质量擦除，不需要 `videoInpaintMasks`。 |

框选、坐标和时间字段规则与 [视频去字幕](./21-erase-video-subtitle.md) 和 [字幕 mask 补充说明](./22-inpaint-masks-supplement.md) 完全一致。差异是普通单视频接口中的 `videoInpaintMasks` 和 `extraOptions` 要传 JSON 字符串，而译制出海任务示例中直接传对象或数组。

## 基础去字请求示例

```json
{
  "idSeries": 10001,
  "projectName": "demo.mp4",
  "callback": "https://example.com/callback",
  "sourceLang": "zh",
  "lang": "",
  "items": [
    {
      "idMaterialVideo": 30001,
      "workDto": {
        "idSeries": 10001,
        "resolution": "1080p",
        "workName": "demo.mp4",
        "extraOptions": {}
      },
      "videoEditParamsDto": {
        "type": "WORK",
        "videoInpaintLang": "zh",
        "needChineseOcclude": 1
      }
    }
  ]
}
```

## Lite 去字请求示例

```json
{
  "idSeries": 10001,
  "projectName": "demo.mp4",
  "callback": "https://example.com/callback",
  "sourceLang": "all",
  "lang": "",
  "items": [
    {
      "idMaterialVideo": 30001,
      "workDto": {
        "idSeries": 10001,
        "resolution": "1080p",
        "workName": "demo.mp4",
        "extraOptions": {
          "extra_inpaint_config": {
            "model": "advanced_lite"
          }
        }
      },
      "videoEditParamsDto": {
        "type": "WORK",
        "videoInpaintLang": "all",
        "needChineseOcclude": 2,
        "videoInpaintMasks": [
          {
            "type": "remove_only_ocr",
            "start": 0,
            "end": 99999,
            "region": [[0, 0.8], [1, 0.8], [1, 1], [0, 1]]
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
    if data.get("code") != 1000:
        raise RuntimeError(f"GhostCut API failed: {data}")
    return data


payload = {
    "idSeries": 10001,
    "projectName": "demo.mp4",
    "callback": "https://example.com/callback",
    "sourceLang": "all",
    "lang": "",
    "items": [
        {
            "idMaterialVideo": 30001,
            "workDto": {
                "idSeries": 10001,
                "resolution": "1080p",
                "workName": "demo.mp4",
                "extraOptions": {
                    "extra_inpaint_config": {
                        "model": "advanced_lite"
                    }
                }
            },
            "videoEditParamsDto": {
                "type": "WORK",
                "videoInpaintLang": "all",
                "needChineseOcclude": 2,
                "videoInpaintMasks": [
                    {
                        "type": "remove_only_ocr",
                        "start": 0,
                        "end": 99999,
                        "region": [[0, 0.8], [1, 0.8], [1, 1], [0, 1]]
                    }
                ]
            }
        }
    ]
}

result = api_post(
    "/v-w-c/gateway/ve/series/edit/task/subtitle/inpaint",
    payload,
)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## Pro 去字请求示例

Pro 去字和 Lite 去字请求结构相同，只把 `workDto.extraOptions.extra_inpaint_config.model` 改为 `advanced` 或 `advanced_large_box`：

```json
{
  "extra_inpaint_config": {
    "model": "advanced"
  }
}
```

如果框面积达到或超过 `20%`，不要使用 `advanced`；改用 `advanced_large_box`，并控制在 `40%` 以下。面积按相对坐标计算：`(x1 - x0) * (y1 - y0)`。

## 遮罩框规则

`videoInpaintMasks[].region` 使用 `0` 到 `1` 的相对坐标，常见矩形框按左上、右上、右下、左下排序：

```json
[
  [0, 0.8],
  [1, 0.8],
  [1, 1],
  [0, 1]
]
```

常用字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `type` | `String` | 框类型。基础版可用 `remove`、`remove_only_ocr`、`keep`；Lite/Pro 框选只能用 `remove_only_ocr`。 |
| `start` | `Number` | 框开始生效的时间点，单位秒。用于跳过片头时，把它设为片头秒数。 |
| `end` | `Number` | 框结束生效的绝对时间点，单位秒。和 `to_end` 二选一。 |
| `to_end` | `Number` | 距离视频结尾多少秒前停止生效。`to_end: 10` 表示跳过最后 10 秒。 |
| `region` | `number[][]` | 四点相对坐标，按左上、右上、右下、左下顺时针排列。 |

## 版本差异

| 版本 | `extra_inpaint_config.model` | `needChineseOcclude` | `videoInpaintLang` | 遮罩框数量 | 遮罩框类型 | 面积限制 |
| --- | --- | --- | --- | --- | --- | --- |
| 基础版 Basic | 不传 | 常用 `1` 全屏或 `2` 框选 | `zh`、`en`、`all`、`ja`、`ko`、`ar` 等 | 支持多框 | `remove`、`remove_only_ocr`、`keep` | 无限制 |
| 高级版 Lite | `advanced_lite` | 固定传 `2` | 仅 `all` | 1 到 10 个 | 仅 `remove_only_ocr` | 无限制 |
| 高级版 Pro 框选 | `advanced` 或 `advanced_large_box` | 固定传 `2` | 仅 `all` | 仅 1 个 | 仅 `remove_only_ocr` | `advanced` 小于 20%；`advanced_large_box` 小于 40% |
| 高级版 Pro 全屏 | `advanced_full` | 固定传 `1` | 仅 `all` | 不需要 | 不适用 | 不适用 |

框类型说明：

| `type` | 作用 | 适用建议 |
| --- | --- | --- |
| `remove` | 整个框内都擦除，不管有没有文字。 | 擦台标、logo、贴纸、水印、固定图标等；主要用于基础版。 |
| `remove_only_ocr` | 只检测并擦除框内文字，尽量保留非文字背景。 | 字幕区域首选；高级版 Lite 和 Pro 框选只能用这个类型。 |
| `keep` | 保护该区域，不进行处理。 | 基础版多框时用于避免误擦某个区域。 |

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
| 竖版右下角备案编号区 | `[[0.5,0.95],[1,0.95],[1,1],[0.5,1]]` |

只在片头或片尾出现的文字、备案编号、剧情提示，建议设置 `start`、`end` 或 `to_end`，避免同一区域后续画面被误擦。

## 后续复用

如果字幕擦除结果要继续用于字幕压制或音频分离，后续任务需要在 `workDto.materialWorkIds` 中传入去字后作品 ID。

`materialWorkIds` 用于复用字幕擦除后的作品结果，不是字幕擦除任务 ID，也不是视频素材 ID。应先通过 [任务查询](./53-series-edit-task-list.md) 的 `task/list` 查询字幕擦除任务结果，拿到对应任务的 `body[].id`；这个字段是任务 ID。再按[视频任务状态查询](./11-work-status-query.md)的方式调用 `/work/status` 查询该任务下的作品详情，从响应的 `body.content[].id` 读取作品 ID，并填入后续任务的 `workDto.materialWorkIds`。

## 相关文档

- [译制出海剪辑 API 总览](./51-series-overview.md)：查看模块流程和任务选择规则。
- [通用任务结构](./52-series-edit-common-task-structure.md)：查看通用字段和 Python 提交通用模板。
- [字幕压制](./57-series-subtitle-burn.md)：基于去文字后视频压制新字幕。
- [音频分离](./58-series-audio-separate.md)：基于去文字后视频做音频分离。
- [任务查询](./53-series-edit-task-list.md)：提交后查询任务状态。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试、幂等和补偿轮询规则。
- [项目与视频素材](./60-series-project-and-video-materials.md)：确认素材已准备完成。
- [字幕 mask 补充说明](./22-inpaint-masks-supplement.md)：查看与普通单视频一致的框选规则、坐标和模型差异。

## Agent 决策规则

- 用户只说“去字幕/擦字幕”且没有手动画框时，优先考虑基础去字。
- 本功能为异步任务；生产接入推荐传入 `callback` 接收结果，轮询作为查询和补偿兜底。
- 用户给出字幕区域或要求框选时，使用 `needChineseOcclude=2` 和 `videoInpaintMasks`。
- 擦字幕时，Lite/Pro 框选使用 `remove_only_ocr`；不要用 Lite/Pro 框选擦 logo、贴纸、台标等非文字内容。
- Lite 模型传 `advanced_lite`，支持 1 到 10 个框；Pro 框选只支持单框，按面积选择 `advanced` 或 `advanced_large_box`。
- 本模块的 `videoInpaintMasks` 可直接传数组对象，不要默认转成 JSON 字符串。
- 坐标必须是 `0` 到 `1` 的相对坐标，点序必须是左上、右上、右下、左下。
- 需要串联后续任务时，记得让后续任务传 `workDto.materialWorkIds`。
- `task/list` 的 `body[].id` 是任务 ID，不是作品 ID；需要继续调用 `/work/status` 查询作品详情，并读取 `body.content[].id` 作为作品 ID。
- `materialWorkIds` 不能用视频素材 ID 代替。
