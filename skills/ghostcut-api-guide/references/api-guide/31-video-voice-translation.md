> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 视频语音翻译与重新配音

> 鬼手剪辑 API 可对视频进行翻译并重新配音，支持 ASR 自动识别或外挂 SRT 字幕，并支持音画自动重新对齐。

## 调用流程

一次完整的视频语音翻译流程包含以下步骤：

1. **准备视频资源**
   如果视频已经可以通过公网 URL 访问，可直接使用该 URL。如果只有本地视频文件，先调用[文件上传 API](./10-file-upload.md)上传视频，获取临时 URL。

2. **准备配音音色**
   经典模式需要在 `wyVoiceParam.character_voices` 中配置目标语种音色，并使用 `wyTaskType=FULL`。公共声音可通过[公共音色查询接口](./32-public-voice-characters.md)获取音色角色 ID，并填入 `id_ve_voice_character`。情感克隆模式通过 `wyTaskType=VOICE_CLONE_PRO` 开启，不需要手动为角色选择音色。

3. **创建语音翻译任务**
   调用 `/v-w-c/gateway/ve/work/free`，传入视频 URL、源语言、目标语言、配音参数和可选字幕输入。接口返回成功后，从 `body.dataList[0].id` 中获取作品 ID。

4. **查询任务状态**
   按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`，传入作品 ID 列表 `idWorks`。处理成功后，响应中会返回 `processStatus` 和结果视频 URL。

5. **下载处理后的视频**
   当 `processStatus` = `1` 时，表示任务处理成功，可以使用返回的视频 URL 下载已翻译并重新配音的视频。

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

### 2. 创建语音翻译任务

以下示例表示：中文视频翻译成英文，使用 AI 配音，并把译后字幕压制到画面中。

```python
wy_voice_param = {
    "character_voices": [
        {
            "character": "role_default",
            "voice_type": "TTS",
            "id_ve_voice_character": 10709,
        }
    ],
    "font_param": {
        "style": "tpl-31-1-T",
        "font_size": 32,
        "position": 0.727,
    },
}

extra_options = {
    "subtitle_format": "srt",
    "extra_video_translate_config": {
        "video_speedup_on": True,
    },
}

task_payload = {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "needWanyin": 1,
    "sourceLang": "zh",
    "lang": "en",
    "wyTaskType": "FULL",
    "wyNeedText": 1,
    "removeBgAudio": 1,
    "wyVoiceParam": json.dumps(wy_voice_param, ensure_ascii=False, separators=(",", ":")),
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
| `needWanyin` | `number` | 是 | 配音功能总开关，语音翻译场景固定传 `1`。 |
| `sourceLang` | `string` | 是 | 源语言，视频原语种代码，例如中文传 `zh`。 |
| `lang` | `string` | 是 | 目标语言，需要翻译成的语种代码，例如英文传 `en`。 |
| `wyTaskType` | `string` | 是 | 语音任务处理类型。常用 `FULL` 表示 ASR 提取、翻译、AI 新配音完整处理。 |
| `wyNeedText` | `number` | 是 | 新字幕展示开关。`0`：不把译后字幕合成到画面中；`1`：开启新字幕画面合成。 |
| `removeBgAudio` | `number` | 否 | 背景音处理策略。`0`：保留背景音；`1`：全局静音，仅保留新 AI 语音；`2`：去除音乐旋律，仅保留环境效果音。 |
| `wyVoiceParam` | `string` | 是 | JSON 字符串，配置角色配音和字幕样式。 |
| `extraOptions` | `string` | 否 | JSON 字符串，配置外挂字幕、音画对齐、OCR 调优、精准时间轴等。 |

## 语音任务类型

`wyTaskType` 控制语音翻译任务的处理方式：

| 值 | 说明 |
| --- | --- |
| `FULL` | 经典模式完整处理：ASR 提取、翻译、AI 新配音，需要手动配置角色音色。 |
| `VOICE_CLONE_PRO` | 情感克隆模式。系统自动复刻原视频声线和情感，不需要手动配置角色音色。 |
| `NO_TTS` | 不配音，保留原视频声音。选此项时 `removeBgAudio` 只能传 `2` 或不传。 |
| `NO_TTS_VOCAL` | 不配音且去人声，仅保留原视频背景音。 |
| `ONLY_ASR` | 仅执行 ASR 提取字幕，不执行配音。独立用法参考 [ASR 提取视频字幕](./25-asr-subtitle-extraction.md)。 |

## `wyVoiceParam` 配音与字幕配置

`wyVoiceParam` 控制最终的听感和观感，主要包含 `character_voices` 和 `font_param`。

### 音色来源与角色规则

- 配音模式分为经典模式和情感克隆模式。
- 经典模式：手动为角色选择音色，必须使用 `wyTaskType=FULL`，并配置 `wyVoiceParam.character_voices[]`。
- 情感克隆模式：传 `wyTaskType=VOICE_CLONE_PRO`，系统自动复刻原视频声线和情感，不需要配置 `character_voices[]`。
- 经典模式下，`voice_type` 常见为 `TTS` 和 `CLONE`。
- `voice_type=TTS` 表示经典基础或经典高级音色。
- `voice_type=CLONE` 表示超真实音色，它仍然属于经典模式，不等于情感克隆模式。
- 音色 ID 统一通过 [公共音色查询接口](./32-public-voice-characters.md) 获取，并填写到 `id_ve_voice_character`。
- 无论 `voice_type=TTS` 还是 `voice_type=CLONE`，都统一使用 `id_ve_voice_character`。
- 纯 AI 自动识别模式 `wyTaskType="FULL"` 下，系统默认将提取出的所有台词归属于 `role_default`。单人配音通常只需配置一个 `role_default`。
- 如果通过 `extraOptions.customer_input` 传入精细台词时间轴，并在台词级别标记了 `character`，必须在 `character_voices` 中为对应角色显式绑定声音 ID。
- 如果希望系统自动复刻原视频声线和情感，使用情感克隆模式，传 `wyTaskType=VOICE_CLONE_PRO`。此时字幕可传可不传；不传时默认通过 ASR 提取原台词。

情感克隆模式的请求体关键片段如下，不需要传 `wyVoiceParam.character_voices[]`：

```json
{
  "wyTaskType": "VOICE_CLONE_PRO",
  "wyVoiceParam": "{\"font_param\":{\"style\":\"tpl-31-1-T\",\"font_size\":32,\"position\":0.727}}"
}
```

### 场景 1：配音并压制译后字幕

适合“配音剧”类任务，同时生成 AI 新配音，并将译后字幕渲染到画面中。

```json
{
  "character_voices": [
    {
      "character": "role_default",
      "voice_type": "TTS",
      "id_ve_voice_character": 10709
    }
  ],
  "font_param": {
    "style": "tpl-31-1-T",
    "font_size": 32,
    "position": 0.727
  }
}
```

### 场景 2：只要画面字幕，不要配音

适合“字幕剧”类任务，需要配合 `wyTaskType="NO_TTS"`。

```json
{
  "font_param": {
    "style": "tpl-31-1-T",
    "font_size": 32,
    "position": 0.727
  }
}
```

### 场景 3：只要配音，不压制字幕

适合只替换声音、不把字幕合成到画面中的任务，需要传 `wyNeedText=0`。

```json
{
  "character_voices": [
    {
      "character": "role_default",
      "voice_type": "TTS",
      "id_ve_voice_character": 10709
    }
  ]
}
```

## `extraOptions` 额外配置

`extraOptions` 主要用于外挂开发者自有字幕、控制音画对齐、调整 OCR 识别策略，或精准注入台词时间轴。

```json
{
  "subtitle_format": "vtt",
  "extra_video_translate_config": {
    "video_speedup_on": true
  },
  "extra_inpaint_config": {
    "subtitle_infer_on": true,
    "auto_correct_on": false,
    "strip_last_punct_on": false,
    "scene_filter_on": true
  },
  "customer_input_srt": {
    "source": "https://example.com/source.srt",
    "translation": "https://example.com/trans.srt"
  },
  "customer_input": {
    "content": [
      {
        "start": 11.18,
        "end": 12.099,
        "source": "珺珺",
        "translation": "Jun",
        "character": "角色A",
        "render_on": true,
        "audio_type": "TTS"
      }
    ]
  }
}
```

字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `subtitle_format` | `string` | 导出附加字幕文件格式，不传默认 `srt`，也可传 `vtt`。 |
| `extra_video_translate_config.video_speedup_on` | `boolean` | 是否开启画面自动调速。默认 `true`，用于达到更好的视听同步效果；设为 `false` 时视频时长保持和原素材一致。 |
| `extra_inpaint_config.subtitle_infer_on` | `boolean` | 字幕推断开关，适用于长时间停留在某区域的文字。 |
| `extra_inpaint_config.auto_correct_on` | `boolean` | OCR 自动校准开关，默认关闭。 |
| `extra_inpaint_config.strip_last_punct_on` | `boolean` | 是否去除句末标点，默认关闭。 |
| `extra_inpaint_config.scene_filter_on` | `boolean` | 场景文字过滤开关，默认开启。 |
| `customer_input_srt.source` | `string` | 原文 SRT 链接。只传 `source` 时，系统会自动翻译并配音。 |
| `customer_input_srt.translation` | `string` | 译文 SRT 链接。若同时传 `source` 和 `translation`，系统会跳过翻译，直接使用 `translation` 中的台词进行压制和配音；两者句子必须一一对应。 |
| `customer_input.content` | `array` | 精准注入台词时间轴。传入后会跳过 ASR/OCR 识别，完全信任传入的时间轴和台词。 |

`customer_input.content` 单句字段说明：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `start` | `number` | 开始时间，单位秒。 |
| `end` | `number` | 结束时间，单位秒。 |
| `source` | `string` | 原文。 |
| `translation` | `string` | 译文。 |
| `character` | `string` | 指定角色名，需与 `wyVoiceParam.character_voices[].character` 对应。 |
| `render_on` | `boolean` | `true`：渲染到画面；`false`：仅发音不渲染。 |
| `audio_type` | `string` | 发音策略。`TTS`：系统 AI 配音；`Mute`：静音去人声；`RAW_VOCAL`：保留原人声。 |

## 查询任务状态

创建任务拿到 `work_id` 后，按[视频任务状态查询](./11-work-status-query.md)调用 `/v-w-c/gateway/ve/work/status`。本功能在 `processStatus == 1` 时优先读取 `videoUrl`；如果还需要独立字幕文件，再检查返回内容中的字幕 URL 字段。若 `processStatus > 1`，按[视频处理状态枚举](./14-video-process-status.md)排查失败原因。生产接入推荐使用 `callback` 接收结果，轮询作为查询和补偿兜底，规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。

## 完整示例

以下示例展示了从创建视频语音翻译任务到轮询获取结果视频的完整流程。

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
    "character_voices": [
        {
            "character": "role_default",
            "voice_type": "TTS",
            "id_ve_voice_character": 10709,
        }
    ],
    "font_param": {
        "style": "tpl-31-1-T",
        "font_size": 32,
        "position": 0.727,
    },
}

extra_options = {
    "subtitle_format": "srt",
    "extra_video_translate_config": {
        "video_speedup_on": True,
    },
}

task = api_post("/v-w-c/gateway/ve/work/free", {
    "urls": ["https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4"],
    "needWanyin": 1,
    "sourceLang": "zh",
    "lang": "en",
    "wyTaskType": "FULL",
    "wyNeedText": 1,
    "removeBgAudio": 1,
    "wyVoiceParam": json.dumps(wy_voice_param, ensure_ascii=False, separators=(",", ":")),
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

## Agent 决策规则

- 用户要“翻译视频并重新配音”“视频语音翻译”“译制视频”时，优先使用本功能。
- 本功能为异步任务；生产接入推荐使用 `callback` 接收结果，轮询作为查询和补偿兜底。
- 默认经典模式完整配音链路使用 `needWanyin=1`、`wyTaskType=FULL`，并配置 `sourceLang`、`lang`、`wyVoiceParam.character_voices`。
- 如果用户只要配音不要画面字幕，传 `wyNeedText=0`，`wyVoiceParam` 可以只包含 `character_voices`。
- 如果用户既要配音又要压制译后字幕，传 `wyNeedText=1`，`wyVoiceParam` 同时包含 `character_voices` 和 `font_param`。
- 如果用户提供了原文/译文 SRT，放到 `extraOptions.customer_input_srt`；同时传 `source` 和 `translation` 时，系统会跳过翻译。
- 如果用户提供逐句时间轴，放到 `extraOptions.customer_input.content`，并确保 `character` 与 `wyVoiceParam.character_voices` 对应。
- 经典模式需要手动选择角色音色；`voice_type=TTS` 表示经典基础或经典高级音色，`voice_type=CLONE` 表示超真实音色。
- 情感克隆模式通过 `wyTaskType=VOICE_CLONE_PRO` 区分，不要把 `voice_type=CLONE` 当作情感克隆模式。
- 查询结果时优先读取 `videoUrl` 获取完成后的视频；如需独立字幕文件，再检查接口返回中的字幕 URL 字段。

## 相关文档

- [API 总览](./00-api-overview.md)：查看功能选择入口和主要调用流程。
- [API 凭证与签名](./02-auth-and-sign.md)：查看公共签名规则和常见鉴权错误。
- [文件上传](./10-file-upload.md)：本地视频或本地 SRT 需要先上传并获得临时 URL。
- [公共音色查询接口](./32-public-voice-characters.md)：没有指定音色 ID 时，先查询公共音色并获取 `id_ve_voice_character`。
- [字幕样式和字体配置补充](./26-subtitle-style-and-fonts.md)：配置译后字幕的字体、描边、阴影和背景。
- [不同功能支持的语言列表](./13-language-support.md)：确认 `sourceLang` 和 `lang` 的可用值。
- [视频任务状态查询](./11-work-status-query.md)：查询作品处理状态并读取 `videoUrl`。
- [视频处理状态枚举](./14-video-process-status.md)：根据 `processStatus` 判断是否成功、继续轮询或失败。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试和幂等规则。
