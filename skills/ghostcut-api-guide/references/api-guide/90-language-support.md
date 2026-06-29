> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# 不同功能支持的语言列表

> 本文档整理 GhostCut 不同产品能力支持的源语言和目标语言。调用接口时，`sourceLang`、`videoInpaintLang`、`lang` 等字段应使用下方语言代码。

## 使用规则

- `sourceLang` 通常表示源语言，也就是视频原语种、音频原语种或字幕原语种。
- `videoInpaintLang` 通常用于视频擦除、OCR 提取等视觉文字识别场景，表示要识别或处理的画面文字语言。
- `lang` 通常表示目标语言，也就是要翻译成的语种。
- 如果某个功能“不需要翻译”，通常将目标语言传成与源语言相同的值。
- 语言代码大体遵循 ISO 639-1；例外包括 `fil` 这类三位代码，以及 `pt-br`、`es-sa` 这类带地区后缀的代码。
- 下表中的“经典配音”“超真实配音”“高情感配音”是按产品能力整理的语种范围。其中“高情感配音”和“情感克隆模式”是同一个概念。具体到配音参数时，`voice_type=TTS` 表示经典基础或经典高级音色，`voice_type=CLONE` 表示超真实音色；情感克隆模式通过 `wyTaskType=VOICE_CLONE_PRO` 区分。

## 各功能支持语种

| 产品能力 / 接口类型 | 支持的源语言 | 支持的目标语言 | 备注 |
| --- | --- | --- | --- |
| 译制出海-经典配音 | 无源语言 | 38 种：`ar`, `pt-br`, `bg`, `pl`, `da`, `de`, `ru`, `fr`, `fil`, `fi`, `km`, `ko`, `nl`, `cs`, `hr`, `ro`, `ms`, `bn`, `es-sa`, `no`, `pt`, `ja`, `sv`, `sk`, `sl`, `th`, `tr`, `ur`, `uk`, `es`, `el`, `hu`, `it`, `hi`, `id`, `en`, `vi`, `zh` | 面向配音目标语种。 |
| 译制出海-超真实配音 | 无源语言 | 35 种：`ar`, `pt-br`, `bg`, `pl`, `da`, `de`, `ru`, `fr`, `fil`, `fi`, `km`, `ko`, `nl`, `cs`, `hr`, `ro`, `ms`, `no`, `pt`, `ja`, `sv`, `es-sa`, `sk`, `ta`, `th`, `tr`, `uk`, `es`, `el`, `hu`, `it`, `hi`, `id`, `en`, `vi`, `zh-tw` | 面向超真实配音目标语种。 |
| 译制出海-高情感配音 / 情感克隆模式 | 无源语言 | 26 种：`ar`, `bg`, `pl`, `da`, `de`, `ru`, `fr`, `fil`, `fi`, `ko`, `nl`, `cs`, `ro`, `ms`, `pt`, `ja`, `sv`, `th`, `tr`, `es`, `el`, `it`, `hi`, `id`, `en`, `vi` | 面向情感克隆模式目标语种。 |
| SRT 翻译 | 39 种：`ar`, `bg`, `pl`, `da`, `de`, `ru`, `fr`, `fil`, `fi`, `km`, `ko`, `nl`, `cs`, `ro`, `ms`, `bn`, `my`, `no`, `pt-br`, `pt`, `ja`, `sv`, `sk`, `sl`, `th`, `tr`, `tk`, `ur`, `es`, `es-sa`, `el`, `hu`, `it`, `hi`, `id`, `en`, `vi`, `zh`, `zh-hant`, `zh-TW` | 39 种：`ar`, `bg`, `pl`, `da`, `de`, `ru`, `fr`, `fil`, `fi`, `km`, `ko`, `nl`, `cs`, `ro`, `ms`, `bn`, `my`, `no`, `pt-br`, `pt`, `ja`, `sv`, `sk`, `sl`, `th`, `tr`, `tk`, `ur`, `es`, `es-sa`, `el`, `hu`, `it`, `hi`, `id`, `en`, `vi`, `zh`, `zh-hant`, `zh-tw` | 用于字幕文件翻译。 |
| ASR 提取字幕 | 31 种：`ar`, `pl`, `da`, `de`, `ru`, `fr`, `fil`, `fi`, `km`, `ko`, `nl`, `cs`, `ms`, `bn`, `my`, `pt`, `ja`, `sv`, `th`, `tr`, `ur`, `uk`, `es`, `el`, `hu`, `it`, `hi`, `id`, `en`, `vi`, `zh` | 无目标语言 | 通过音频识别生成 SRT。 |
| OCR 提取字幕 | 17 种 + 自动识别：`zh`, `en`, `ja`, `ko`, `id`, `ms`, `fil`, `de`, `fr`, `ar`, `es`, `pt`, `it`, `tr`, `bg`, `vi`, `nl`, `auto` | 31 种：`zh`, `en`, `zh-hant`, `ja`, `ko`, `pt`, `pt-br`, `fr`, `es`, `ar`, `vi`, `th`, `de`, `ru`, `it`, `id`, `hi`, `tr`, `fil`, `ms`, `km`, `pl`, `hu`, `cs`, `bg`, `ro`, `da`, `no`, `sv`, `nl`, `fi` | 如不需要翻译，目标语言填入与源语言相同的值。源语言不确定时优先使用 `auto`。 |
| 视频语音翻译、精教版、字幕压制 | 17 种：`zh`, `en`, `ja`, `ko`, `pt`, `fr`, `es`, `ar`, `vi`, `th`, `de`, `ru`, `it`, `id`, `ms`, `tr`, `da` | 38 种：`zh`, `en`, `zh-hant`, `ja`, `ko`, `pt`, `pt-br`, `fr`, `es`, `ar`, `vi`, `th`, `de`, `ru`, `it`, `id`, `hi`, `tr`, `fil`, `ms`, `km`, `pl`, `hu`, `cs`, `bg`, `ro`, `da`, `no`, `sv`, `nl`, `fi`, `el`, `sk`, `sl`, `ur`, `bn`, `my`, `tk` | 支持自动识别 ASR 和音画重新对齐。 |
| 视频擦除 / 去文字 | 基础擦除支持 6 种：`all`, `zh`, `en`, `ja`, `ko`, `ar`；高级擦除 Lite 和 Pro 只支持 `all` | 无目标语言 | 自动检测视频内置字幕并擦除。 |
| 视频文字翻译 | 2 种：`zh`, `en` | 31 种：`zh`, `en`, `zh-hant`, `ja`, `ko`, `pt`, `pt-br`, `fr`, `es`, `ar`, `vi`, `th`, `de`, `ru`, `it`, `id`, `hi`, `tr`, `fil`, `ms`, `km`, `pl`, `hu`, `cs`, `bg`, `ro`, `da`, `no`, `sv`, `nl`, `fi` | 包含 OCR 提取、擦除以及翻译回填。 |
| 图片擦除与翻译 | 支持 70+ 种 OCR 识别：`zh`, `zh-hant`, `both`, `en`, `auto`, `ja`, `ko`, `th`, `vi`, `id`, `ms`, `fil`, `hi`, `ru`, `de`, `fr`, `ar`, `es`, `pt`, `it`, `pl`, `nl` 等 | 支持左侧全部源语言，另支持 `ti`、`uy` 作为纯翻译目标语言 | `ti` 藏语和 `uy` 维吾尔语不支持 OCR 识别，不能作为源语言，仅支持作为图片翻译目标语言。 |

## 常用语言代码速查

| 语言代码 | 中文名称 | 英文名称 |
| --- | --- | --- |
| `all` | 全部 | all language |
| `auto` | 自动识别 | Auto |
| `both` | 中英文 | Both Chinese and English |
| `zh` | 中文 | Chinese |
| `zh-hant` | 中文（繁体） | Chinese (Traditional) |
| `zh-tw` / `zh-TW` | 中文（台湾） | Chinese (Taiwan) |
| `en` | 英语 | English |
| `ja` | 日语 | Japanese |
| `ko` | 韩语 | Korean |
| `es` | 西班牙语-欧陆 | Spanish (Europe) |
| `es-sa` | 西班牙语-南美 | Spanish (South America) |
| `pt` | 葡萄牙语 | Portuguese |
| `pt-br` | 葡萄牙语-巴西 | Portuguese (Brazil) |
| `fr` | 法语 | French |
| `de` | 德语 | German |
| `ru` | 俄语 | Russian |
| `ar` | 阿拉伯语 | Arabic |
| `th` | 泰语 | Thai |
| `vi` | 越南语 | Vietnamese |
| `id` | 印尼语 | Indonesian |
| `ms` | 马来语（马来西亚） | Malay (Malaysian) |
| `fil` | 菲律宾语 | Philippines |
| `hi` | 印地语 | Hindi |
| `it` | 意大利语 | Italian |
| `nl` | 荷兰语 | Dutch |
| `pl` | 波兰语 | Polish |
| `da` | 丹麦语 | Danish |
| `fi` | 芬兰语 | Finnish |
| `km` | 高棉语 | Khmer |
| `bg` | 保加利亚语 | Bulgarian |
| `bn` | 孟加拉语 | Bengali |
| `cs` | 捷克语 | Czech |
| `el` | 希腊语 | Greek |
| `hr` | 克罗地亚语 | Croatian |
| `hu` | 匈牙利语 | Hungarian |
| `my` | 缅甸语 | Burmese |
| `no` | 挪威语 | Norwegian |
| `ro` | 罗马尼亚语 | Romanian |
| `sk` | 斯洛伐克语 | Slovak |
| `sl` | 斯洛文尼亚语 | Slovenian |
| `sv` | 瑞典语 | Swedish |
| `ta` | 泰米尔语 | Tamil |
| `tk` | 土库曼语 | Turkmen |
| `tr` | 土耳其语 | Turkish |
| `uk` | 乌克兰语 | Ukrainian |
| `ur` | 乌尔都语 | Urdu |
| `ti` | 藏语 | Tibetan |
| `uy` | 维吾尔语 | Uyghur |

## 全部语言代码表

| 语言代码 | 中文名称 | 英文名称 |
| --- | --- | --- |
| `af` | 南非荷兰语 | Afrikaans |
| `az` | 阿塞拜疆语 | Azerbaijan |
| `be` | 白俄罗斯语 | Belarus |
| `bg` | 保加利亚语 | Bulgarian |
| `bn` | 孟加拉语 | Bengali |
| `bs` | 波斯尼亚语 | Bosnian |
| `ca` | 加泰罗尼亚语 | Catalan |
| `ceb` | 宿务语 | Cebu language |
| `co` | 科西嘉语 | Corsican |
| `cs` | 捷克语 | Czech |
| `cy` | 威尔士语 | Welsh |
| `da` | 丹麦语 | Danish |
| `de` | 德语 | German |
| `el` | 希腊语 | Greek |
| `en` | 英语 | English |
| `eo` | 世界语 | Esperanto |
| `es` | 西班牙语-欧陆 | Spanish (Europe) |
| `es-sa` | 西班牙语-南美 | Spanish |
| `et` | 爱沙尼亚语 | Estonia |
| `eu` | 巴斯克语 | Basque |
| `fi` | 芬兰语 | Finnish |
| `fil` | 菲律宾语 | Philippines |
| `fr` | 法语 | French |
| `fy` | 弗里斯兰语 | Frisian |
| `ga` | 爱尔兰语 | Irish |
| `gd` | 苏格兰盖尔语 | Scottish Gaelic |
| `gl` | 加利西亚语 | Galician |
| `gu` | 古吉拉特语 | Gujarati |
| `ha` | 豪萨语 | Hausa |
| `haw` | 夏威夷语 | Hawaiian |
| `he` | 希伯来语 | Hebrew |
| `hi` | 印地语 | Hindi |
| `hr` | 克罗地亚语 | Croatian |
| `ht` | 海地克里奥尔语 | Haiti Creole |
| `hu` | 匈牙利语 | Hungarian |
| `id` | 印尼语 | Indonesian |
| `ig` | 伊博语 | Igbo |
| `is` | 冰岛语 | Icelandic |
| `it` | 意大利语 | Italy |
| `ja` | 日语 | Japanese |
| `jv` | 印尼-爪哇语 | Indonesian-Javanese |
| `jy` | 格鲁吉亚语 | Georgia |
| `km` | 高棉语 | Khmer |
| `kn` | 卡纳达语 | Kannada |
| `ko` | 韩语 | Korean |
| `ku` | 库尔德语 | Kurdish |
| `ky` | 吉尔吉斯语 | Kyrgyz (Kirgiz) |
| `la` | 拉丁语 | Latin |
| `lb` | 卢森堡语 | Luxembourg |
| `lt` | 立陶宛语 | Lithuanian |
| `lv` | 拉脱维亚语 | Latvia |
| `mg` | 马尔加什语 | Malagasy |
| `mi` | 毛利语 | Maori |
| `mk` | 马其顿语 | Macedonia |
| `ml` | 马拉雅拉姆语 | Malayalam |
| `mn` | 蒙古语 | Mongolian |
| `mr` | 马拉地语 | Marathi |
| `ms` | 马来语（马来西亚） | Malay (Malaysian) |
| `mt` | 马耳他语 | Maltese |
| `mww` | 白苗语 | Bai Miao |
| `my` | 缅甸语 | Burmese |
| `ne` | 尼泊尔语 | Nepal |
| `nl` | 荷兰语 | Dutch |
| `no` | 挪威语 | Norwegian |
| `ny` | 齐切瓦语 | Chichewa |
| `otq` | 克雷塔罗奥托米语 | Queretaro Otomi |
| `pa` | 旁遮普语 | Punjabi |
| `pl` | 波兰语 | Polish |
| `ps` | 普什图语 | Pashto |
| `pt` | 葡萄牙语 | Portuguese |
| `pt-br` | 葡萄牙语-巴西 | Portuguese (Brazil) |
| `ro` | 罗马尼亚语 | Romanian |
| `ru` | 俄语 | Russian |
| `rw` | 卢旺达语 | Kinyarwanda |
| `sk` | 斯洛伐克语 | Slovak |
| `sl` | 斯洛文尼亚语 | Slovenian |
| `sm` | 萨摩亚语 | Samoa |
| `sn` | 修纳语 | Shona |
| `so` | 索马里语 | Somalia |
| `sq` | 阿尔巴尼亚语 | Albanian |
| `sr` | 塞尔维亚语（拉丁语） | Serbia (Latin) |
| `st` | 塞索托语 | Sesotho |
| `su` | 印尼巽他语 | Indonesian-Sundanese |
| `sv` | 瑞典语 | Swedish |
| `sw` | 斯瓦希里语 | Swahili |
| `te` | 泰卢固语 | Telugu |
| `tg` | 塔吉克语 | Tajik |
| `th` | 泰语 | Thai |
| `ti` | 藏语 | Tibetan |
| `tk` | 土库曼语 | Turkmen |
| `to` | 汤加语 | Tongan |
| `tr` | 土耳其语 | Turkey |
| `uk` | 乌克兰语 | Ukraine |
| `ur` | 乌尔都语 | Urdu |
| `uz` | 乌兹别克语 | Uzbek |
| `vi` | 越南语 | Vietnamese |
| `yi` | 意第绪语 | Yiddish |
| `yo` | 约鲁巴语 | Yoruba |
| `yua` | 尤卡坦玛雅语 | Yucatan Mayan |
| `zh` | 中文 | Chinese |
| `zh-hant` | 中文（繁体） | Chinese (Traditional) |
| `zu` | 南非祖鲁语 | South African Zulu |

## Agent 决策规则

- 在选择功能前，先判断用户需要的是 OCR、ASR、语音翻译、字幕压制、视频擦除、视频文字翻译、图片翻译还是 SRT 翻译。
- 不要把某功能的目标语言列表套用到另一个功能。例如 ASR 只有源语言，没有目标语言；OCR 提取如果不翻译，目标语言应与源语言相同。
- 视频擦除基础模型可按 `zh`、`en`、`ja`、`ko`、`ar` 或 `all` 指定文字语言；高级擦除 Lite/Pro 只使用 `all`。
- 图片翻译的 `ti`、`uy` 只能作为目标语言，不能作为 OCR 源语言。
- 当用户请求不在列表中的语种时，说明该功能在本文档中未明确支持；OCR 类能力可优先使用 `auto`，其他能力不要自行编造语种代码。

## 相关文档

- [API 总览](./00-api-overview.md)：查看功能选择入口和重要参数关系。
- [视频去字幕](./20-erase-video-subtitle.md)：使用 `videoInpaintLang` 指定要擦除的画面文字语言。
- [OCR 提取视频字幕](./23-ocr-subtitle-extraction.md)：使用 `videoInpaintLang` 和 `lang` 控制识别与输出语种。
- [ASR 提取视频字幕](./24-asr-subtitle-extraction.md)：使用 `sourceLang` 指定音频源语言。
- [视频语音翻译与重新配音](./31-video-voice-translation.md)：使用 `sourceLang` 和 `lang` 指定视频翻译方向。
