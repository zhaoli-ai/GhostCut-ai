# GhostCut API 最小示例

这些文件用于让新用户快速跑通签名、创建任务和查询任务状态。

## 文件说明

| 文件 | 用途 |
| --- | --- |
| `.env.example` | `AppKey` 和 `AppSecret` 环境变量模板。 |
| `video-inpaint-advanced-lite-fullscreen.payload.json` | 创建视频去文字任务：高擦 Lite，1 个全屏大小的框选范围。 |
| `work-status.payload.json` | 查询普通视频处理任务状态的请求体模板。 |
| `image-translate.payload.json` | 创建图片中文翻英文并合成结果图的请求体模板，默认使用演示图片 URL。 |

## 常用命令

先设置真实凭证：

```bash
export GHOSTCUT_APP_KEY="your_app_key"
export GHOSTCUT_APP_SECRET="your_app_secret"
```

然后在 skill 根目录执行：

```bash
python scripts/ghostcut_api.py sign --payload examples/video-inpaint-advanced-lite-fullscreen.payload.json
python scripts/ghostcut_api.py post --path /v-w-c/gateway/ve/work/free --payload examples/video-inpaint-advanced-lite-fullscreen.payload.json
python scripts/ghostcut_api.py work-status 521461135
```

说明：

- `.env.example` 中是占位值，运行前替换为真实 `AppKey` 和 `AppSecret`。
- 视频示例默认使用演示视频 URL。真实业务接入时，替换为自己的公网视频 URL；本地视频需先上传。
- 创建任务成功后，从响应的 `body.dataList[0].id` 读取作品 ID，再用 `work-status` 查询。
- 图片示例默认使用演示图片 URL。真实业务接入时，替换为自己的公网图片 URL；本地图片需先上传。
