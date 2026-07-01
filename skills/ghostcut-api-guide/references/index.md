# GhostCut API 指引参考

详细文档位于 `api-guide/`。当前 skill 直接随附并维护该快照；如另有外部源文档目录，需要显式指定 `--source` 后再用同步脚本对比或导入。

## 入口文档

- `api-guide/llms.txt`：简明文档索引。
- `api-guide/00-api-overview.md`：通用 API 总览和功能路由。
- `api-guide/01-quickstart.md`：新用户 5 分钟快速上手，使用示例 payload 跑通视频去文字任务。
- `sample-assets.md`：用户没有可用视频或图片时的演示素材 URL 和使用限制。

最小示例文件：

- `../examples/.env.example`：`AppKey` 和 `AppSecret` 环境变量模板。
- `../examples/video-inpaint-advanced-lite-fullscreen.payload.json`：视频去文字高擦 Lite、全屏框选任务请求体。
- `../examples/work-status.payload.json`：普通视频任务状态查询请求体。
- `../examples/image-translate.payload.json`：图片翻译任务请求体。

## 通用基础

- `api-guide/02-auth-and-sign.md`：API 凭证获取、签名规则和常见鉴权错误。
- `api-guide/03-media-requirements.md`：素材 URL、视频格式、图片格式、本地上传和批量数量要求。
- `api-guide/10-file-upload.md`：上传本地文件。
- `api-guide/11-work-status-query.md`：查询 `/work/status`。
- `api-guide/12-point-balance-query.md`：查询当前 `AppKey` 对应商户的有效点卡余额。
- `api-guide/13-language-support.md`：语言支持。
- `api-guide/14-video-process-status.md`：处理状态和错误码。
- `api-guide/15-async-and-callbacks.md`：异步任务、轮询、回调、验签、重试和幂等规则。

## 视频 AI 处理

- `api-guide/21-erase-video-subtitle.md`：视频去字幕、去文字、去 logo 或固定区域擦除。
- `api-guide/22-inpaint-masks-supplement.md`：擦除模型版本、遮罩框类型、时间字段和相对坐标规则。
- `api-guide/23-burn-subtitles.md`：将已有 SRT 字幕文件硬压制到视频画面中。
- `api-guide/24-ocr-subtitle-extraction.md`：通过图像 OCR 识别视频画面中的硬字幕，并输出 SRT 文件。
- `api-guide/25-asr-subtitle-extraction.md`：通过音频语音识别提取台词，并输出 SRT 文件。
- `api-guide/26-subtitle-style-and-fonts.md`：字幕样式细节。
- `api-guide/27-video-basic-processing.md`：视频基础剪辑、截取、分辨率、智能优化、滤镜、镜像、缩放和画面移动。
- `api-guide/30-background-music-separation.md`：去除原视频背景音中的音乐旋律，保留人声和环境效果音。
- `api-guide/31-video-voice-translation.md`：翻译视频并生成 AI 新配音。
- `api-guide/32-public-voice-characters.md`：公共音色查询。

## 图片 AI 处理

- `api-guide/81-image-processing.md`：图片文字擦除、图片翻译、翻译结果二次微调和重新合成。

## 译制出海

- `api-guide/51-series-overview.md`：译制出海模块总览。
- `api-guide/52-series-edit-common-task-structure.md`：译制出海通用任务结构和 Python 提交通用模板。
- `api-guide/53-series-edit-task-list.md`：译制出海任务列表。
- `api-guide/54-series-subtitle-extract.md`：译制出海字幕提取。
- `api-guide/55-series-subtitle-inpaint.md`：译制出海字幕擦除和遮罩框规则。
- `api-guide/56-series-dubbing.md`：译制出海 AI 配音。
- `api-guide/57-series-subtitle-burn.md`：译制出海字幕压制。
- `api-guide/58-series-audio-separate.md`：译制出海音频分离。
- `api-guide/59-series-edit-errors-and-checklist.md`：译制出海检查项和错误排查。
- `api-guide/60-series-project-and-video-materials.md`：译制出海项目与视频素材。
- `api-guide/61-series-subtitle-materials.md`：译制出海字幕素材管理。
- `api-guide/62-series-subtitle-translation.md`：译制出海字幕翻译任务。
- `api-guide/63-series-translation-glossary.md`：译制出海翻译术语库。

## 参考附录

暂无独立参考附录。通用语言、状态和错误码已归入“通用基础”。

## 维护资料

- `api-guide/99-cursor.md`：Cursor 配置和文档维护辅助说明。

脚本：

- `../scripts/ghostcut_api.py`：签名、发送请求、上传文件、查询 `/work/status`、查询点卡余额和查询译制出海 `task/list`。
- `../scripts/sync_api_guide.py`：检查当前 skill 快照；如另有外部源文档目录，可显式传 `--source /path/to/api-guide` 做对比或同步。
