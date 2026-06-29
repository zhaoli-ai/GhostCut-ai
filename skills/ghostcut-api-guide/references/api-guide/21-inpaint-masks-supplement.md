# 视频去字幕模型版本与遮罩框坐标补充说明

> 本文是 videoInpaintMasks 和 字幕擦除 类型的补充说明，面向 Agent 使用。鉴权和创建任务以 [视频去字幕](./20-erase-video-subtitle.md) 为准；查询任务状态以[视频任务状态查询](./11-work-status-query.md)为准。本文只说明如何选择擦除版本，以及如何构造 `videoInpaintMasks`。

## Agent 快速决策

先根据用户目标选择模式：

| 目标 | 推荐参数 | 说明 |
| --- | --- | --- |
| 低成本、全屏自动去文字 | 不传 `extraOptions`，`needChineseOcclude=1` | 基础版全屏自动，成本最低，适合普通电商/TikTok 视频。 |
| 框选一个或多个字幕区域，追求成本和批量 | `model=advanced_lite`，`needChineseOcclude=2` | Lite 只擦框内识别到的文字，支持 1 到 10 个框。 |
| 单个字幕区域，追求更好质量 | `model=advanced` 或 `advanced_large_box`，`needChineseOcclude=2` | Pro 框选只支持单框；小框用 `advanced`，大框用 `advanced_large_box`。 |
| 全屏自动且追求 Pro 效果 | `model=advanced_full`，`needChineseOcclude=1` | 不传 `videoInpaintMasks`，成本较高、速度较慢。 |
| 擦 logo、贴纸、台标等非文字内容 | 基础版 + `type=remove` | Lite/Pro 框选只支持 `remove_only_ocr`，不要用于擦非文字图标。 |

## 版本差异

| 版本 | `extraOptions` | `needChineseOcclude` | `videoInpaintLang` | 遮罩框数量 | 遮罩框类型 | 面积限制 | 典型场景 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 基础版 Basic | 不传 | 常用 `1` 全屏或 `2` 框选 | `zh`、`en`、`all`、`ja`、`ko`、`ar` 等 | 支持多框 | `remove`、`remove_only_ocr`、`keep` | 无限制 | 低成本、擦文字、擦 logo/贴纸、保护区域 |
| 高级版 Lite | `{"extra_inpaint_config":{"model":"advanced_lite"}}` | 固定传 `2` | 仅 `all` | 1 到 10 个 | 仅 `remove_only_ocr` | 无限制 | 多框字幕、短剧批量处理 |
| 高级版 Pro 框选 | `advanced` 或 `advanced_large_box` | 固定传 `2` | 仅 `all` | 仅 1 个 | 仅 `remove_only_ocr` | `advanced` 小于 20%；`advanced_large_box` 保守按小于 40% | 单个区域高质量擦字幕 |
| 高级版 Pro 全屏 | `{"extra_inpaint_config":{"model":"advanced_full"}}` | 固定传 `1` | 仅 `all` | 不需要 | 不适用 | 不适用 | 全屏自动高质量擦除 |

注意：

- `extraOptions` 是 JSON 字符串，不是 JSON 对象。
- `videoInpaintMasks` 也是 JSON 字符串，且内部必须是列表，即使只有一个框也要写成 `[...]`。
- Pro 框选只支持单框。如果同一视频有多个要擦的区域，应优先用 `advanced_lite`，或拆成多次处理。
- Pro 框选面积按相对坐标计算：`(x1 - x0) * (y1 - y0)`。例如 `[[0,0.62],[1,0.62],[1,0.82],[0,0.82]]` 的面积是 `1 * 0.2 = 0.2`。

## 遮罩框对象结构

`needChineseOcclude=2` 时传 `videoInpaintMasks`。推荐先按对象数组构造，再 `json.dumps` 成字符串。

```json
[
  {
    "type": "remove_only_ocr",
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

| 字段 | 说明 |
| --- | --- |
| `type` | 框类型，视频去文字常用 `remove`、`remove_only_ocr`、`keep`。Lite/Pro 框选只能用 `remove_only_ocr`。 |
| `start` | 框开始生效的时间点，单位秒。用于跳过片头时，把它设为片头秒数。 |
| `end` | 框结束生效的绝对时间点，单位秒。和 `to_end` 二选一。 |
| `to_end` | 距离视频结尾多少秒前停止生效。`to_end: 10` 表示跳过最后 10 秒，适合不知道视频总时长但要避开片尾的场景。 |
| `region` | 四点坐标，使用 0 到 1 的相对坐标，按左上、右上、右下、左下顺时针排列。 |

## 遮罩框类型

| `type` | 作用 | 适用建议 |
| --- | --- | --- |
| `remove` | 整个框内都擦除，不管有没有文字。 | 擦台标、logo、贴纸、水印、固定图标等。主要用于基础版。 |
| `remove_only_ocr` | 只检测并擦除框内文字，尽量保留非文字背景。 | 字幕区域首选。高级版 Lite 和高级版 Pro 框选只能选这个类型。 |
| `keep` | 保护该区域，不进行处理。 | 基础版多框时用于避免误擦某个区域。 |
| `keep_no_trans` | 翻译场景中保护文字不翻译。 | 不属于普通视频去文字的优先参数。 |
| `trans_only_ocr` | 翻译场景中只处理框中文字。 | 不属于普通视频去文字的优先参数。 |

## 坐标规则

`region` 使用相对坐标，不是像素坐标：

```json
[
  [x0, y0],
  [x1, y0],
  [x1, y1],
  [x0, y1]
]
```

坐标系说明：

- 原点在视频左上角。
- `x` 从左到右递增，范围 `0` 到 `1`。
- `y` 从上到下递增，范围 `0` 到 `1`。
- 点顺序必须是左上、右上、右下、左下。
- 像素坐标转相对坐标：`relative_x = pixel_x / video_width`，`relative_y = pixel_y / video_height`。

示例：视频宽高为 `720 x 1280`，像素点 `[360, 640]` 的相对坐标是 `[360/720, 640/1280]`，即 `[0.5, 0.5]`。

## 常用参考框

以下坐标是短剧/字幕场景的参考值，实际接入时仍应按视频画面微调。

### 竖版视频常用字幕区

适合 9:16 竖版视频，字幕常在画面下方偏中位置：

```json
[
  [0, 0.56],
  [1, 0.56],
  [1, 0.76],
  [0, 0.76]
]
```

### 横版视频常用字幕区

适合 16:9 横版视频，底部字幕区：

```json
[
  [0, 0.8],
  [1, 0.8],
  [1, 1],
  [0, 1]
]
```

### 竖版右上角剧情提示区

```json
[
  [0.85, 0.02],
  [1, 0.02],
  [1, 0.33],
  [0.85, 0.33]
]
```

剧情提示有时只在开头几秒出现。此类框建议设置 `end`，避免后续画面同一区域被误擦。

### 竖版左上角剧情提示区

```json
[
  [0, 0.01],
  [0.15, 0.01],
  [0.15, 0.33],
  [0, 0.33]
]
```

同样建议按实际出现时长设置 `end`。

### 竖版右下角备案编号区

```json
[
  [0.5, 0.95],
  [1, 0.95],
  [1, 1],
  [0.5, 1]
]
```

备案编号通常只在开头几秒出现。建议设置 `end`，不要让该框全程生效。

## 请求示例

### 高级版 Lite 多框字幕擦除

```json
{
  "urls": ["https://example.com/input.mp4"],
  "needChineseOcclude": 2,
  "videoInpaintLang": "all",
  "extraOptions": "{\"extra_inpaint_config\":{\"model\":\"advanced_lite\"}}",
  "videoInpaintMasks": "[{\"type\":\"remove_only_ocr\",\"start\":0,\"to_end\":10,\"region\":[[0,0.56],[1,0.56],[1,0.76],[0,0.76]]},{\"type\":\"remove_only_ocr\",\"start\":0,\"end\":5,\"region\":[[0.85,0.02],[1,0.02],[1,0.33],[0.85,0.33]]}]"
}
```

### 高级版 Pro 单框高质量擦除

```json
{
  "urls": ["https://example.com/input.mp4"],
  "needChineseOcclude": 2,
  "videoInpaintLang": "all",
  "extraOptions": "{\"extra_inpaint_config\":{\"model\":\"advanced\"}}",
  "videoInpaintMasks": "[{\"type\":\"remove_only_ocr\",\"start\":0,\"end\":99999,\"region\":[[0,0.62],[1,0.62],[1,0.81],[0,0.81]]}]"
}
```

如果该框面积达到或超过 20%，不要用 `advanced`；改用 `advanced_large_box`，并确保面积保守小于 40%。

### 高级版 Pro 全屏自动擦除

```json
{
  "urls": ["https://example.com/input.mp4"],
  "needChineseOcclude": 1,
  "videoInpaintLang": "all",
  "extraOptions": "{\"extra_inpaint_config\":{\"model\":\"advanced_full\"}}"
}
```

## Agent 检查清单

创建任务前检查：

1. 用户是否要擦非文字内容。如果是，优先基础版 `remove`，不要选高级版 Lite/Pro 框选。
2. 是否需要多个框。如果是，不要选高级版 Pro 框选，优先 `advanced_lite`。
3. 如果选择高级版 Pro 框选，确认只有一个框，并计算面积是否满足模型限制。
4. `videoInpaintMasks` 是否是 JSON 字符串形式的列表。
5. 坐标是否为 0 到 1 的相对坐标，点序是否为左上、右上、右下、左下。
6. 只在片头或片尾出现的文字，是否设置了 `start`、`end` 或 `to_end`，避免误擦。

## 相关文档

- [API 总览](./00-api-overview.md)：查看公共调用流程和功能选择入口。
- [视频去字幕](./20-erase-video-subtitle.md)：创建擦除任务并读取结果视频字段。
- [视频任务状态查询](./11-work-status-query.md)：查询作品处理状态并读取 `videoUrl`。
- [OCR 提取视频字幕](./23-ocr-subtitle-extraction.md)：OCR 字幕提取也使用 `videoInpaintMasks` 指定识别范围。
- [不同功能支持的语言列表](./90-language-support.md)：确认 `videoInpaintLang` 在擦除或 OCR 场景下的可用值。
