> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 译制出海 AI 配音

> AI 配音用于在译制出海项目中生成新配音，可配合字幕文本、角色音色和字幕样式生成译后视频。本文说明经典模式、音色类型、手动角色音色选择和情感克隆模式的参数差异。

## 接口信息

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/edit/task/dubbing
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

接口路径：

```text
gateway/ve/series/edit/task/dubbing
```

## 最小可用请求检查清单

组装 `/series/edit/task/dubbing` 请求时，先确认下面这些条件都满足：

| 检查项 | 要求 |
| --- | --- |
| 项目和视频 | 已准备 `idSeries` 和 `items[].idMaterialVideo`，且二者属于同一项目上下文。 |
| 字幕输入 | `workDto.idVeMaterialSrt` 与 `workDto.extraOptions.customer_input.content[]` 必须二选一；不能同时传，也不能完全不传。 |
| 配音模式 | 经典模式传 `wyTaskType=FULL` 并传 `wyVoiceParam.character_voices[]`；情感克隆模式传 `wyTaskType=VOICE_CLONE_PRO`，不传 `character_voices[]`。 |
| 经典模式音色 | `character_voices[].voice_type` 传 `TTS` 或 `CLONE`；`character_voices[].id_ve_voice_character` 来自 [公共音色查询接口](./32-public-voice-characters.md) 返回的音色角色 ID。 |
| 原音处理 | `videoEditParamsDto.removeBgAudio` 需要出现在 AI 配音任务中。 |
| 新任务标志 | `/edit/task/dubbing` 表示发起新的配音任务，`videoEditParamsDto.needWyEdit` 始终传 `0`。 |
| 新字幕 | `wyNeedText=1` 时必须传 `wyVoiceParam.font_param`，并让 `font_param.subtitleLang` 与目标语言 `lang` 一致；`wyNeedText=0` 时不需要传 `font_param`。 |
| 结果查询 | 提交后先用 [任务查询](./42-series-edit-task-list.md) 定位任务；需要作品 ID、播放地址或详情时，再用任务 ID 调用 [视频任务状态查询](./11-work-status-query.md)。 |

## 推荐使用流程

1. 先通过 [项目与视频素材](./49-series-project-and-video-materials.md) 准备 `idSeries` 和 `idMaterialVideo`。
2. 准备字幕输入来源：
   - 已有字幕素材时，使用 `workDto.idVeMaterialSrt`。
   - 需要手工指定时间轴、台词、角色或译文时，使用 `workDto.extraOptions.customer_input.content[]`。
   - `idVeMaterialSrt` 和 `customer_input` 不接受同时传，必须二选一。
   - `/series/edit/task/dubbing` 不允许完全不传字幕；经典模式和情感克隆模式都必须提供上述两种字幕输入之一。
   - 如果需要先把字幕翻译成目标语种，先执行 [字幕翻译任务](./51-series-subtitle-translation.md)。
3. 先选择配音模式：
   - 经典模式：手动为角色选择音色，必须使用 `wyTaskType=FULL`，同时在 `character_voices[]` 中配置每个角色的音色。
   - 情感克隆模式：传 `wyTaskType=VOICE_CLONE_PRO`，系统自动复刻原声声线和情感，不需要为角色手动选择音色。
4. 经典模式下再准备音色：
   - 音色统一使用 [公共音色查询接口](./32-public-voice-characters.md) 查询后填写到 `id_ve_voice_character`。
   - `voice_type=TTS` 表示经典基础或经典高级音色；`voice_type=CLONE` 表示超真实音色。
   - 无论 `voice_type=TTS` 还是 `voice_type=CLONE`，都使用同一套 `id_ve_voice_character` 传参逻辑。
5. 如需基于已有作品结果继续处理，例如“先擦除字幕，再做配音”，先查询前一步任务，再通过 `/work/status` 取到可复用的作品 ID。作品 ID 路径是 `body.content[].id`，填入 `workDto.materialWorkIds`。
6. 调用本文接口提交配音任务。
7. 提交后先调用 [任务查询](./42-series-edit-task-list.md) 判断任务是否完成；如果还需要作品详情、作品 ID 或播放地址，再按 [视频任务状态查询](./11-work-status-query.md) 调用 `/v-w-c/gateway/ve/work/status`。

## 字幕输入来源

AI 配音至少需要一份可用的字幕内容。`/series/edit/task/dubbing` 不支持在完全不传字幕的情况下由系统默认 ASR 提取字幕；经典模式和情感克隆模式都必须使用下列两种输入方式之一：

| 方式 | 位置 | 适用场景 |
| --- | --- | --- |
| 使用已有字幕素材 | `workDto.idVeMaterialSrt` | 已经上传、提取或翻译好了字幕，直接复用现成字幕。 |
| 手工传字幕内容 | `workDto.extraOptions.customer_input.content[]` | 需要显式指定时间轴、角色、原文、译文，或希望用人工编辑后的内容直接驱动配音。 |

### 何时优先用 `idVeMaterialSrt`

- 已经有与当前视频绑定的字幕素材。
- 需要复用 OCR、ASR、上传字幕或字幕翻译任务的结果。
- 只需要引用已有字幕，不需要在本次请求里手工覆盖时间轴和文本。

### 何时优先用 `customer_input.content[]`

- 需要手工指定每句台词的开始时间、结束时间、角色、原文和译文。
- 需要把人工修订后的台词直接作为本次配音的输入。
- 需要为部分句子补充角色、发音策略或人工修订标记。

`customer_input.content[].audio_type` 可控制单句发音策略：

| 枚举 | 含义 |
| --- | --- |
| `TTS` | 系统 AI 配音。 |
| `Mute` | 静音不配音。 |
| `RAW_VOCAL` | 保留原片人声。 |

### 输入来源必须二选一

`workDto.idVeMaterialSrt` 和 `workDto.extraOptions.customer_input` 不接受同时传。组装任务时必须先选定一种字幕来源：

- 使用已有字幕素材时，只传 `workDto.idVeMaterialSrt`，不要再传 `customer_input`。
- 使用人工编辑内容时，只传 `workDto.extraOptions.customer_input.content[]`，不要再传 `idVeMaterialSrt`。
- 不要自行假设“后传字段覆盖前传字段”或“`customer_input` 会覆盖字幕素材”；同时传属于错误请求。
- 不要把普通单视频配音中的“未传字幕时默认 ASR”规则套用到译制出海 `/series/edit/task/dubbing`。

## 经典模式配音

经典模式指“手动为角色选择音色”的配音方式。经典基础、经典高级和超真实音色都属于经典模式；区别只在 `voice_type` 和音色 ID，不在配音模式。

经典模式必须使用 `wyTaskType=FULL`，并在 `wyVoiceParam.character_voices[]` 中为每个角色配置音色。

关键参数：

| 字段 | 位置 | 值 |
| --- | --- | --- |
| `needWanyin` | `videoEditParamsDto` | `1` |
| `wyTaskType` | `videoEditParamsDto` | `FULL` |
| `wyNeedText` | `videoEditParamsDto` | `1` 表示把新字幕压制到画面；`0` 表示只重新配音、不压制新字幕。 |
| `wyVoiceParam.font_param` | `videoEditParamsDto` | `wyNeedText=1` 时必传，用于控制新字幕样式；`wyNeedText=0` 时不传。 |
| `wyVoiceParam.character_voices[]` | `videoEditParamsDto` | 角色音色 |
| `customer_input` | `workDto.extraOptions` | 台词、角色、时间轴和译文 |

请求示例：

```json
{
  "idSeries": 10001,
  "projectName": "demo.mp4",
  "callback": "https://example.com/callback",
  "sourceLang": "zh",
  "lang": "en",
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
                "source": "Hello.",
                "character": "Narrator",
                "id_ve_character": 100001,
                "manualModify": true,
                "translation": "Hello.",
                "audio_type": "TTS"
              }
            ]
          }
        }
      },
      "videoEditParamsDto": {
        "wyVoiceParam": {
          "font_param": {
            "style": "n-4-T",
            "font_size": 40,
            "position": 0.73,
            "videoWidth": 622,
            "subtitleLang": "en",
            "fontFileName": "NotoSans-Bold.ttf"
          },
          "character_voices": [
            {
              "character": "Narrator",
              "id_ve_character": 100001,
              "voice_type": "TTS",
              "id_ve_voice_character": 200001
            }
          ]
        },
        "wyNeedText": 1,
        "removeBgAudio": 0,
        "wyTaskType": "FULL",
        "needWyEdit": 0,
        "needWanyin": 1,
        "type": "WORK"
      },
      "overwriteLang": "en"
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
    "lang": "en",
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
                                "source": "Hello.",
                                "character": "Narrator",
                                "id_ve_character": 100001,
                                "manualModify": True,
                                "translation": "Hello.",
                                "audio_type": "TTS"
                            }
                        ]
                    }
                }
            },
            "videoEditParamsDto": {
                "wyVoiceParam": {
                    "font_param": {
                        "style": "n-4-T",
                        "font_size": 40,
                        "position": 0.73,
                        "videoWidth": 622,
                        "subtitleLang": "en",
                        "fontFileName": "NotoSans-Bold.ttf"
                    },
                    "character_voices": [
                        {
                            "character": "Narrator",
                            "id_ve_character": 100001,
                            "voice_type": "TTS",
                            "id_ve_voice_character": 200001
                        }
                    ]
                },
                "wyNeedText": 1,
                "removeBgAudio": 0,
                "wyTaskType": "FULL",
                "needWyEdit": 0,
                "needWanyin": 1,
                "type": "WORK"
            },
            "overwriteLang": "en"
        }
    ]
}

result = api_post(
    "/v-w-c/gateway/ve/series/edit/task/dubbing",
    payload,
)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

如果只需要生成新配音、不把字幕合成到画面中，`wyNeedText` 可以传 `0`。此时仍然需要字幕输入来驱动配音，但 `wyVoiceParam` 可以只包含 `character_voices[]`，不需要传 `font_param`。

## 超真实音色

超真实是音色类型，不是情感克隆模式。使用超真实音色时仍然属于经典模式：需要手动为角色选择音色，并在 `character_voices[]` 中传对应音色。

超真实请求结构与经典基础/经典高级音色一致，主要差异是角色音色配置：

```json
{
  "character": "Narrator",
  "id_ve_character": 100001,
  "voice_type": "CLONE",
  "id_ve_voice_character": 200002
}
```

当前规则已经明确：

- `voice_type=CLONE` 表示超真实音色。
- `voice_type=TTS` 表示经典基础或经典高级音色。
- `voice_type=CLONE` 仍然属于经典模式，不等于情感克隆模式。
- 无论 `voice_type=TTS` 还是 `voice_type=CLONE`，都使用 `id_ve_voice_character`。
- 使用音色前，仍应确认该音色支持目标语种 `lang`。

## 情感克隆

情感克隆是配音模式，不是 `voice_type=CLONE`。它表示：不手动为角色选择音色，由系统自动复刻原视频的人声声线和情感。

情感克隆与经典模式的主要差异：

- `wyTaskType` 必须传 `VOICE_CLONE_PRO`，它是情感克隆模式的标志。
- 不需要传 `wyVoiceParam.character_voices[]`，也不需要调用公共音色接口选择音色。
- 仍然必须提供字幕输入：要么传 `workDto.idVeMaterialSrt`，要么传 `workDto.extraOptions.customer_input.content[]`。不能完全不传字幕。
- `wyNeedText=1` 时，`wyVoiceParam` 只传 `font_param`；`wyNeedText=0` 时不需要传 `font_param`。
- 不要把 `voice_type=CLONE` 当成情感克隆模式；它只是超真实音色类型。
- `customer_input.content[]` 中可不传 `character`、`manualModify`，`id_ve_character` 可传 `0`。
- `/edit/task/dubbing` 表示发起一个新的配音任务，`needWyEdit` 始终传 `0`。

请求片段：

```json
{
  "items": [
    {
      "videoEditParamsDto": {
        "wyVoiceParam": {
          "font_param": {
            "style": "tpl-14-1-T",
            "font_size": 40,
            "position": 0.73,
            "videoWidth": 622,
            "subtitleLang": "en",
            "fontFileName": "NotoSans-Bold.ttf"
          }
        },
        "wyTaskType": "VOICE_CLONE_PRO",
        "wyNeedText": 1,
        "removeBgAudio": 0,
        "needWyEdit": 0,
        "needWanyin": 1,
        "type": "WORK"
      },
      "overwriteLang": "en"
    }
  ]
}
```

## 音色选择与字段映射

音色通过 [公共音色查询接口](./32-public-voice-characters.md) 获取。查询接口返回对象中的音色角色 ID，提交配音任务时应填入 `character_voices[].id_ve_voice_character`。

常规映射方式：

| 音色类型 | 字段 | 来源 |
| --- | --- | --- |
| 经典基础/经典高级 | `character_voices[].voice_type=TTS` | 公共音色查询接口中 `voiceType=0` 或 `voiceType=1` 的音色。 |
| 超真实 | `character_voices[].voice_type=CLONE` | 公共音色查询接口中 `voiceType=2` 的音色。 |
| 任意经典模式音色 | `character_voices[].id_ve_voice_character` | 音色查询结果中的音色角色 ID。 |
| 任意经典模式音色 | `character_voices[].character` | 角色名。 |
| 任意经典模式音色 | `character_voices[].id_ve_character` | 角色 ID。 |

补充规则：

- `voice_type` 表示音色类型，不表示配音模式；常见 `TTS`、`CLONE`。
- 查询接口中的 `voiceType` 是筛选条件，取值 `0` 经典基础、`1` 经典高级、`2` 超真实；它不等同于提交参数 `voice_type`。
- 如果需要经典基础或经典高级音色，通常先用 `voiceType=0` 或 `voiceType=1` 查询候选音色，再在提交任务时填写 `voice_type=TTS` 和对应的 `id_ve_voice_character`。
- 如果需要超真实音色，通常先用 `voiceType=2` 查询候选音色，再在提交任务时填写 `voice_type=CLONE` 和对应的 `id_ve_voice_character`。
- 情感克隆模式通过 `wyTaskType=VOICE_CLONE_PRO` 区分，不通过 `voice_type=CLONE` 区分。
- 音色 ID 不应凭空猜测，应以音色查询接口返回的可用音色 ID 为准。

## AI 配音相关参数规则

AI 配音任务中有些字段容易和字幕擦除、视频翻译请求混在一起。Agent 组装请求时按以下规则处理：

| 字段 | AI 配音中的处理规则 |
| --- | --- |
| `removeBgAudio` | 原音处理参数，需要在 AI 配音任务中出现。常用值：`0` 保留原声和背景音，`1` 全局静音，`2` 去除音乐旋律并尽量保留人声/效果音。 |
| `overwriteLang` | 目标语种覆盖字段，传目标语言，通常与顶层 `lang` 一致；`wyNeedText=1` 时还要与 `wyVoiceParam.font_param.subtitleLang` 一致。 |
| `overwriteSourceLang` | 覆盖当前作品原语种，主要影响显示；新组装 AI 配音请求时可以忽略。 |
| `needWyEdit` | `/edit/task/dubbing` 是发起新的配音任务，该字段始终传 `0`。 |
| `needChineseOcclude` / `videoInpaintLang` / `videoInpaintMasks` / `videoInpaintMasks_lite` / `videoInpaintMasks_pro` / `vtrMode` / `vtrProModel` | 去字幕相关字段，不属于 AI 配音最小请求体。Agent 不要在 AI 配音任务中主动生成；如果需要去字幕，应先按 [译制出海字幕擦除](./44-series-subtitle-inpaint.md) 单独创建前序任务，再用 `materialWorkIds` 复用擦除后的作品。 |
| `extra_video_translate_config.use_audio_character` / `rhythmParam` | 新组装 AI 配音请求时不要主动生成；如果调用方已有稳定请求体，可按原请求体保留。它们不参与经典模式、超真实音色或情感克隆模式的判断。 |

## 字幕样式参数

译制出海 AI 配音中的新字幕样式，沿用 [字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md) 的规则。本文只保留组装配音任务时必须知道的部分，完整的 V1/V2 字段、字体文件、字号缩放和背景配置请看该补充文档。

规则：

- `wyNeedText=1` 表示把新字幕压制到画面，必须传 `videoEditParamsDto.wyVoiceParam.font_param`。
- `wyNeedText=0` 表示只生成新配音、不压制新字幕，不需要传 `font_param`。
- `font_param.subtitleLang` 应与目标语言 `lang` 一致；同时传 `overwriteLang` 时，也应保持一致。

### V1.0 简化写法

适合只需要快速控制字幕样式、字号和位置的场景。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `style` | `string` | 字幕样式 code，例如 `tpl-31-1-T`、`n-4-T`。 |
| `font_size` | `number` | 字号，基于 720p 做缩放。 |
| `position` | `number` | 字幕区域上沿相对位置，常用 `0.72` 到 `0.8`。 |

示例：

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

适合需要精细控制字体、描边、阴影、背景和多语种字体文件的场景。配音任务中可在 `font_param` 中补充 `subtitleLang`、`videoWidth`、`fontFileName` 和 `config`；完整字段含义以 [字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md) 为准。

最小结构示例：

```json
{
  "font_param": {
    "style": "n-1-T",
    "font_size": 40,
    "position": 0.72,
    "subtitleLang": "en",
    "videoWidth": 1280,
    "fontFileName": "NotoSans-Bold.ttf",
    "config": {}
  }
}
```

## 复用已有作品结果

如果当前配音任务不是直接基于原始视频，而是要接在某个已完成的视频任务之后，例如先做字幕擦除、再做配音，需要在 `workDto` 中传入：

```json
{
  "workDto": {
    "materialWorkIds": "50001"
  }
}
```

规则：

- `materialWorkIds` 传的是已有作品 ID，不是 `idMaterialVideo`。
- 不要把 `task/list` 返回的 `body[].id` 直接当成 `materialWorkIds`；那个字段是任务 ID。
- 正确流程是：先查 [任务查询](./42-series-edit-task-list.md) 取得前一步任务 ID，再按 [视频任务状态查询](./11-work-status-query.md) 调用 `/work/status`，从返回的 `body.content[].id` 读取可复用的作品 ID。

## 结果查询与作品获取

提交配音任务后，不要只看提交接口是否返回成功。推荐按下面的顺序查询：

1. 调用 [任务查询](./42-series-edit-task-list.md)。
2. 按 `idSeries`、语言方向和任务类型定位当前配音任务。译制出海配音任务通常对应 `taskType=SERIES_CLIP3`。
3. 读取 `task/list` 返回的 `body[].id`。这个字段是任务 ID，也可理解为 project id，不是作品 ID。
4. 如果只是判断任务是否完成，可先看：
   - `processingWorkCount`
   - `successWorkCount`
   - `errorWorkCount`
5. 如果还需要作品 ID、播放地址或作品详情，再把上一步的任务 ID 传给 [视频任务状态查询](./11-work-status-query.md) 的 `/v-w-c/gateway/ve/work/status`。
6. 以 `/work/status` 返回的作品详情为准读取最终结果；作品 ID 的精确路径是 `body.content[].id`。

对 agent 的结论：

- `task/list` 负责定位任务和判断任务级进度。
- `/work/status` 负责读取作品级结果。
- 不要把 `task/list.body[].id` 当成视频作品 ID 直接使用。

## 角色和字幕关系

- `customer_input.content[].character` 应与 `wyVoiceParam.character_voices[].character` 对应。
- `customer_input.content[].id_ve_character` 应与 `wyVoiceParam.character_voices[].id_ve_character` 对应。
- 如果 `wyNeedText=1`，必须提供 `font_param` 以控制新字幕样式，且 `font_param.subtitleLang` 必须与目标语言 `lang` 一致。
- 如果 `wyNeedText=0`，不需要压制新字幕，可不传 `font_param`。
- 如果使用已有字幕素材，先通过字幕列表确认 `workDto.idVeMaterialSrt` 属于同一 `idSeries` 和对应视频素材。
- 使用 `idVeMaterialSrt` 且经典模式需要手动配置音色时，角色可以从字幕素材的 `slInfo.sl[].character` 和 `slInfo.sl[].id_ve_character` 提取；如果业务已接入角色列表接口，也可以从该接口获取本部剧中的全部角色后再选择需要配音的角色。
- `idVeMaterialSrt` 和 `customer_input` 必须二选一，不能同时传。
- 如果配音前需要翻译字幕，先使用字幕翻译任务生成目标语种字幕，再把译后字幕用于配音。

## 配音专属检查清单

- `idSeries` 和 `idMaterialVideo` 必须属于同一个项目上下文；如果使用 `idVeMaterialSrt`，该字幕素材也必须属于同一项目上下文。
- `idVeMaterialSrt` 和 `customer_input` 是否只传了一种；不要同时传。
- `wyNeedText=1` 时，`font_param.subtitleLang` 必须与目标语言 `lang` 一致。
- `wyNeedText=0` 时，不需要压制新字幕，可不传 `wyVoiceParam.font_param`。
- `customer_input.content[].character` 与 `character_voices[].character` 应保持一一对应。
- `customer_input.content[].id_ve_character` 与 `character_voices[].id_ve_character` 应保持一一对应。
- 如果使用字幕素材，是否已从 `slInfo.sl[]` 获得角色信息；如果业务已接入角色列表接口，也可用该接口的角色结果为经典模式配置 `character_voices[]`。
- 公共音色必须确认支持目标语种；不要只按音色名称猜测可用语种。
- 经典模式下，无论 `voice_type=TTS` 还是 `voice_type=CLONE`，都使用 `id_ve_voice_character`。
- 不要把 `voice_type=CLONE` 当作情感克隆模式；它只表示超真实音色。
- 情感克隆模式传 `wyTaskType=VOICE_CLONE_PRO`，不需要传 `character_voices[]`。
- `/edit/task/dubbing` 表示发起新的配音任务，`needWyEdit` 始终传 `0`。
- 如果需要复用字幕擦除等前一步结果，使用 `materialWorkIds` 传作品 ID；该 ID 来自 `/work/status` 的 `body.content[].id`，不要误传视频素材 ID 或任务 ID。

## 相关文档

- [译制出海剪辑 API 总览](./40-series-overview.md)：查看模块流程和任务选择规则。
- [通用任务结构](./41-series-edit-common-task-structure.md)：查看 `customer_input`、`wyVoiceParam` 结构和 Python 提交通用模板。
- [视频任务状态查询](./11-work-status-query.md)：通过任务 ID 继续查询作品详情和播放地址。
- [公共音色查询接口](./32-public-voice-characters.md)：获取音色 ID 和可用语种。
- [字幕样式和字体配置补充](./25-subtitle-style-and-fonts.md)：查看 V1/V2 字幕样式、字号缩放、字体文件和背景配置。
- [任务查询](./42-series-edit-task-list.md)：提交后查询任务处理进度。
- [字幕素材管理](./50-series-subtitle-materials.md)：获取 `idVeMaterialSrt` 或解析字幕内容。
- [字幕翻译任务](./51-series-subtitle-translation.md)：先翻译字幕再配音。
- [翻译术语库](./52-series-translation-glossary.md)：固定角色名和专有名词译法。
- [错误与检查清单](./48-series-edit-errors-and-checklist.md)：排查音色与语种不匹配等问题。

## Agent 决策规则

- 用户要“译制出海配音”“AI 配音”“翻译并配音”时，使用本接口。
- 经典模式必须使用 `wyTaskType=FULL`，并通过 `character_voices[]` 手动选择角色音色。
- 情感克隆模式传 `wyTaskType=VOICE_CLONE_PRO`，不需要传 `character_voices[]`，但仍然必须提供 `idVeMaterialSrt` 或 `customer_input.content[]` 作为字幕输入。
- 提交后先查 `task/list`，需要作品详情或播放地址时再查 `/work/status`。
- 每个角色的 `character`、`id_ve_character` 和音色配置必须匹配。
- `wyNeedText=1` 时必须提供 `font_param`，且 `font_param.subtitleLang` 必须与目标语言 `lang` 一致；`wyNeedText=0` 时可以只配音不压字幕。
- 已有可复用字幕时，使用 `idVeMaterialSrt`；需要显式控制时间轴和文本时，使用 `customer_input.content[]`。两者必须二选一，不能同时传。
- `/series/edit/task/dubbing` 不能完全不传字幕；不要使用普通单视频“默认 ASR 提取字幕”的规则。
- 只需要快速设置样式时，优先用 V1.0：`style`、`font_size`、`position`。
- 需要控制字体、描边、阴影、背景或多语种字体文件时，使用 V2.0 并补齐 `config`、`fontFileName`、`subtitleLang`、`videoWidth`。
- 音色 ID 通过 [公共音色查询接口](./32-public-voice-characters.md) 获取。
- 经典模式下，无论 `voice_type=TTS` 还是 `voice_type=CLONE`，统一使用 `id_ve_voice_character`。
- `voice_type=TTS` 表示经典基础或经典高级音色；`voice_type=CLONE` 表示超真实音色。
- 不要用 `voice_type=CLONE` 判断情感克隆模式；情感克隆模式看 `wyTaskType=VOICE_CLONE_PRO`。
- `/edit/task/dubbing` 是新建配音任务，`needWyEdit` 始终传 `0`。
- 如果需要复用前序视频结果，先查任务 ID，再查 `/work/status` 取得 `body.content[].id`，填入 `materialWorkIds`。
- 使用字幕素材时，不要把翻译任务 ID 或上传临时 URL 填进 `idVeMaterialSrt`。
- 如果报角色音色与目标语种不匹配，应重新选择支持目标语种的音色。
