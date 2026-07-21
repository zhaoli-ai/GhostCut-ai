# 译制出海通用任务结构

> 译制出海的字幕提取、字幕擦除、AI 配音、字幕压制和音频分离共用同一套任务请求结构。具体任务差异只体现在 `videoEditParamsDto`、`workDto.extraOptions` 和 `wyVoiceParam` 的取值。

> [多作品合并](./64-series-video-merge.md)不适用本文结构。该接口使用 `clipParamMsRequest.idSeries` 和 JSON 字符串 `data.episodes[]`，不传 `items[]`、`workDto` 或 `videoEditParamsDto`。

> 说明：配音任务统一使用 `id_ve_voice_character` 传音色。

在组装本文结构前，必须先准备好项目和素材 ID：`idSeries` 来自项目创建或查询，`idMaterialVideo` 来自视频素材上传、导入或查询。AI 配音和字幕压制还需要准备 `idVeMaterialSrt`，它来自字幕素材上传、创建、字幕提取、字幕翻译、复制或查询。

## 适用接口

以下接口都使用本文说明的结构：

```text
gateway/ve/series/edit/task/subtitle/extract
gateway/ve/series/edit/task/subtitle/inpaint
gateway/ve/series/edit/task/dubbing
gateway/ve/series/edit/task/subtitle/burn
gateway/ve/series/edit/task/audio/separate
```

## 请求结构模板

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
        "workName": "demo.mp4"
      },
      "videoEditParamsDto": {
        "type": "WORK"
      }
    }
  ]
}
```

## Python 提交通用模板

译制出海剪辑任务都使用 `AppKey` + `AppSign` 签名。下面的函数可复用于字幕提取、字幕擦除、AI 配音、字幕压制和音频分离任务；不同任务只需要替换 `path` 和 `payload`。

```python
import hashlib
import json

import requests


APP_KEY = "your_app_key"
APP_SECRET = "your_app_secret"
BASE_URL = "https://api.zhaoli.com"


def dumps_body(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def make_app_sign(body_str: str, app_secret: str) -> str:
    body_md5hex = hashlib.md5(body_str.encode("utf-8")).hexdigest()
    return hashlib.md5((body_md5hex + app_secret).encode("utf-8")).hexdigest()


def ghostcut_post(path: str, payload: dict) -> dict:
    body_str = dumps_body(payload)
    headers = {
        "Content-Type": "application/json",
        "AppKey": APP_KEY,
        "AppSign": make_app_sign(body_str, APP_SECRET),
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
```

## 字段来源总表

| 字段或路径 | 从哪里获得 | 填到哪里 | 说明 |
| --- | --- | --- | --- |
| `idSeries` | [项目与视频素材](./60-series-project-and-video-materials.md) 的项目创建或项目列表。 | 顶层 `idSeries`、`workDto.idSeries`。 | 剧集或项目 ID，是译制出海任务的主上下文。 |
| `idMaterialVideo` | [项目与视频素材](./60-series-project-and-video-materials.md) 的视频上传、视频导入或视频列表。 | `items[].idMaterialVideo`。 | 视频素材 ID，必须与 `idSeries` 属于同一项目上下文。 |
| `idVeMaterialSrt` | [字幕素材管理](./61-series-subtitle-materials.md) 的字幕上传、创建、复制或字幕列表；也可来自字幕提取或字幕翻译后的字幕列表结果。 | `workDto.idVeMaterialSrt`，或作为源字幕 ID 参与字幕翻译。 | 字幕素材 ID。AI 配音和字幕压制中都必须与 `customer_input.content[]` 同时传。 |
| `task/list.body[].id` | [任务查询](./53-series-edit-task-list.md) 返回。 | 作为 `/v-w-c/gateway/ve/work/status` 的 project/task 查询 ID。 | 这是任务 ID，也可理解为 project id，不是作品 ID。 |
| `/work/status.body.content[].id` | 使用 `task/list.body[].id` 调用 [视频任务状态查询](./11-work-status-query.md) 后返回。 | 后续任务的 `workDto.materialWorkIds`。 | 这是作品 ID；需要复用字幕擦除、音频分离等前一步处理结果时使用。 |
| `id_ve_character` | 从字幕内容 `slInfo.sl[].id_ve_character` 提取；已接入角色列表时，也可从角色列表结果获取。 | `customer_input.content[].id_ve_character`、`character_voices[].id_ve_character`。 | 角色 ID，用于把字幕句子和经典模式音色配置关联起来。 |
| `character` | 从字幕内容 `slInfo.sl[].character` 提取；也可使用业务编辑后的角色名。 | `customer_input.content[].character`、`character_voices[].character`。 | 角色名应与 `id_ve_character` 对应。 |
| `id_ve_voice_character` | [公共音色查询接口](./32-public-voice-characters.md) 返回的音色角色对象 `body[].id`。 | `character_voices[].id_ve_voice_character`。 | 经典模式手动选音色时使用；`voice_type=TTS` 和 `voice_type=CLONE` 都使用该字段。 |
| `sourceLang` | 用户选择的原语种，或项目/素材上下文中的原语种。 | 顶层 `sourceLang`，必要时也填入 `videoEditParamsDto.sourceLang`。 | 原语种 code，例如 `zh`、`en`；无原语种任务按具体功能要求处理。 |
| `lang` | 用户选择的目标语种。 | 顶层 `lang`，必要时也填入 `videoEditParamsDto.lang` 和 `items[].overwriteLang`。 | 目标语种 code。AI 配音压字幕时还应与 `font_param.subtitleLang` 一致。 |
| `font_param.subtitleLang` | 通常直接使用目标语言 `lang`。 | `videoEditParamsDto.wyVoiceParam.font_param.subtitleLang`。 | `wyNeedText=1` 时使用，用于新字幕样式和字体匹配。 |
| `removeBgAudio` | 用户选择的原音处理策略。 | `videoEditParamsDto.removeBgAudio`。 | AI 配音任务需要传入；常见 `0` 保留原声和背景音，`1` 全局静音，`2` 去除音乐旋律并尽量保留人声/效果音。 |

提交任务前，视频素材应满足 `downloadStatus=1` 且 `processStatus=1`。否则任务可能因为素材仍在准备中失败。

## 顶层字段

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idSeries` | `Long` | 是 | 剧集 ID，来自项目创建或查询。 |
| `projectName` | `String` | 建议 | 任务名称，建议填写，方便后续查询。 |
| `callback` | `String` | 否 | 回调地址。生产接入推荐传入；回调格式、验签、重试和幂等规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。 |
| `sourceLang` | `String` | 视任务 | 原语种 code，例如 `zh`、`all`。 |
| `lang` | `String` | 视任务 | 目标语种 code，例如 `en`；无目标语种任务可传空字符串。 |
| `items` | `List` | 是 | 视频任务列表，每个元素对应一个待处理视频。 |
| `workDto` | `Object` | 否 | 顶层作品参数。如使用 `items`，通常放在 `items[]` 元素内。 |
| `videoEditParamsDto` | `Object` | 否 | 顶层剪辑参数。如使用 `items`，通常放在 `items[]` 元素内。 |
| `idWork` | `Long` | 否 | 基于已有作品发起任务时使用。 |
| `oldWanyinTaskId` | `String` | 否 | 复用已有配音任务时使用。 |
| `hidden` | `Byte` | 否 | 是否隐藏。 |

## `items[]` 字段

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idMaterialVideo` | `Long` | 是 | 素材视频 ID，来自视频素材上传、导入或查询。 |
| `idWork` | `Long` | 否 | 基于已有作品发起任务时使用。 |
| `newWanyinTaskId` | `String` | 否 | 新配音任务 ID。 |
| `oldWanyinTaskId` | `String` | 否 | 旧配音任务 ID。 |
| `workDto` | `Object` | 是 | 当前视频的作品参数。 |
| `videoEditParamsDto` | `Object` | 是 | 当前视频的剪辑任务参数。 |
| `overwriteSourceLang` | `String` | 否 | 覆盖当前作品原语种，主要影响显示；AI 配音新组装请求时可忽略。 |
| `overwriteLang` | `String` | 否 | 覆盖当前作品目标语种。AI 配音中传目标语言，通常与顶层 `lang` 一致；`wyNeedText=1` 时还要与 `font_param.subtitleLang` 一致。 |
| `overwriteExtraOption` | `String` | 否 | 覆盖扩展配置。 |

## `workDto` 常用字段

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `idSeries` | `Long` | 是 | 剧集 ID。 |
| `workName` | `String` | 建议 | 输出作品名称。 |
| `resolution` | `String` | 否 | 输出分辨率，例如 `1080p`。 |
| `duration` | `Number` | 否 | 视频时长，单位秒。 |
| `originalDuration` | `Number` | 否 | 原始视频时长，单位秒。 |
| `fileSize` | `Integer` | 否 | 文件大小。 |
| `idVeMaterialSrt` | `Long` | 配音/字幕压制常用 | 字幕素材 ID，来自字幕上传、创建、复制或查询。 |
| `materialWorkIds` | `String` | 否 | 复用已有作品结果，例如去文字后的视频作品 ID。 |
| `extraOptions` | `Object` / `String` | 否 | 扩展配置。 |
| `callback` | `String` | 否 | 回调地址，通常传顶层 `callback` 即可。 |

## `videoEditParamsDto` 常用字段

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `type` | `String` | 是 | 固定传 `WORK`。 |
| `needWanyin` | `Byte` | 视任务 | 是否启用配音能力，`1` 表示启用。 |
| `wyTaskType` | `String` | 视任务 | 配音任务类型，常见 `ONLY_ASR`、`FULL`、`VOICE_CLONE_PRO`、`NO_TTS`。配音模式中，`FULL` 表示经典模式，`VOICE_CLONE_PRO` 表示情感克隆模式。 |
| `wyNeedText` | `Byte` | 视任务 | 是否把新字幕压制到画面。AI 配音中 `1` 表示配音并压制新字幕，`0` 表示只重新配音、不压制新字幕。 |
| `needWyEdit` | `Byte` | 配音常用 | `/edit/task/dubbing` 表示发起新的配音任务，该字段始终传 `0`。 |
| `sourceLang` | `String` | 否 | 原语种。 |
| `lang` | `String` | 否 | 目标语种。 |
| `videoInpaintLang` | `String` | 去字/OCR 常用 | 去字或 OCR 语种。 |
| `needChineseOcclude` | `Byte` | 去字/OCR 常用 | 去字或 OCR 模式。 |
| `videoInpaintMasks` | `List` / `String` | 否 | 去字或 OCR 区域。AI 配音最小请求体不包含该字段；如果配音前需要处理原视频硬字幕，应先创建字幕擦除任务，再在配音任务中用 `workDto.materialWorkIds` 复用擦除后的作品。 |
| `videoInpaintMasks_lite` | `List` | 否 | Lite 去字区域。 |
| `videoInpaintMasks_pro` | `List` | 否 | Pro 去字区域。 |
| `vtrMode` | `String` | 否 | 去字模式，例如 `lite`。 |
| `vtrProModel` | `String` | 否 | Pro 模型，例如 `advanced`。 |
| `wyVoiceParam` | `Object` | 配音/字幕压制常用 | 字幕样式与角色音色配置。 |
| `removeBgAudio` | `Byte` | 配音/音频分离常用 | 原音处理方式。AI 配音任务需要传入；常用 `0` 保留原声和背景音，`1` 全局静音，`2` 去除音乐旋律并尽量保留人声/效果音。音频分离固定传 `2`。 |
| `rhythmParam` | `String` | 否 | 节奏参数，不使用可传空字符串。 |

## `workDto.extraOptions.customer_input`

配音和字幕压制任务可使用 `customer_input` 传入台词内容。译制出海 AI 配音和字幕压制中，`workDto.idVeMaterialSrt` 和 `workDto.extraOptions.customer_input.content[]` 都要传。

```json
{
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
```

常见字段说明：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `prefix` | `String` | 台词内容前缀或批次标识。 |
| `content[].start` | `Number` | 台词开始时间，单位秒。 |
| `content[].end` | `Number` | 台词结束时间，单位秒。 |
| `content[].source` | `String` | 原文台词。 |
| `content[].translation` | `String` | 译文或要压制的字幕文本。 |
| `content[].character` | `String` | 角色名。 |
| `content[].id_ve_character` | `Long` | 角色 ID。 |
| `content[].manualModify` | `Boolean` | 是否为手动修改内容。 |
| `content[].audio_type` | `String` | 单句发音策略。枚举：`TTS` 系统 AI 配音，`Mute` 静音不配音，`RAW_VOCAL` 保留原片人声。 |

如果输入数据中出现 `content[].use_for_clone`，组装新请求时不要依赖该字段，也不要用它判断情感克隆模式。情感克隆模式以 `wyTaskType=VOICE_CLONE_PRO` 为准。

## `wyVoiceParam.font_param`

字幕样式配置示例：

```json
{
  "style": "n-4-T",
  "font_size": 40,
  "position": 0.73,
  "videoWidth": 622,
  "config": {
    "subtitleAreaWidth": 0.9,
    "fontFamily": "NotoSans",
    "fontStyleItalic": false,
    "fontWeightBold": true,
    "textAlign": "center",
    "lineSpace": 5,
    "bgType": 0,
    "strokeLineWidth": 2,
    "strokeStyle": "#FA8B80",
    "shadowColor": "rgba(0, 0, 0, 0)",
    "shadowOffsetX": 1,
    "shadowOffsetY": 1,
    "shadowBlur": 1,
    "bgH": 0,
    "bgW": 0,
    "bgR": 0,
    "bgPaddingY": 4,
    "fillStyle": "#FEFAFE"
  },
  "subtitleLang": "en",
  "fontFileName": "NotoSans-Bold.ttf"
}
```

## `wyVoiceParam.character_voices[]`

`character_voices[]` 只用于经典模式。经典模式表示手动为角色选择音色，必须使用 `wyTaskType=FULL`。

角色音色配置示例：

```json
[
  {
    "character": "Narrator",
    "id_ve_character": 100001,
    "voice_type": "TTS",
    "id_ve_voice_character": 200001
  }
]
```

字段说明：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `character` | `String` | 角色名称。 |
| `id_ve_character` | `Long` | 角色 ID。 |
| `voice_type` | `String` | 音色类型，常见 `TTS`、`CLONE`。`TTS` 表示经典基础或经典高级音色；`CLONE` 表示超真实音色。 |
| `id_ve_voice_character` | `Long` | 当前统一使用的音色 ID。无论 `voice_type=TTS` 还是 `voice_type=CLONE`，都使用该字段传参。 |

不要把 `voice_type=CLONE` 理解成情感克隆模式。情感克隆模式传 `wyTaskType=VOICE_CLONE_PRO`，不需要传 `character_voices[]`。

## 复用已有作品结果

如果一个后续任务要使用前一步任务生成的视频，例如“先去文字，再压制字幕”，需要在后续任务的 `workDto` 中增加：

```json
{
  "workDto": {
    "materialWorkIds": "50001"
  }
}
```

`materialWorkIds` 用于复用已有作品结果，不是视频素材 ID。查询前一步任务结果时，先找到对应的最新任务记录，读取 `task/list` 返回对象 `body[].id` 作为任务 ID；再按[视频任务状态查询](./11-work-status-query.md)的方式调用 `/work/status` 查询该任务下的作品详情，读取 `body.content[].id` 作为作品 ID，并填入后续任务的 `workDto.materialWorkIds`。该作品必须可用，否则会出现业务校验失败。

## 相关文档

- [译制出海剪辑 API 总览](./51-series-overview.md)：查看模块流程和任务选择规则。
- [项目与视频素材](./60-series-project-and-video-materials.md)：准备 `idSeries` 和 `idMaterialVideo`。
- [字幕素材管理](./61-series-subtitle-materials.md)：准备 `idVeMaterialSrt`，并在需要时解析 `slInfo.sl[]` 组装 `customer_input.content[]`。
- [任务查询](./53-series-edit-task-list.md)：提交任务后查询处理状态。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试、幂等和补偿轮询规则。
- [错误与检查清单](./59-series-edit-errors-and-checklist.md)：提交前检查参数完整性。

## Agent 决策规则

- 本文覆盖的五类任务以 `items[]` 为核心；每个视频一个 `items[]` 元素。
- 上述规则只适用于本文列出的五类任务；多作品合并必须使用其独立的 `data.episodes[]` 结构。
- 本模块任务为异步处理；生产接入推荐传入顶层 `callback` 接收结果，轮询作为查询和补偿兜底。
- 先拿真实 ID，再组装任务；不要用项目名、视频 URL 或字幕文件名代替 ID。
- `idSeries` 和 `items[].idMaterialVideo` 必须属于同一个项目上下文；如果使用 `workDto.idVeMaterialSrt`，该字幕素材也必须属于同一项目上下文。
- AI 配音和字幕压制任务中，必须同时传 `workDto.idVeMaterialSrt` 和 `workDto.extraOptions.customer_input.content[]`；`idVeMaterialSrt` 绑定字幕素材上下文，`customer_input.content[]` 明确本次使用的逐句内容。
- `videoEditParamsDto.type` 固定传 `WORK`。
- 普通任务参数优先放到 `items[]` 元素内的 `workDto` 和 `videoEditParamsDto`，不要同时在顶层和 `items[]` 元素内重复放不一致的值。
- `sourceLang`、`lang` 可以在顶层和 `videoEditParamsDto` 中同时出现，确保二者语义一致。
- 本模块示例中，`workDto.extraOptions`、`videoEditParamsDto.wyVoiceParam` 可直接传对象；去字或 OCR 任务中的 `videoEditParamsDto.videoInpaintMasks` 可直接传数组。不要默认套用普通单视频接口里的 JSON 字符串写法。译制出海 AI 配音前先判断原素材是否已无硬字幕、是否已通过 `materialWorkIds` 复用字幕擦除后作品；如果两者都不是，应询问用户是否需要先创建字幕擦除任务。
- 配音模式分为经典模式和情感克隆模式：经典模式使用 `wyTaskType=FULL` 并手动传 `character_voices[]`；情感克隆模式使用 `wyTaskType=VOICE_CLONE_PRO`，不要把 `voice_type=CLONE` 当成情感克隆模式。
- 不要把 `task/list` 的 `body[].id` 直接当成作品 ID；它是任务 ID，需要再调用 `/work/status` 查询。
- 不要用 `idMaterialVideo` 代替 `workDto.materialWorkIds`。
