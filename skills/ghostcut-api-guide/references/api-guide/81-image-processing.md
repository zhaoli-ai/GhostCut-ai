> ## 文档索引
> 可通过 [llms.txt](./llms.txt) 获取完整文档索引。
> 在继续查阅前，建议先通过该文件了解所有可用页面。

# AI 图片处理

> 鬼手剪辑 API 可对图片进行文字识别与擦除、图像多语言文字翻译，并支持对翻译结果进行二次编辑与重新合成。图片处理接口均为异步任务。

## 调用流程

一次完整的图片处理流程包含以下步骤：

1. **准备图片资源**
   如果图片已经可以通过公网 URL 访问，可直接使用该 URL。如果只有本地图片文件，先调用[文件上传 API](./10-file-upload.md)上传图片，获取临时 URL。

2. **创建图片处理任务**
   调用 `/v-w-c/gateway/ve/image/translate`，传入图片 URL、源语言、目标语言和处理参数。接口返回成功后，从 `body` 中获取图片任务 ID。

3. **查询任务状态**
   调用 `/v-w-c/gateway/ve/image/translate/query`，传入图片任务 ID。处理成功后，响应中会返回 `status` 和 `result`。

4. **读取处理结果**
   当 `status == 1` 时，表示任务处理成功。翻译并合成后的最终图片读取 `result.output_url`；仅擦除文字后的无字底图读取 `result.inpaint_url`。

5. **可选：二次微调**
   如果需要调整译文、颜色、字号或排版，可选择生成授权码唤起官方 Web 精修编辑器，或通过 `/v-w-c/gateway/ve/image/translate/redo` 提交修改后的 `result` 重新合成。

## 图片限制

| 限制项 | 说明 |
| --- | --- |
| 图片尺寸 | 不超过 `2000 * 2000 px` |
| 文件大小 | 不超过 `50MB` |
| URL | 地址中不能包含中文字符 |
| 格式 | 支持 `png`、`jpeg`、`jpg`、`bmp`、`webp` |

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
    body_str = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
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

### 2. 创建图片处理任务

调用 `/v-w-c/gateway/ve/image/translate` 创建任务。`downloadInfo` 必须是 JSON 字符串，内部 `url` 为待处理图片地址。

以下示例表示：识别中文图片文字，翻译成英文，并合成带译文的新图片。

```python
task_payload = {
    "downloadInfo": json.dumps(
        {
            "url": "https://gc100.cdn.izhaoli.cn/ve_material_image/A-00b4943646344cfc/e2d6dd82903f4059bd94c9b660f5f7b6/1782789120948.webp"
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ),
    "translateOn": 1,
    "srcLang": "zh",
    "tgtLang": "en",
    "commodityFilterOn": 0,
    "synthesisOn": 1,
}

task = api_post("/v-w-c/gateway/ve/image/translate", task_payload)

image_task_id = task["body"]
print(f"图片任务创建成功，Task ID: {image_task_id}")
```

常用参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `downloadInfo` | `string` | 是 | JSON 字符串，结构为 `{"url":"https://example.com/input.png"}`。长度不要超过 1000 字符。本地图片需要先通过[文件上传](./10-file-upload.md)获取 URL。 |
| `translateOn` | `number` | 是 | 翻译功能总开关。`0`：仅擦除文字，不翻译；`1`：开启翻译并回填。 |
| `srcLang` | `string` | 是 | 源语言。常用 `auto` 自动识别、`zh` 中文、`en` 英文、`both` 中英双语、`th` 泰语等。语种范围见[不同功能支持的语言列表](./13-language-support.md)。 |
| `tgtLang` | `string` | 是 | 目标语言。仅在 `translateOn=1` 时生效；仅擦除文字时可传空字符串。 |
| `commodityFilterOn` | `number` | 否 | 商品文字保护开关。`0`：关闭；`1`：开启。开启后，商品包装上的核心文字不会被擦除和翻译。 |
| `synthesisOn` | `number` | 是 | 图片合成开关。是否合成最终包含译文的图片，默认传 `1`。 |
| `callback` | `string` | 否 | 异步回调地址。生产接入推荐传入；任务完成后，系统会将与查询接口结构一致的结果 JSON 通过 POST 推送到该地址，回调格式和验签见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。 |
| `extraOptions` | `string` | 否 | JSON 字符串，传额外配置。例如指定图片翻译字体：`{"font_family":"Trirong"}`，目前主要用于泰语自定义字体。 |

### 3. 查询图片处理结果

创建任务拿到 `image_task_id` 后，调用 `/v-w-c/gateway/ve/image/translate/query` 查询状态。

```python
result = api_post("/v-w-c/gateway/ve/image/translate/query", {
    "id": image_task_id
})

status = result["body"]["status"]

if status == 1:
    image_result = result["body"]["result"]
    print(f"合成结果: {image_result.get('output_url')}")
    print(f"无字底图: {image_result.get('inpaint_url')}")
elif status == -1:
    print("处理中，请稍后继续查询")
else:
    print(f"处理失败: {result['body'].get('taskStatusEnum')}")
```

状态字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `status` | `number` | 处理状态。`-1`：待处理或处理中；`1`：处理成功；`>1`：处理失败。 |
| `result` | `object` | 图片处理结果对象。常用 `output_url` 表示包含翻译结果并合成后的最终图片 URL，`inpaint_url` 表示仅擦除文字后的无字底图 URL。 |
| `taskStatusEnum` | `object` | 错误状态的详细枚举信息，处理失败时重点查看。 |

## 完整示例

以下示例展示了从创建图片翻译任务到轮询获取结果图片的完整流程。

```python
import hashlib
import json
import time
import requests

APP_KEY = "your_app_key"
APP_SECRET = "your_app_secret"
BASE_URL = "https://api.zhaoli.com"


def api_post(path: str, payload: dict) -> dict:
    body_str = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
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


task = api_post("/v-w-c/gateway/ve/image/translate", {
    "downloadInfo": json.dumps(
        {"url": "https://gc100.cdn.izhaoli.cn/ve_material_image/A-00b4943646344cfc/e2d6dd82903f4059bd94c9b660f5f7b6/1782789120948.webp"},
        ensure_ascii=False,
        separators=(",", ":"),
    ),
    "translateOn": 1,
    "srcLang": "zh",
    "tgtLang": "en",
    "commodityFilterOn": 0,
    "synthesisOn": 1,
})

image_task_id = task["body"]
print(f"图片任务创建成功，Task ID: {image_task_id}")

while True:
    result = api_post("/v-w-c/gateway/ve/image/translate/query", {
        "id": image_task_id
    })

    body = result["body"]
    status = body["status"]

    if status == 1:
        image_result = body["result"]
        print(f"合成结果: {image_result.get('output_url')}")
        print(f"无字底图: {image_result.get('inpaint_url')}")
        break

    if status > 1:
        print(f"处理失败: {body.get('taskStatusEnum')}")
        break

    print("处理中，等待 30 秒后重试...")
    time.sleep(30)
```

## 仅擦除图片文字

如果用户只需要擦除图片上的文字，不需要翻译和回填，创建任务时传：

```python
payload = {
    "downloadInfo": json.dumps(
        {"url": "https://gc100.cdn.izhaoli.cn/ve_material_image/A-00b4943646344cfc/e2d6dd82903f4059bd94c9b660f5f7b6/1782789120948.webp"},
        ensure_ascii=False,
        separators=(",", ":"),
    ),
    "translateOn": 0,
    "srcLang": "auto",
    "tgtLang": "",
    "synthesisOn": 1,
}
```

处理成功后优先读取 `result.inpaint_url` 作为无字底图。

## 图片翻译结果二次微调

GhostCut 提供两种方式对初次生成的图片结果进行纠错或排版微调。

### 方式 A：生成授权码，唤起官方在线 Web 精修编辑器

先调用 `/v-w-c/gateway/ve/image/translate/auth/apply` 获取授权码：

```python
auth_result = api_post("/v-w-c/gateway/ve/image/translate/auth/apply", {
    "id": image_task_id,
    "expireSeconds": 7200,
})

auth_code = auth_result["body"]
editor_url = f"https://editor.jollytoday.com/?l=zh&c={auth_code}&PURE"
print(editor_url)
```

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `number` | 是 | 图片翻译任务 ID。 |
| `expireSeconds` | `number` | 是 | 授权码过期时间，单位秒。范围 `0` 到 `604800`，建议传 `7200`。 |

响应参数：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `body` | `string` | 授权 Code，例如 `A-48ca...`。若为空，表示授权失败。 |

获取 Code 后拼接在线编辑器 URL：

```text
https://editor.jollytoday.com/?l={语言}&c={授权Code}&PURE
```

参数说明：

| 参数 | 说明 |
| --- | --- |
| `l` | 编辑器界面语言，`zh` 表示中文界面，`en` 表示英文界面。 |
| `c` | 授权 Code。 |
| `PURE` | 可选，附加后隐藏 GhostCut 官方 Logo。 |

### 方式 B：通过 API 直接修改参数重新合成

先通过 `/v-w-c/gateway/ve/image/translate/query` 获取原始 `result`，在保留原有坐标和定位字段的前提下修改排版元数据，再调用 `/v-w-c/gateway/ve/image/translate/redo` 提交重新合成。

```python
query_result = api_post("/v-w-c/gateway/ve/image/translate/query", {
    "id": image_task_id
})

image_result = query_result["body"]["result"]

# 根据业务需要修改 image_result 中 meta_data 节点下的译文、颜色、描边或字号。
# 不要删除原 result 中的坐标、定位、图层等字段。

redo_result = api_post("/v-w-c/gateway/ve/image/translate/redo", {
    "id": image_task_id,
    "result": json.dumps(image_result, ensure_ascii=False, separators=(",", ":")),
})

print(redo_result["body"])
```

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | `number` | 是 | 图片翻译任务 ID。 |
| `result` | `string` | 是 | JSON 字符串，基于查询接口返回的 `result` 原文修改后传入。建议仅修改 `meta_data` 节点下的 `translation`、`fill_color`、`stroke_color`、`trans_font_size` 这 4 类核心字段。 |

响应参数：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `body` | `number` | 修改任务是否成功进入队列。返回 `1` 表示已进入异步处理。 |

> 注意：`redo` 不做自适应排版，文字过长可能产生重叠。提交时应严格保留原 `result` 中的坐标、定位和其他渲染字段。

## 响应示例

创建图片处理任务成功时，`body` 为图片任务 ID：

```json
{
  "body": 20842790
}
```

查询图片处理成功时，响应中会包含状态和图片结果：

```json
{
  "body": {
    "status": 1,
    "result": {
      "output_url": "https://example.com/output.png",
      "inpaint_url": "https://example.com/inpaint.png"
    }
  }
}
```

## Agent 决策规则

- 用户要处理图片上的文字、擦除图片文字、翻译图片并回填到图中时，使用本功能。
- 用户给的是本地图片路径时，先按[文件上传](./10-file-upload.md)获取图片 URL，再创建图片处理任务。
- 图片 URL 不能包含中文字符；如果用户提供的 URL 含中文，应先提醒用户更换或转义为可直接访问的英文 URL。
- 图片尺寸、大小或格式不满足限制时，不要直接提交任务，应先提醒用户转换图片。
- `downloadInfo` 和 `extraOptions` 都是 JSON 字符串，不要把对象直接传给接口。
- 仅擦除文字时传 `translateOn=0`，`tgtLang` 可为空，结果优先读取 `result.inpaint_url`。
- 翻译并回填时传 `translateOn=1`，需要同时提供 `srcLang` 和 `tgtLang`，结果优先读取 `result.output_url`。
- 涉及语言代码时，先查[不同功能支持的语言列表](./13-language-support.md)，不要凭常识猜测。
- 创建任务成功只表示异步任务已提交，不代表图片已经处理完成；生产接入推荐等待 `callback`，查询 `status` 用于主动查询和补偿兜底，回调验签和幂等规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。
- 二次微调优先使用官方 Web 精修编辑器；通过 API `redo` 时，应尽量只修改 `translation`、`fill_color`、`stroke_color`、`trans_font_size`。

## 相关文档

- [API 总览](./00-api-overview.md)：查看功能选择入口和主要调用流程。
- [API 凭证与签名](./02-auth-and-sign.md)：查看公共签名规则和常见鉴权错误。
- [文件上传](./10-file-upload.md)：本地图片需要先上传并获得临时 URL。
- [不同功能支持的语言列表](./13-language-support.md)：确认图片擦除与翻译的源语言和目标语言可用值。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback 回调格式、验签、重试和幂等规则。
- 鬼手剪辑 API 域名：`https://api.zhaoli.com`
