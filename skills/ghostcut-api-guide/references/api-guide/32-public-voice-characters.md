> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 公共音色查询接口

> 本文档说明 GhostCut 公共音色角色查询接口。经典模式的视频语音翻译与重新配音需要从该接口获取音色 ID，并填入 `wyVoiceParam.character_voices[].id_ve_voice_character`。无论 `voice_type=TTS` 还是 `voice_type=CLONE`，都统一使用 `id_ve_voice_character` 传参。

## 什么时候调用

当用户需要为[视频语音翻译与重新配音](./31-video-voice-translation.md)选择公共音色时，调用本接口。

常见场景：

- 按目标语言查找可用音色，例如英语、日语、韩语。
- 按声音类型筛选经典基础、经典高级或超真实音色。
- 按性别、年龄段筛选音色。
- 获取音色试听音频 `demoUrl`，供用户挑选。
- 获取音色角色 ID，并填入 `wyVoiceParam.character_voices[].id_ve_voice_character`。

## 接口信息

接口前缀：

```text
gateway/ve/voicecharacter
```

聚合查询接口：

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/voicecharacter/aggregate/list
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

该接口需要 `AppKey` 和 `AppSign` 签名。

## 认证

鬼手剪辑 API 使用 `AppKey` + `AppSign` 进行鉴权。`AppSign` 的生成规则为双重 MD5：

1. 将请求参数序列化为 JSON 字符串。
2. 对 JSON 字符串做一次 MD5，得到 `body_md5hex`。
3. 将 `body_md5hex + AppSecret` 拼接后再次做 MD5，得到最终的 `AppSign`。

> 注意：用于签名的 JSON 字符串需要和实际发送的请求体保持一致，否则签名会校验失败。

## 通用返回结构

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `body` | `object` / `array` | 业务返回内容。可能是音色列表，也可能是按语言分组后的列表。 |
| `count` | `number` | 返回条数。不分组时为音色数量，按语言分组时为语言分组数量。 |
| `code` | `number` | 返回码。成功值按实际接口返回判断；调用示例兼容 `1000` 和 `200`。 |
| `msg` | `string` | 返回消息。 |
| `trace` | `string` | 链路追踪 ID。 |

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `number` | 否 | 音色角色 ID。 |
| `voiceType` | `number` | 否 | 声音类型。`0`：经典基础；`1`：经典高级；`2`：超真实。 |
| `voiceCharacterSex` | `number` | 否 | 性别。`0`：女；`1`：男。 |
| `voiceCharacterAge` | `number` | 否 | 年龄段。`0`：未分类；`1`：儿童；`2`：青年；`3`：中年；`4`：老年。 |
| `voiceCharacterLanguage` | `string` | 否 | 支持语言过滤，例如 `en`、`ja`、`ko`。 |
| `voiceCharacterLocale` | `string` | 否 | 语言地区或口音过滤，例如 `en-US`。 |
| `groupByLanguage` | `boolean` | 否 | 是否按语言分组返回。`true` 表示按语言分组，默认 `false`。 |

### `voiceType`、`voice_type` 与配音模式的关系

这几个概念容易混淆：

| 字段 | 出现位置 | 含义 |
| --- | --- | --- |
| `voiceType` | 本查询接口请求参数 | 用于筛选音色类型，`0` 经典基础、`1` 经典高级、`2` 超真实。 |
| `voice_type` | 配音任务的 `character_voices[]` | 提交经典模式配音任务时的音色类型，`TTS` 表示经典基础或经典高级，`CLONE` 表示超真实。 |
| `wyTaskType` | 配音任务参数 | 配音模式字段。`FULL` 表示经典模式，`VOICE_CLONE_PRO` 表示情感克隆模式。 |

规则：

- `voiceType` 只用于查询和筛选音色，不要原样填入配音任务的 `voice_type`。
- 经典模式中，无论 `voice_type=TTS` 还是 `voice_type=CLONE`，音色 ID 都填入 `id_ve_voice_character`。
- 如果要使用经典基础或经典高级音色，通常先用 `voiceType=0` 或 `voiceType=1` 查询候选音色，再在配音任务中填写 `voice_type=TTS` 和对应的 `id_ve_voice_character`。
- 如果要使用超真实音色，通常先用 `voiceType=2` 查询候选音色，再在配音任务中填写 `voice_type=CLONE` 和对应的 `id_ve_voice_character`。
- `voice_type=CLONE` 不等于情感克隆模式；它只是超真实音色类型，仍然属于经典模式。
- 情感克隆模式通过 `wyTaskType=VOICE_CLONE_PRO` 区分，不需要手动选择公共音色，也不需要传 `character_voices[]`。

### 取值映射速查

| 查询接口中的字段或取值 | 配音任务中的字段或动作 | 说明 |
| --- | --- | --- |
| `voiceType=0` 或 `voiceType=1` | `character_voices[].voice_type=TTS` | 经典基础、经典高级音色都按 `TTS` 提交。 |
| `voiceType=2` | `character_voices[].voice_type=CLONE` | 超真实音色按 `CLONE` 提交，但仍属于经典模式。 |
| `body[].id` | `character_voices[].id_ve_voice_character` | 音色角色 ID 的来源。 |
| `supportLanguageList[].voiceCharacterLanguage` | 校验目标语言 `lang` | 用于确认该音色是否支持目标语种，不直接写入 `character_voices[]`。 |
| `supportLanguageList[].voiceCharacterLocale` | 校验目标地区或口音 | 用于筛选或展示口音，不直接写入 `character_voices[]`。 |
| 需要手动为角色选择音色 | `wyTaskType=FULL`，并传 `character_voices[]` | 这是经典模式。 |
| 需要情感克隆 | `wyTaskType=VOICE_CLONE_PRO`，不传 `character_voices[]` | 不需要调用公共音色接口选择音色。 |

### 支持的语言过滤值

`voiceCharacterLanguage` 可使用以下语言代码：

```text
ar, bg, bn, cs, da, de, el, en, es, es-sa, fi, fil, fr, hi, hr, hu,
id, it, ja, km, ko, ms, nl, no, pl, pt, pt-br, ro, ru, sk, sl, sv,
ta, th, tr, uk, ur, vi, zh, zh-tw
```

### 支持的地区/口音过滤值

`voiceCharacterLocale` 可使用以下地区或口音代码：

```text
ar-SA, bg-BG, bn-IN, cs-CZ, da-DK, de-DE, el-GR, en-AU, en-CA,
en-GB, en-IN, en-US, en-ZA, es-CO, es-ES, es-MX, es-SA, fi-FI,
fil-PH, fr-FR, hi-IN, hr-HR, hu-HU, id-ID, it-IT, ja-JP, km-KH,
ko-KR, ms-MY, nb-NO, nl-NL, pl-PL, pt-BR, pt-PT, ro-RO, ru-RU,
sk-SK, sl-SI, sv-SE, th-TH, tr-TR, uk-UK, ur-IN, vi-VN, zh-CN, zh-TW
```

## 请求示例

查询支持韩语的青年女性超真实音色：

```json
{
  "voiceCharacterLanguage": "ko",
  "voiceType": 2,
  "voiceCharacterSex": 0,
  "voiceCharacterAge": 2
}
```

查询英语美国口音音色：

```json
{
  "voiceCharacterLanguage": "en",
  "voiceCharacterLocale": "en-US"
}
```

按语言分组返回：

```json
{
  "groupByLanguage": true
}
```

## Python 调用示例

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
    sign = make_app_sign(body_str, APP_SECRET)
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


result = ghostcut_post("/v-w-c/gateway/ve/voicecharacter/aggregate/list", {
    "voiceCharacterLanguage": "en",
    "voiceType": 2,
    "voiceCharacterSex": 0,
})

for voice in result["body"]:
    print(voice["id"], voice.get("voiceCharacterNameEn"), voice.get("voiceCharacterNameZh"))
```

## 返回对象说明

### 音色角色对象

接口返回的音色角色对象可理解为 `GatewayVoiceCharacterAggregateVo`：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `number` | 音色角色 ID。填入配音任务时作为 `id_ve_voice_character` 的取值。 |
| `voiceType` | `number` | 声音类型。`0`：经典基础；`1`：经典高级；`2`：超真实。 |
| `voiceCharacterSex` | `number` | 性别。`0` 女，`1` 男。 |
| `voiceCharacterAge` | `number` | 年龄段。`0` 未分类，`1` 儿童，`2` 青年，`3` 中年，`4` 老年。 |
| `voiceCharacterNameZh` | `string` | 中文名称。 |
| `voiceCharacterNameEn` | `string` | 英文名称。 |
| `voiceCharacterNameBr` | `string` | 巴葡名称。 |
| `voiceCharacterDescZh` | `string` | 中文描述。 |
| `voiceCharacterDescEn` | `string` | 英文描述。 |
| `voiceCharacterDescBr` | `string` | 巴葡描述。 |
| `avatarUrl` | `string` | 头像 URL。 |
| `voiceLevelList` | `array` | 声音级别或标签列表。 |
| `supportLanguageList` | `array` | 支持语言及试听音频列表。 |

### 声音标签对象

`voiceLevelList` 中每一项表示一个声音标签：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `number` | 标签 ID。 |
| `significantDegree` | `number` | 标签显著程度。 |
| `voiceCharacterTagZh` | `string` | 标签中文名。 |
| `voiceCharacterTagEn` | `string` | 标签英文名。 |
| `voiceCharacterTagBr` | `string` | 标签巴葡名。 |

常见标签包括“清晰”“温柔”“活力”“日常对话”等，实际以接口返回为准。

### 支持语言与试听对象

`supportLanguageList` 中每一项表示该音色在某个语言或口音下的试听信息：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `number` | 语言记录 ID。 |
| `idVoice` | `number` | 关联声音 ID。 |
| `voiceCharacterLanguage` | `string` | 支持语言，例如 `en`、`ko`。 |
| `voiceCharacterLocale` | `string` | 地区或口音，例如 `en-US`。 |
| `demoText` | `string` | 试听文本。 |
| `demoUrl` | `string` | 试听音频 URL。可用于给用户预览声音。 |

## 在配音接口中使用

公共音色查询接口返回的音色角色对象 `id`，用于填充 `wyVoiceParam.character_voices[].id_ve_voice_character`。

示例：

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

字段说明：

| 字段 | 说明 |
| --- | --- |
| `character` | 角色名。未标注角色时通常使用 `role_default`。 |
| `voice_type` | `TTS` 或 `CLONE`。`TTS` 表示经典基础或经典高级音色，`CLONE` 表示超真实音色；当前两种类型都使用同一套 `id_ve_voice_character` 传参逻辑。 |
| `id_ve_voice_character` | 公共音色查询接口返回的音色角色对象 `id`。 |

## 选择音色建议

- 先根据视频语音翻译的目标语言 `lang` 查询 `voiceCharacterLanguage`。
- 如果需要特定口音，再传 `voiceCharacterLocale`，例如 `en-US`、`en-GB`。
- 按用户偏好筛选 `voiceCharacterSex` 和 `voiceCharacterAge`。
- 将候选音色的 `voiceCharacterNameZh` / `voiceCharacterNameEn`、`voiceCharacterDescZh` / `voiceCharacterDescEn`、标签和 `demoUrl` 展示给用户选择。
- 选择后，把音色角色对象 `id` 写入 `id_ve_voice_character`。

## Agent 决策规则

- 用户要做视频语音翻译、重新配音，并且没有指定音色 ID 时，先调用本接口查询公共音色。
- 只有经典模式需要为角色选择公共音色；情感克隆模式由 `wyTaskType=VOICE_CLONE_PRO` 触发，不需要调用本接口挑选角色音色。
- 查询公共音色时，优先按目标语言 `lang` 过滤 `voiceCharacterLanguage`。
- 如果用户指定“男声/女声/儿童/青年/中年/老年”，映射到 `voiceCharacterSex` 和 `voiceCharacterAge`。
- 返回结果里的音色角色对象 `id` 用于填写配音参数 `id_ve_voice_character`；`supportLanguageList[].id` 是语言记录 ID。
- 如果需要试听，使用 `supportLanguageList[].demoUrl`。
- 组装配音参数时，直接设置 `character_voices[].id_ve_voice_character`。
- 不要把 `voice_type=CLONE` 解释成情感克隆；它对应的是超真实音色。

## 相关文档

- [API 总览](./00-api-overview.md)：查看公共签名规则和功能选择入口。
- [视频语音翻译与重新配音](./31-video-voice-translation.md)：将查询到的 `id_ve_voice_character` 填入配音参数。
- [不同功能支持的语言列表](./90-language-support.md)：确认视频翻译目标语言 `lang` 的可用值。
