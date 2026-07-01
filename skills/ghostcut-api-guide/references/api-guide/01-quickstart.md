# 5 分钟快速上手

> 本文面向新安装 `ghostcut-api-guide` skill 的用户，目标是先跑通一个最小闭环：获取凭证、生成签名、创建视频去文字任务、查询任务结果。

## 最小闭环

本文示例使用普通视频处理接口 `/v-w-c/gateway/ve/work/free` 创建一个视频去文字任务：

- 功能：视频去文字。
- 模型：高擦 Lite，`advanced_lite`。
- 范围：1 个全屏大小的框选范围。
- 素材：默认使用[演示视频](../sample-assets.md)；真实接入时替换为自己的视频 URL。

对应请求体位于：

```text
../../examples/video-inpaint-advanced-lite-fullscreen.payload.json
```

下文命令默认在 skill 根目录执行，也就是包含 `SKILL.md`、`scripts/` 和 `examples/` 的目录。

## 1. 获取 API 凭证

GhostCut API 调用前需要准备 `AppKey` 和 `AppSecret`，完整说明见[API 凭证与签名](./02-auth-and-sign.md)：

1. 打开[鬼手剪辑官网](https://cn.jollytoday.com/)并注册或登录账号。
2. 登录后直接访问[用户中心](https://cn.jollytoday.com/center/)。
3. 在 `API secret key` 一栏查看 `AppKey` 和 `AppSecret`。

设置环境变量：

```bash
export GHOSTCUT_APP_KEY="your_app_key"
export GHOSTCUT_APP_SECRET="your_app_secret"
```

也可以参考模板：

```bash
source examples/.env.example
```

运行前先把模板里的占位值替换成真实凭证。不要把真实密钥提交到仓库或发到公开聊天中。

## 2. 准备视频 URL

如果只是体验 API 流程，可以先使用示例 payload 中的演示视频 URL：

```text
https://gc100.cdn.izhaoli.cn/demo/1691660164246.mp4
```

如果使用自己的本地视频，先上传获取 URL：

```bash
python scripts/ghostcut_api.py upload --file /path/input.mp4 --material-file-type video
```

上传成功后，将输出的 URL 替换到 `examples/video-inpaint-advanced-lite-fullscreen.payload.json` 的 `urls[0]`。

提交视频任务前确认：

- 视频格式支持 `mp4`、`avi`、`mov`、`mkv`、`mpg`、`m3u8`、`m4v`。
- 视频 URL 不能包含中文字符。
- 本地视频必须先上传获取 URL，不能直接把本地路径传给创建任务接口。

更完整的视频、图片、SRT 素材约束见[素材 URL 与格式要求](./03-media-requirements.md)。

## 3. 生成一次签名

先用示例请求体生成 `AppSign`，确认本地能正确读取 `GHOSTCUT_APP_SECRET`：

```bash
python scripts/ghostcut_api.py sign --payload examples/video-inpaint-advanced-lite-fullscreen.payload.json
```

如果提示缺少 `AppSecret`，检查是否已经设置 `GHOSTCUT_APP_SECRET`。

## 4. 创建视频去文字任务

创建任务：

```bash
python scripts/ghostcut_api.py post --path /v-w-c/gateway/ve/work/free --payload examples/video-inpaint-advanced-lite-fullscreen.payload.json
```

示例 payload 的核心参数：

```json
{
  "needChineseOcclude": 2,
  "videoInpaintLang": "all",
  "extraOptions": "{\"extra_inpaint_config\":{\"model\":\"advanced_lite\"}}",
  "videoInpaintMasks": "[{\"type\":\"remove_only_ocr\",\"start\":0,\"end\":99999,\"region\":[[0,0],[1,0],[1,1],[0,1]]}]"
}
```

创建接口返回成功只表示任务已提交，不代表视频已经处理完成。成功提交后，从响应中读取：

```text
body.dataList[0].id
```

这个值是后续查询 `/work/status` 使用的作品 ID。

生产接入推荐在创建任务时传入 `callback`，由 GhostCut 在任务完成后推送结果；轮询作为主动查询和补偿兜底。回调格式、验签和幂等规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。

## 5. 查询任务结果

如果已拿到作品 ID，可以直接查询：

```bash
python scripts/ghostcut_api.py work-status 521461135
```

把 `521461135` 替换成创建任务响应中的真实作品 ID。

也可以使用请求体模板：

```bash
python scripts/ghostcut_api.py post --path /v-w-c/gateway/ve/work/status --payload examples/work-status.payload.json
```

查询结果判断：

| 状态 | 含义 | 下一步 |
| --- | --- | --- |
| `processStatus == 1` | 处理成功 | 读取 `videoUrl` 下载结果视频。 |
| `processStatus < 1` | 处理中 | 等待后继续查询；生产接入的补偿轮询规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。 |
| `processStatus > 1` | 处理失败 | 查看 `errorDetail`，并参考[视频处理状态枚举](./14-video-process-status.md)。 |

## 下一步

- 需要处理本地视频：阅读[文件上传](./10-file-upload.md)。
- 需要了解鉴权和签名：阅读[API 凭证与签名](./02-auth-and-sign.md)。
- 需要确认素材格式和 URL 要求：阅读[素材 URL 与格式要求](./03-media-requirements.md)。
- 需要调整擦除范围或模型：阅读[字幕 mask 补充说明](./22-inpaint-masks-supplement.md)。
- 需要接入回调：阅读[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。
- 需要查找其他能力：回到[API 总览](./00-api-overview.md)或[完整文档索引](./llms.txt)。
