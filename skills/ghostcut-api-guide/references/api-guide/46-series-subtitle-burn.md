> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 译制出海字幕压制

> 字幕压制用于把字幕内容渲染到视频画面中。可以基于原视频压制，也可以基于字幕擦除后的结果视频压制。

## 接口信息

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/edit/task/subtitle/burn
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

接口路径：

```text
gateway/ve/series/edit/task/subtitle/burn
```

## 最小可用请求检查清单

| 检查项 | 要求 |
| --- | --- |
| 项目和视频 | 已准备 `idSeries` 和 `items[].idMaterialVideo`，且视频素材已满足 `downloadStatus=1`、`processStatus=1`。 |
| 字幕输入 | `workDto.idVeMaterialSrt` 与 `workDto.extraOptions.customer_input.content[]` 必须二选一；不能同时传。 |
| 字幕压制参数 | 固定传 `wyTaskType=NO_TTS`、`wyNeedText=1`、`needWyEdit=0`。 |
| 字幕样式 | 必须传 `videoEditParamsDto.wyVoiceParam.font_param`；不需要传 `character_voices[]`。 |
| 基于擦除后视频 | 如果要基于字幕擦除后的作品压字幕，`workDto.materialWorkIds` 必须来自 `/work/status.body.content[].id`。 |
| 结果查询 | 提交后先查 [任务查询](./42-series-edit-task-list.md)，需要作品 ID 或播放地址时再查 [视频任务状态查询](./11-work-status-query.md)。 |

## 原视频字幕压制

关键参数：

| 字段 | 位置 | 值 |
| --- | --- | --- |
| `needWanyin` | `videoEditParamsDto` | `1` |
| `wyTaskType` | `videoEditParamsDto` | `NO_TTS` |
| `wyNeedText` | `videoEditParamsDto` | `1` |
| `needWyEdit` | `videoEditParamsDto` | `0` |
| `customer_input` | `workDto.extraOptions` | 字幕内容和时间轴 |
| `wyVoiceParam.font_param` | `videoEditParamsDto` | 字幕样式 |

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
        "extraOptions": {
          "customer_input": {
            "prefix": "demo-series",
            "content": [
              {
                "start": 0.12,
                "end": 1.22,
                "source": "示例字幕。",
                "character": "Narrator",
                "id_ve_character": 100001,
                "manualModify": true,
                "translation": "示例字幕。"
              }
            ]
          }
        }
      },
      "videoEditParamsDto": {
        "type": "WORK",
        "needWanyin": 1,
        "wyTaskType": "NO_TTS",
        "wyNeedText": 1,
        "needWyEdit": 0,
        "wyVoiceParam": {
          "font_param": {
            "style": "n-4-T",
            "font_size": 40,
            "position": 0.73,
            "videoWidth": 622,
            "subtitleLang": "zh",
            "fontFileName": "NotoSans-Bold.ttf"
          }
        }
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
                    "customer_input": {
                        "prefix": "demo-series",
                        "content": [
                            {
                                "start": 0.12,
                                "end": 1.22,
                                "source": "示例字幕。",
                                "character": "Narrator",
                                "id_ve_character": 100001,
                                "manualModify": True,
                                "translation": "示例字幕。"
                            }
                        ]
                    }
                }
            },
            "videoEditParamsDto": {
                "type": "WORK",
                "needWanyin": 1,
                "wyTaskType": "NO_TTS",
                "wyNeedText": 1,
                "needWyEdit": 0,
                "wyVoiceParam": {
                    "font_param": {
                        "style": "n-4-T",
                        "font_size": 40,
                        "position": 0.73,
                        "videoWidth": 622,
                        "subtitleLang": "zh",
                        "fontFileName": "NotoSans-Bold.ttf"
                    }
                }
            }
        }
    ]
}

result = api_post(
    "/v-w-c/gateway/ve/series/edit/task/subtitle/burn",
    payload,
)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

## 去文字后视频字幕压制

如果字幕压制要基于字幕擦除后的结果视频，在原视频字幕压制请求基础上，在 `workDto` 中增加 `materialWorkIds`：

```json
{
  "workDto": {
    "materialWorkIds": "50001"
  }
}
```

`materialWorkIds` 应填写字幕擦除任务产出的可复用作品 ID。先通过 [任务查询](./42-series-edit-task-list.md) 的 `task/list` 查询字幕擦除任务结果，找到对应的最新字幕擦除任务，读取 `body[].id` 作为任务 ID；再按[视频任务状态查询](./11-work-status-query.md)的方式调用 `/work/status` 查询该任务下的作品详情，从响应的 `body.content[].id` 读取作品 ID，并填入 `workDto.materialWorkIds`。

## 字幕内容来源

本接口示例使用 `workDto.extraOptions.customer_input.content[]` 直接传入字幕内容和时间轴。若业务使用已上传字幕素材，可改用 `workDto.idVeMaterialSrt`。

`workDto.idVeMaterialSrt` 和 `workDto.extraOptions.customer_input` 不接受同时传。组装字幕压制任务时必须二选一：要么引用字幕素材，要么直接传字幕内容和时间轴。

`idVeMaterialSrt` 应来自 [字幕素材管理](./50-series-subtitle-materials.md) 的字幕上传、创建、复制或查询结果。不要把字幕文件 URL、上传凭证中的临时 URL 或翻译任务 ID 填入该字段。

## 字幕压制与音色配置

字幕压制使用 `wyTaskType=NO_TTS`，表示只压制字幕、不生成新配音。此时 `wyVoiceParam` 只需要 `font_param`，永远不需要传 `character_voices[]`。

组装字幕压制请求时不要传 `character_voices[]`；字幕压制不会生成新配音，不需要任何角色音色配置。

## 字幕样式参数

译制出海字幕压制里的 `wyVoiceParam.font_param`，与普通单视频文档 [字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md) 使用同一套规则。没有特殊样式要求时，可以直接复用 `25` 中推荐的默认组合。

### V1.0 简化写法

适合快速压制字幕，只控制样式、字号和位置。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `style` | `string` | 字幕样式 code。常用 `tpl-31-1-T`。 |
| `font_size` | `number` | 字号，基于 720p 缩放。 |
| `position` | `number` | 字幕区域上沿位置，常用 `0.727` 到 `0.8`。 |

推荐默认值：

```json
{
  "font_param": {
    "style": "tpl-31-1-T",
    "font_size": 32,
    "position": 0.727
  }
}
```

### V2.0 完整写法

适合需要更细控制外观的场景，例如自定义字体、描边、阴影或背景。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `style` | `string` | 样式 code。 |
| `font_size` | `number` | 字号。 |
| `position` | `number` | 字幕位置。 |
| `subtitleLang` | `string` | 字幕语种，应与压制字幕语言一致。 |
| `videoWidth` | `number` | 参考画布宽度，通常填视频宽度。 |
| `fontFileName` | `string` | 字体文件名。 |
| `config` | `object` | 细粒度样式配置。 |

示例：

```json
{
  "font_param": {
    "style": "n-1-T",
    "font_size": 40,
    "position": 0.72,
    "subtitleLang": "en",
    "videoWidth": 1280,
    "fontFileName": "NotoSans-Bold.ttf",
    "config": {
      "fontFamily": "NotoSans",
      "fontWeightBold": true,
      "fontStyleItalic": false,
      "textAlign": "center",
      "lineSpace": 5,
      "fillStyle": "#FFFFFF",
      "strokeLineWidth": 2,
      "strokeStyle": "#010101",
      "shadowColor": "rgba(0, 0, 0, 0)",
      "shadowOffsetX": 1,
      "shadowOffsetY": 1,
      "shadowBlur": 1,
      "bgType": 0,
      "subtitleAreaWidth": 0.9
    }
  }
}
```

### 常用配置建议

- 没有特别美术要求时，优先使用 `style="tpl-31-1-T"`、`font_size=32`、`position=0.727` 到 `0.8`。
- `font_size` 会根据视频尺寸缩放。720p 基准下常用 `30` 到 `50`；竖屏视频可适当增大。
- 字幕被挡住或离底部太近时，优先调 `position`。
- `subtitleAreaWidth` 不要设得太小，否则会导致频繁自动换行。

### `config` 常用字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `fontFamily` | `string` | 字体名，例如 `NotoSans`。 |
| `fontWeightBold` | `boolean` | 是否加粗。 |
| `fontStyleItalic` | `boolean` | 是否斜体。 |
| `textAlign` | `string` | 对齐方式，通常 `center`。 |
| `lineSpace` | `number` | 行间距。 |
| `fillStyle` | `string` | 字体颜色。 |
| `strokeLineWidth` | `number` | 描边宽度。 |
| `strokeStyle` | `string` | 描边颜色。 |
| `shadowColor` | `string` | 阴影颜色。 |
| `shadowOffsetX` | `number` | 阴影 X 偏移。 |
| `shadowOffsetY` | `number` | 阴影 Y 偏移。 |
| `shadowBlur` | `number` | 阴影模糊程度。 |
| `bgType` | `number` | 背景类型。`0` 表示无背景。 |
| `subtitleAreaWidth` | `number` | 字幕区域宽度占比。 |

### 字体文件规则

- `fontFamily` 与 `fontFileName` 应成对指定。
- 多语种场景优先使用 `NotoSans`。
- `fontFileName` 需要根据 `subtitleLang` 和是否加粗计算，例如 `NotoSans-Bold.ttf`、`NotoSansJP-Bold.ttf`、`NotoSansTC-Bold.ttf`。
- 更完整的字体映射、背景类型和默认样式，直接参考 [字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md)。

## 相关文档

- [译制出海剪辑 API 总览](./40-series-overview.md)：查看模块流程和任务选择规则。
- [通用任务结构](./41-series-edit-common-task-structure.md)：查看 `customer_input`、`font_param`、`materialWorkIds` 和 Python 提交通用模板。
- [字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md)：查看 V1/V2 字幕样式、字号缩放、字体文件和背景配置。
- [字幕素材管理](./50-series-subtitle-materials.md)：获取 `idVeMaterialSrt` 或从 `slInfo` 解析字幕内容。
- [字幕擦除](./44-series-subtitle-inpaint.md)：先擦除旧字幕，再压制新字幕。
- [视频任务状态查询](./11-work-status-query.md)：如果要查看作品播放地址或详情，按本文方式查询。
- [任务查询](./42-series-edit-task-list.md)：提交后查询任务处理进度。

## Agent 决策规则

- 用户只要把字幕压到画面上，不需要生成新配音时，用本接口。
- 字幕压制固定使用 `wyTaskType=NO_TTS`，并设置 `wyNeedText=1`。
- 字幕文本和时间轴可放在 `workDto.extraOptions.customer_input.content[]`。
- 如果使用字幕素材，先查字幕列表确认 `idVeMaterialSrt`。
- `idVeMaterialSrt` 和 `customer_input` 必须二选一，不能同时传。
- 如果要基于去字后视频压制，必须传 `workDto.materialWorkIds`；取值来自 `/work/status` 的 `body.content[].id`。
- `wyTaskType=NO_TTS` 的字幕压制永远不需要 `character_voices[]`；只传 `wyVoiceParam.font_param` 配置字幕样式。
- `font_param.subtitleLang` 应与字幕语言一致。
- 只需要快速设置样式时，优先使用 V1.0：`style`、`font_size`、`position`。
- 需要控制字体、描边、阴影、背景或多语种字体文件时，使用 V2.0 并补齐 `config`、`fontFileName`、`subtitleLang`、`videoWidth`。
