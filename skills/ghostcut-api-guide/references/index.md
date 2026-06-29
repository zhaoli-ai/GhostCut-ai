# GhostCut API 指引参考

详细源文档位于 `api-guide/`。当主项目的 `api指引/` 更新后，应同步该目录，避免 skill 使用过期快照。

优先入口：

- `api-guide/llms.txt`：简明文档索引。
- `api-guide/00-api-overview.md`：通用 API 总览和功能路由。
- `api-guide/40-series-overview.md`：译制出海模块总览。
- `api-guide/41-series-edit-common-task-structure.md`：译制出海通用任务结构和 Python 提交通用模板。
- `sample-assets.md`：用户没有可用视频时的演示素材 URL 和使用限制。

常用参考文档：

- `api-guide/10-file-upload.md`：上传本地文件。
- `api-guide/11-work-status-query.md`：查询 `/work/status`。
- `api-guide/25-subtitle-style-and-fonts.md`：字幕样式细节。
- `api-guide/32-public-voice-characters.md`：公共音色查询。
- `api-guide/42-series-edit-task-list.md`：译制出海任务列表。
- `api-guide/48-series-edit-errors-and-checklist.md`：译制出海检查项和错误排查。
- `api-guide/90-language-support.md`：语言支持。
- `api-guide/91-video-process-status.md`：处理状态和错误码。

脚本：

- `../scripts/ghostcut_api.py`：签名、发送请求、上传文件、查询 `/work/status` 和查询译制出海 `task/list`。
- `../scripts/sync_api_guide.py`：检查或同步 `api指引/` 到 skill 快照。
