> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 字幕样式和字体配置补充

> 本文档说明 GhostCut 字幕样式配置方式，主要用于[为视频压制字幕](./22-burn-subtitles.md)和[视频语音翻译与重新配音](./31-video-voice-translation.md)中的新字幕渲染。字幕样式统一通过 `wyVoiceParam` JSON 字符串下的 `font_param` 节点控制。

## 适用场景

当接口参数中需要传 `wyVoiceParam`，且希望控制画面字幕样式时，使用本文档。

常见场景：

- 字幕压制：将用户提供的 SRT 字幕硬压制到视频画面中。
- 视频语音翻译：翻译视频并重新配音，同时把译后字幕压制到画面中。
- 只压字幕不配音：`wyTaskType="NO_TTS"` 且 `wyNeedText=1`。
- 配音并显示新字幕：`wyTaskType="FULL"` 且 `wyNeedText=1`。

## V1.0 字幕样式

V1.0 只支持三类基础配置：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `style` | `string` | 字幕样式 code。 |
| `font_size` | `number` | 字体大小，单位 px，会根据视频画布尺寸缩放。 |
| `position` | `number` | 字幕区域上沿在画布 Y 轴的位置，范围通常为 `0` 到 `1`。 |

常用 V1.0 样式 code：

| 样式 code | 说明 |
| --- | --- |
| `n-1-T` | 基础白字描边样式。 |
| `n-2-T` | 黑字白描边样式。 |
| `n-3-T` | 黄字黑描边样式。 |
| `n-4-T` | 白字彩色描边样式。 |
| `n-5-T` | 蓝字黑描边样式。 |
| `tpl-14-1-T` | 黄字黑描边并带阴影。 |
| `tpl-30-1-T` | 蓝色背景白字样式。 |
| `tpl-31-1-T` | 黑色圆角背景白字样式，常用于字幕压制。 |
| `tpl-33-1-T` | 三色线框背景样式。 |
| `tpl-37-1-T` | 双矩形背景样式。 |
| `tpl-129-1-T` | 绿色圆角背景白字样式。 |
| `tpl-186-2-T` | 白字棕色描边样式。 |
| `tpl-193-2-T` | 黄色圆角背景黑字样式。 |

V1.0 参数示例：

```json
{
  "font_param": {
    "style": "tpl-31-1-T",
    "font_size": 32,
    "position": 0.8
  }
}
```

如果同一个 `wyVoiceParam` 还要配置配音角色，可同时包含 `character_voices`：

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

## 字号缩放规则

`font_size` 不是直接按传入值原样渲染，而是会根据视频宽高做缩放。

计算逻辑可理解为：

```text
实际渲染字号 = round(font_size / 720 * min(min(video_width, video_height), 1080))
```

建议：

- 720p 基准下，常用字号可从 `30` 到 `50` 之间选择。
- 横屏视频常用 `32` 左右。
- 竖屏短视频可适当增大，但仍需避免字幕区域过宽导致频繁换行。
- 如果字幕太靠下或遮挡画面内容，可调整 `position`，例如 `0.72` 到 `0.82`。

## V2.0 字幕样式

V2.0 在 V1.0 的 `style`、`font_size`、`position` 基础上，增加了更细的配置项：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `style` | `string` | 是 | 样式 code。 |
| `font_size` | `number` | 是 | 字体大小。 |
| `position` | `number` | 是 | 字幕区域上沿位置。 |
| `config` | `object` | 是 | 字幕样式细项配置，例如字体、描边、阴影、背景等。 |
| `fontFileName` | `string` | 是 | 字体文件名，例如 `NotoSans-Bold.ttf`。 |
| `subtitleLang` | `string` | 是 | 字幕语种，例如 `en`、`zh`、`ja`。 |
| `videoWidth` | `number` | 是 | 前端编辑显示画布宽度，通常可用视频宽度像素值代替。 |

V2.0 完整示例：

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

## `config` 可调整字段

`config` 中可能存在很多默认字段。通过默认配置生成的字段尽量不要随意删除；通常只调整下表列出的字段。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `fontFamily` | `string` | 字体名，例如 `NotoSans`。 |
| `fontWeightBold` | `boolean` | 是否加粗。 |
| `fontStyleItalic` | `boolean` | 是否倾斜。 |
| `textAlign` | `string` | 对齐方式，通常为 `center`。 |
| `lineSpace` | `number` | 行间距，单位 px。 |
| `fillStyle` | `string` | 字体填充颜色，例如 `#FFFFFF`。 |
| `strokeLineWidth` | `number` | 描边宽度，单位 px。 |
| `strokeStyle` | `string` | 描边颜色。 |
| `shadowColor` | `string` | 阴影颜色。传 `rgba(..., 0)` 可关闭阴影。 |
| `shadowOffsetX` | `number` | 阴影水平偏移。 |
| `shadowOffsetY` | `number` | 阴影垂直偏移。 |
| `shadowBlur` | `number` | 阴影模糊程度。 |
| `bgType` | `number` | 背景类型。 |
| `subtitleAreaWidth` | `number` | 字幕区域宽度占视频宽度的比例，例如 `1` 表示占满，`0.54` 表示占 54%。 |

`subtitleAreaWidth` 不要设置得过小。区域太窄会导致字幕自动换行；如果自动换行不理想，应优先在字幕文本中手动添加换行符。

## 背景类型

V2.0 支持多种背景类型：

| `bgType` | 说明 | 额外配置 |
| --- | --- | --- |
| `0` | 无背景 | 不需要额外字段。 |
| `2` | 纯色背景，单行圆角矩形，多行时整个区域是一整块背景 | `bgColors`、`bgR`、`bgPaddingY` |
| `3` | 两个矩形背景 | `bgColors`、`bgW`、`bgPadding` |
| `4` | 三色线框背景 | `bgColors`、`bgPadding`、`bgH`、`bgRW` |

`bgType=2` 示例：

```json
{
  "bgType": 2,
  "bgColors": ["#000000"],
  "bgR": 3,
  "bgPaddingY": 6
}
```

`bgType=3` 示例：

```json
{
  "bgType": 3,
  "bgColors": ["#000000", "#25F4EE", "#FE2C55"],
  "bgW": 3,
  "bgPadding": [10, 4, 8, 1]
}
```

`bgType=4` 示例：

```json
{
  "bgType": 4,
  "bgColors": ["#ffffff", "#25F4EE", "#000000", "#FE2C55"],
  "bgPadding": [8, 4, 6, 1],
  "bgH": 5,
  "bgRW": 0.3
}
```

## 字体和字体文件

V2.0 需要同时指定 `fontFamily` 和 `fontFileName`。

规则：

- `fontFamily` 表示字体族，例如 `NotoSans`、`Roboto`、`Montserrat`。
- `fontFileName` 表示实际字体文件名，例如 `NotoSans-Bold.ttf`。
- 字体文件可通过 `https://p.cdn.izhaoli.cn/font/{fontFileName}` 访问。
- 如果某个字体渲染异常，优先换用其他字体文件。
- 如需增加字体，需要联系 GhostCut。

字体文件 URL 示例：

```text
https://p.cdn.izhaoli.cn/font/NotoSans-Bold.ttf
```

常用字体：

| 字体 | 适用说明 |
| --- | --- |
| `NotoSans` | 通用字体，支持多语种，建议默认使用。 |
| `Noto_Serif` | 通用衬线字体。 |
| `Roboto` | 常用西文字体。 |
| `Montserrat` | 常用西文字体。 |
| `Open_Sans` | 常用西文字体，但不建议用于 `bn`、`ur`。 |
| `M_PLUS_1p` / `M_PLUS_Rounded_1c` / `Shippori_Mincho` | 日语可用字体。 |
| `Hahmlet` / `Nanum_Myeongjo` | 韩语可用字体。 |
| `Fahkwang` / `Kanit` / `Sarabun` / `Prompt` | 泰语可用字体。 |
| `Amiri` / `Noto_Sans_Arabic` / `Almarai` | 阿拉伯语、乌尔都语可用字体。 |
| `Hind` / `Mukta` / `Kalam` | 印地语可用字体。 |
| `HindSiliguri` | 孟加拉语可用字体。 |
| `MiSans` / `SmileySans` / `Alimama_ShuHeiTi` 等 | 中文可用字体。 |

## 字体文件名计算规则

计算 `fontFileName` 时，需要考虑字体名、字幕语种和是否加粗。

基本规则：

```text
fontFileName = 字体基础文件名 + ("-Bold.ttf" 或 "-Regular.ttf")
```

例如：

| 输入 | 输出 |
| --- | --- |
| `fontFamily=NotoSans`, `subtitleLang` 为空，`fontWeightBold=false` | `NotoSans-Regular.ttf` |
| `fontFamily=NotoSans`, `subtitleLang=ja`, `fontWeightBold=true` | `NotoSansJP-Bold.ttf` |
| `fontFamily=NotoSans`, `subtitleLang=zh`, `fontWeightBold=true` | `NotoSansTC-Bold.ttf` |
| `fontFamily=Noto_Serif`, `subtitleLang=ko`, `fontWeightBold=false` | `NotoSerifKR-Regular.ttf` |

常见特殊映射：

| 字体 + 语种 | 字体基础文件名 |
| --- | --- |
| `NotoSans_zh` / `NotoSans_zh-hant` | `NotoSansTC` |
| `NotoSans_ja` | `NotoSansJP` |
| `NotoSans_ko` | `NotoSansKR` |
| `NotoSans_km` | `NotoSansKhmer` |
| `NotoSans_th` | `NotoSansThai` |
| `NotoSans_ar` / `NotoSans_ur` | `NotoSansArabic` |
| `NotoSans_bn` | `NotoSansBengali` |
| `Noto_Serif_zh` / `Noto_Serif_zh-hant` | `NotoSerifTC` |
| `Noto_Serif_ja` | `NotoSerifJP` |
| `Noto_Serif_ko` | `NotoSerifKR` |
| `Noto_Serif_bn` | `NotoSerifBengali` |
| `Noto_Serif_th` | `NotoSerifThai` |

## 根据样式 code 构造 V2.0 默认配置

V1.0 样式可以视为 V2.0 某些默认配置的组合。需要精细控制时，可以先按样式 code 生成默认 `config`，再只修改需要微调的字段。

常用默认配置思路：

```python
def build_font_param_config(style: str) -> dict:
    base = {
        "subtitleAreaWidth": 0.9,
        "fontFamily": "NotoSans",
        "fontStyleItalic": False,
        "fontWeightBold": False,
        "textAlign": "center",
        "lineSpace": 5,
        "bgType": 0,
        "strokeLineWidth": 0,
        "strokeStyle": "#301000",
        "shadowColor": "rgba(0, 0, 0, 0)",
        "shadowOffsetX": 1,
        "shadowOffsetY": 1,
        "shadowBlur": 1,
        "bgH": 0,
        "bgW": 0,
        "bgR": 0,
        "bgPaddingY": 4,
    }

    presets = {
        "n-1-T": {
            "fillStyle": "#FFFFFF",
            "strokeLineWidth": 2,
            "strokeStyle": "#010101",
            "fontWeightBold": True,
        },
        "tpl-31-1-T": {
            "fillStyle": "#FFFFFF",
            "strokeLineWidth": 0,
            "fontWeightBold": True,
            "bgType": 2,
            "bgColors": ["#000000"],
            "bgR": 3,
            "bgPaddingY": 6,
        },
        "tpl-193-2-T": {
            "fillStyle": "#000000",
            "strokeLineWidth": 0,
            "fontWeightBold": True,
            "bgType": 2,
            "bgColors": ["#FFB800"],
            "bgR": 3,
            "bgPaddingY": 6,
        },
    }

    base.update(presets.get(style, {}))
    return base
```

## 推荐配置

### 普通字幕压制

适合大多数场景，简单稳定：

```json
{
  "font_param": {
    "style": "tpl-31-1-T",
    "font_size": 32,
    "position": 0.8
  }
}
```

### 视频语音翻译并显示新字幕

适合配音后显示译文字幕：

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

### 需要精细控制字体、描边和背景

适合需要品牌化字幕样式的场景：

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

## Agent 决策规则

- 只需要快速设置字幕位置、字号和样式时，使用 V1.0：`style`、`font_size`、`position`。
- 用户明确要求字体、阴影、描边、多色背景、字幕区域宽度等细节时，使用 V2.0。
- `wyVoiceParam` 是 JSON 字符串；在 Python 中应先构造对象，再用 `json.dumps(..., ensure_ascii=False, separators=(",", ":"))` 转成字符串。
- 字幕压制或视频配音新字幕没有特别要求时，推荐 `style="tpl-31-1-T"`、`font_size=32`、`position=0.727` 到 `0.8`。
- V2.0 中 `config`、`fontFileName`、`subtitleLang`、`videoWidth` 要与 `style`、`font_size`、`position` 一起放在 `font_param` 下。
- 选择字体时必须考虑字幕语种。中文、日语、韩语、泰语、阿拉伯语、印地语、孟加拉语等语种应优先选择明确支持该语种的字体。
- 如果字幕换行不理想，先检查 `subtitleAreaWidth` 是否太小；必要时在字幕文本中手动加入换行符。

## 相关文档

- [API 总览](./00-api-overview.md)：查看字幕样式与各功能之间的关系。
- [为视频压制字幕](./22-burn-subtitles.md)：把已有 SRT 字幕压制到视频画面。
- [视频语音翻译与重新配音](./31-video-voice-translation.md)：翻译视频并在新配音过程中渲染字幕。
