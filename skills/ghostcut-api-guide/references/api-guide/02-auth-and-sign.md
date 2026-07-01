# API 凭证与签名

> 本文说明 GhostCut API 的 `AppKey`、`AppSecret` 获取方式、请求签名规则和本地脚本使用方式。除 OSS 文件上传请求本身外，GhostCut 业务接口通常都需要 `AppKey` + `AppSign` 鉴权。

## 获取 API 凭证

GhostCut API 调用前需要准备 `AppKey` 和 `AppSecret`。新用户可按下面流程获取：

1. 打开[鬼手剪辑官网](https://cn.jollytoday.com/)并注册或登录账号。
2. 登录后直接访问[用户中心](https://cn.jollytoday.com/center/)。
3. 在页面中的 `API secret key` 一栏查看 `AppKey` 和 `AppSecret`。
4. 妥善保存 `AppKey` 和 `AppSecret`，后续用 `AppSecret` 生成 `AppSign`。

安全建议：

- 不要把真实 `AppKey`、`AppSecret` 写入代码仓库、公开文档或聊天记录。
- 不要把 `AppSecret` 发给不可信的第三方服务。
- 本地运行示例脚本时，优先使用环境变量：

```bash
export GHOSTCUT_APP_KEY="your_app_key"
export GHOSTCUT_APP_SECRET="your_app_secret"
```

## 请求头

GhostCut 业务接口通常使用以下请求头：

```http
Content-Type: application/json
AppKey: <your_app_key>
AppSign: <generated_sign>
```

文件上传有两层请求：

- 获取上传凭证的 GhostCut 业务接口需要 `AppKey` 和 `AppSign`。
- 上传文件到 OSS 的 `multipart/form-data` 请求本身不使用 `AppKey` 或 `AppSign`，按[文件上传](./10-file-upload.md)返回的表单字段提交。

## 签名规则

```text
body_str = 请求 JSON 字符串
body_md5hex = md5(body_str).hexdigest()
AppSign = md5(body_md5hex + AppSecret).hexdigest()
```

注意事项：

- 用于签名的 `body_str` 必须和实际发送的请求体完全一致。
- 不要先用一种 JSON 字符串生成签名，再发送另一种格式化后的 JSON。
- 建议在同一段代码中生成 `body_str`、计算 `AppSign` 并发送请求。
- 使用 `scripts/ghostcut_api.py` 时，脚本会用紧凑 JSON 生成签名并发送同一份请求体。

Python 签名示例：

```python
import hashlib
import json

APP_SECRET = "your_app_secret"

payload = {
    "idWorks": ["521461135"]
}

body_str = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
body_md5hex = hashlib.md5(body_str.encode("utf-8")).hexdigest()
app_sign = hashlib.md5((body_md5hex + APP_SECRET).encode("utf-8")).hexdigest()

print(app_sign)
```

## 使用脚本验证

在 skill 根目录中，可以用随附脚本生成一次签名：

```bash
python scripts/ghostcut_api.py sign --payload examples/video-inpaint-advanced-lite-fullscreen.payload.json
```

也可以发送签名后的请求：

```bash
python scripts/ghostcut_api.py post --path /v-w-c/gateway/ve/work/status --payload examples/work-status.payload.json
```

如果脚本提示缺少凭证，检查是否已设置：

```bash
echo "$GHOSTCUT_APP_KEY"
echo "$GHOSTCUT_APP_SECRET"
```

## 常见鉴权错误

| 现象 | 常见原因 | 处理方式 |
| --- | --- | --- |
| 缺少 `AppKey` 或 `AppSign` | 请求头未传完整 | 检查请求头是否包含 `AppKey` 和 `AppSign`。 |
| `AppKey is invalid` | `AppKey` 错误或账号无权限 | 回到用户中心确认 `API secret key`。 |
| `AppSign is invalid` | 签名请求体与实际请求体不一致，或 `AppSecret` 错误 | 使用同一个 `body_str` 计算签名并发送，确认 `AppSecret`。 |
| 本地脚本提示缺少凭证 | 环境变量未设置 | 设置 `GHOSTCUT_APP_KEY` 和 `GHOSTCUT_APP_SECRET`。 |

状态码和公共错误码说明见[视频处理状态枚举](./14-video-process-status.md)。

## 相关文档

- [5 分钟快速上手](./01-quickstart.md)：用示例 payload 跑通签名、创建任务和查询结果。
- [素材 URL 与格式要求](./03-media-requirements.md)：提交任务前检查素材 URL、格式和大小限制。
- [文件上传](./10-file-upload.md)：本地文件上传和 OSS 表单上传规则。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：回调验签使用同类签名规则，但必须基于原始回调请求体。
