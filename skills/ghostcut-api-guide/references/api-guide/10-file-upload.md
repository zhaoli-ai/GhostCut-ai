---
title: "GhostCut 本地文件上传 API"
description: "面向 Agent 的 GhostCut 本地 SRT、图片、视频上传调用说明。用于把本地文件上传到 GhostCut OSS，并获得可传给其他 GhostCut API 的临时 URL。"
---

# GhostCut 本地文件上传 API

本文档面向 Agent 或自动化调用程序。目标是让模型在只有本地文件时，能够先上传文件，获得临时公网 URL，再把该 URL 传给 GhostCut 的其他处理接口。

## 什么时候调用

当用户要处理的素材是本地文件，而后续 GhostCut API 需要一个可访问的 URL 时，先调用本上传流程。

支持上传：

- 图片：`materialFileType=image`
- 视频：`materialFileType=video`
- 字幕：`materialFileType=srt`
- 译制出海项目视频素材：`materialFileType=video_series`
- 译制出海项目字幕素材：`materialFileType=srt_series`
- 替换译制出海项目中的视频素材：`materialFileType=video_series_replace`

临时 URL 不保证长期有效。通常会员过期时有效期约 14 天，会员未过期时有效期约 30 天。获得 URL 后应尽快传给 GhostCut 的后续处理接口，不应把该接口当作通用网盘使用。

## 调用总流程

1. 准备 `AppKey` 和 `AppSecret`。
2. 根据上传场景组装 JSON 请求体。
3. 对 JSON 请求体生成 `AppSign`。
4. 调用获取上传凭证接口。
5. 用返回的凭证把本地文件以 `multipart/form-data` 上传到 `body.host`。
6. 上传成功后，用 `body.urlPrefix + filename` 拼出临时 URL。
7. 如需删除文件，调用删除接口，传入上传时使用的 `key`。

## 认证与签名

除 OSS 文件上传本身外，GhostCut 业务接口都需要签名。

请求头：

```http
Content-Type: application/json
AppKey: <your_app_key>
AppSign: <generated_sign>
```

签名规则：

```text
body_str = 请求 JSON 字符串
body_md5hex = md5(body_str).hexdigest()
AppSign = md5(body_md5hex + AppSecret).hexdigest()
```

重要约束：

- 用于签名的 `body_str` 必须和实际发送的请求体完全一致。
- 生成 JSON 时不要随意改变空格、字段顺序或编码后再复用旧签名。
- 建议在同一个函数中同时生成 `body_str`、`AppSign` 并发送请求。

Python 签名示例：

```python
import hashlib
import json


def dumps_body(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def make_app_sign(body_str: str, app_secret: str) -> str:
    body_md5hex = hashlib.md5(body_str.encode("utf-8")).hexdigest()
    return hashlib.md5((body_md5hex + app_secret).encode("utf-8")).hexdigest()
```

## 接口一：获取上传凭证

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/file/upload/policy/apply
```

该接口需要 `AppKey` 和 `AppSign`。

### 普通图片、视频、字幕上传

用于获得普通素材上传凭证。适合后续把临时 URL 传给去字幕、图片处理等接口。

请求体字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `nonce` | string | 是 | 随机字符串。 |
| `materialFileType` | string | 否 | 文件类型。可选 `image`、`video`、`srt`。不传默认 `image`。 |
| `expireSeconds` | integer | 否 | 上传凭证过期时间，单位秒，范围 `1` 到 `86400`，默认 `3600`。 |

请求示例：

```json
{
  "nonce": "iY2FsbGJhY2tVcmwiOiJodH",
  "materialFileType": "video"
}
```

### 译制出海：上传剧集视频素材

用于把视频上传到某个译制出海项目或剧集下，作为剧集素材。

请求体字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `nonce` | string | 是 | 随机字符串。 |
| `idSeries` | long | 是 | 剧集或项目 ID。 |
| `materialFileType` | string | 是 | 固定传 `video_series`。 |
| `materialName` | string | 是 | 本集名称。 |
| `expireSeconds` | integer | 否 | 上传凭证过期时间，单位秒。 |

请求示例：

```json
{
  "nonce": "iY2FsbGJhY2tVcmwiOiJodH",
  "idSeries": 123123,
  "materialFileType": "video_series",
  "materialName": "第一集"
}
```

成功响应的 `body` 中会额外返回：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `idMaterialVideo` | long | 新增的视频素材 ID。后续上传该视频对应字幕时要使用。 |

### 译制出海：上传剧集字幕素材

用于把 SRT 字幕上传到某个剧集下，并关联到一个具体视频素材。

请求体字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `nonce` | string | 是 | 随机字符串。 |
| `idSeries` | long | 是 | 剧集或项目 ID。 |
| `idMaterialVideo` | long | 是 | 视频素材 ID，来自上传 `video_series` 后返回的 `body.idMaterialVideo`。 |
| `materialFileType` | string | 是 | 固定传 `srt_series`。 |
| `materialName` | string | 是 | 字幕素材名称。 |
| `fileName` | string | 否 | 字幕文件名，下载时可能使用。 |
| `sourceLang` | string | 是 | 字幕语种 code，例如 `en`。具体枚举以 GhostCut 查询枚举接口为准。 |
| `expireSeconds` | integer | 否 | 上传凭证过期时间，单位秒。 |

请求示例：

```json
{
  "nonce": "iY2FsbGJhY2tVcmwiOiJodH",
  "idSeries": 123123,
  "idMaterialVideo": 123123123,
  "materialFileType": "srt_series",
  "materialName": "第一集的英文字幕",
  "fileName": "episode_1_en.srt",
  "sourceLang": "en"
}
```

成功响应的 `body` 中会额外返回：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `idMaterialSrt` | long | 新增的字幕素材 ID。 |

### 译制出海：替换已有视频素材文件

用于上传新视频文件，替换某个已有视频素材 ID 下的文件。

请求体字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `nonce` | string | 是 | 随机字符串。 |
| `idMaterialVideo` | long | 是 | 要替换的视频素材 ID。 |
| `materialFileType` | string | 是 | 固定传 `video_series_replace`。 |
| `expireSeconds` | integer | 否 | 上传凭证过期时间，单位秒。 |

请求示例：

```json
{
  "nonce": "iY2FsbGJhY2tVcmwiOiJodH",
  "idMaterialVideo": 123123123,
  "materialFileType": "video_series_replace"
}
```

## 上传凭证响应

获取上传凭证成功时，响应外层通常满足：

```json
{
  "code": 1000,
  "msg": "success",
  "body": {
    "accessid": "OSSAccessKeyId",
    "base64CallbackBody": "base64-callback",
    "dir": "ve_material_image2/A-xxx/uuid/",
    "expire": "1702973411",
    "host": "https://ghost-cut.oss-cn-shanghai.aliyuncs.com",
    "ossBucket": "ghost-cut",
    "ossEndpoint": "oss-cn-shanghai.aliyuncs.com",
    "policy": "base64-policy",
    "signature": "oss-signature",
    "urlPrefix": "https://gc100.cdn.izhaoli.cn/ve_material_image2/A-xxx/uuid/"
  },
  "trace": "trace-id"
}
```

模型调用时应检查：

- `code == 1000`
- `body.host` 存在
- `body.dir` 存在
- `body.urlPrefix` 存在
- `body.policy`、`body.signature`、`body.accessid`、`body.base64CallbackBody` 存在

## 接口二：使用上传凭证上传本地文件

```http
POST <body.host>
Content-Type: multipart/form-data
```

该接口是 OSS 表单上传，不需要 `AppKey` 或 `AppSign`。

表单字段：

| 字段 | 来源 | 说明 |
| --- | --- | --- |
| `key` | `body.dir + filename` | OSS 对象路径。删除文件时也使用这个值。 |
| `OSSAccessKeyId` | `body.accessid` | 上传凭证中的 access id。 |
| `policy` | `body.policy` | 上传策略。 |
| `signature` | `body.signature` | OSS 上传签名。 |
| `callback` | `body.base64CallbackBody` | 上传成功后的回调配置。 |
| `success_action_status` | 固定 `200` | 要求 OSS 成功时返回 HTTP 200。 |
| `file` | 本地文件二进制 | 要上传的文件内容。 |

文件名建议：

- 使用短文件名，例如 `input.mp4`、`subtitle_en.srt`。
- 避免空格、中文、特殊符号和过长文件名。
- 上传时的 `filename` 必须和拼接 URL 时使用的 `filename` 完全一致。

上传成功判断：

- HTTP 请求成功。
- 响应体为 `{"Status":"OK"}`。

上传成功后：

```text
temporary_url = body.urlPrefix + filename
key = body.dir + filename
```

后续 GhostCut API 需要素材 URL 时，传 `temporary_url`。

## 视频素材状态枚举

普通视频上传和译制出海视频上传都会经历视频素材下载、转码和预处理。相关接口或素材列表中出现的 `processStatus` 是“视频素材状态”，不等同于普通视频作品在 `/work/status` 中返回的任务处理状态。普通视频作品状态见[视频处理状态枚举](./14-video-process-status.md)。

通用判断：

| 判断 | 含义 | 下一步 |
| --- | --- | --- |
| `processStatus < 1` | 素材仍在下载、转码或等待预处理 | 继续等待或轮询。 |
| `processStatus == 1` | 素材已可用 | 可继续提交后续处理任务。 |
| `processStatus > 1` | 素材准备失败 | 按下方枚举排查；修复素材或资源问题后重新上传、导入或替换。 |

视频素材 `processStatus` 常见枚举：

| `processStatus` | 枚举名 | 中文说明 | 英文说明 | 建议处理 |
| --- | --- | --- | --- | --- |
| `-3` | `BaiduDownloadInit` | 百度云下载初始化中 | `Baidu cloud download initializing` | 中间状态，继续等待或轮询。 |
| `-2` | `Transcoding` | 转码中 | `Transcoding` | 中间状态，继续等待或轮询。 |
| `-1` | `Default` | 默认，需要进行处理 | `Default, waiting for processing` | 中间状态，继续等待或轮询。 |
| `1` | `Success` | 成功 | `Success` | 素材准备完成，可用于后续处理任务。 |
| `2` | `VideoUrlParseError` | URL 解析失败 | `Failed to parse supplied url` | 检查 URL 是否为公网可访问的视频直链，不能是登录页、网盘页或含中文字符的地址；修复后重新导入。 |
| `3` | `DownloadFailure` | 下载失败 | `Failed to download material video` | 检查 URL 是否可访问、视频是否可播放、文件是否损坏；修复后重新导入或重新上传。 |
| `4` | `TimeoutError` | 下载超时 | `Download timeout` | 可先重试；如多次失败，换用更稳定的素材 URL 或重新上传。 |
| `5` | `FpsNotSupportedError` | 帧率过高不支持 | `Frame rate is too high` | 重新导出为常规帧率后再上传或导入。 |
| `6` | `ValidationError` | 验证失败 | `Validation error` | 检查素材格式、大小、时长和元信息；必要时重新转码后再上传。 |
| `7` | `TranscodeError` | 转码失败 | `Transcode error` | 素材转码失败；可先重新转码为常规 `mp4` 后再上传，仍失败时联系 GhostCut 并提供素材 ID。 |
| `8` | `MaterialNotExistError` | 素材不存在 | `Material not exist` | 检查素材 ID 是否正确、素材是否已删除或是否属于当前项目。 |
| `16` | `VideoCorruptedError` | 视频下载转码前后时长相差超过阈值，判定为下载的视频损坏 | `The material video may be currupted` | 检查视频是否完整可播放，建议重新导出或重新上传。 |
| `17` | `ModerationSubmitError` | 审核任务提交失败 | `Failed to submit video audit task` | 可重试；多次失败时联系 GhostCut。 |
| `73` | `PointExhaustedError` | 点数不足 | `Point exhausted` | 补充点数后重新处理。 |
| `98` | `ResourceExhaustedError` | OSS 资源耗尽 | `Storage space is insufficient` | 清理存储空间或扩容后重试。 |
| `99` | `ExeedDurationLimit` | 超出素材时长限制 | `Material video succeeds duration limit` | 拆分或裁剪视频后重新上传。 |
| `100` | `ExeedSizeLimit` | 超出素材大小限制 | `Material video succeeds size limit` | 压缩视频或降低码率后重新上传。 |

## 删除上传后的文件

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/file/remove
```

该接口需要 `AppKey` 和 `AppSign`。

请求体字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `key` | string | 是 | 上传文件时使用的 `body.dir + filename`。 |

请求示例：

```json
{
  "key": "ve_material_video/A-54de6d3682c44c8a/9c33a4254ec449e2bffd8633b52ee6f6/1739794241470.mp4"
}
```

成功响应：

```json
{
  "body": 1,
  "code": 1000,
  "count": 0,
  "msg": "success",
  "trace": "bb44e9ba17444bd09d0ec9434798ff34"
}
```

注意：删除会删除素材记录和对应文件。由于 URL 背后可能有 CDN，删除后短时间内 URL 仍可能可以访问，需要等待 CDN 同步。

## 文件一致性校验

OSS 上传响应头里的 `Content-MD5` 是服务端收到文件后的 base64 MD5。可和本地文件的 base64 MD5 对比。

本地计算方式：

```python
import base64
import hashlib


def file_base64_md5(local_file_path: str) -> str:
    with open(local_file_path, "rb") as f:
        digest = hashlib.md5(f.read()).digest()
    return base64.b64encode(digest).decode("utf-8")
```

对比逻辑：

```python
server_md5 = upload_response.headers.get("Content-MD5")
local_md5 = file_base64_md5(local_file_path)

if server_md5 and server_md5 != local_md5:
    raise RuntimeError("uploaded file md5 mismatch")
```

## Python 完整示例

该示例完成普通本地文件上传，并返回临时 URL 和删除用的 key。

```python
import base64
import hashlib
import json
import os
import uuid
from typing import Any

import requests


APP_KEY = "your_app_key"
APP_SECRET = "your_app_secret"
BASE_URL = "https://api.zhaoli.com"


def dumps_body(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def make_app_sign(body_str: str, app_secret: str) -> str:
    body_md5hex = hashlib.md5(body_str.encode("utf-8")).hexdigest()
    return hashlib.md5((body_md5hex + app_secret).encode("utf-8")).hexdigest()


def ghostcut_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
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
    if data.get("code") != 1000:
        raise RuntimeError(f"GhostCut API failed: {data}")
    return data


def file_base64_md5(local_file_path: str) -> str:
    with open(local_file_path, "rb") as f:
        digest = hashlib.md5(f.read()).digest()
    return base64.b64encode(digest).decode("utf-8")


def apply_upload_policy(material_file_type: str = "image") -> dict[str, Any]:
    payload = {
        "nonce": uuid.uuid4().hex,
        "materialFileType": material_file_type,
    }
    data = ghostcut_post("/v-w-c/gateway/ve/file/upload/policy/apply", payload)
    return data["body"]


def upload_with_policy(local_file_path: str, policy_body: dict[str, Any], filename: str | None = None) -> dict[str, str]:
    if filename is None:
        filename = os.path.basename(local_file_path)

    key = policy_body["dir"] + filename

    form_data = {
        "key": key,
        "OSSAccessKeyId": policy_body["accessid"],
        "policy": policy_body["policy"],
        "signature": policy_body["signature"],
        "callback": policy_body["base64CallbackBody"],
        "success_action_status": "200",
    }

    with open(local_file_path, "rb") as f:
        files = {"file": (filename, f)}
        response = requests.post(policy_body["host"], data=form_data, files=files, timeout=120)

    response.raise_for_status()
    if response.text.strip() != '{"Status":"OK"}':
        raise RuntimeError(f"OSS upload failed: {response.text}")

    server_md5 = response.headers.get("Content-MD5")
    if server_md5 and server_md5 != file_base64_md5(local_file_path):
        raise RuntimeError("OSS upload md5 mismatch")

    return {
        "url": policy_body["urlPrefix"] + filename,
        "key": key,
    }


def upload_local_file(local_file_path: str, material_file_type: str = "image", filename: str | None = None) -> dict[str, str]:
    policy_body = apply_upload_policy(material_file_type)
    return upload_with_policy(local_file_path, policy_body, filename)


if __name__ == "__main__":
    result = upload_local_file(r"C:\Users\example\Downloads\input.mp4", material_file_type="video", filename="input.mp4")
    print(result["url"])
    print(result["key"])
```

## Python：译制出海上传视频后再上传字幕

```python
def apply_series_video_policy(id_series: int, material_name: str) -> dict[str, Any]:
    payload = {
        "nonce": uuid.uuid4().hex,
        "idSeries": id_series,
        "materialFileType": "video_series",
        "materialName": material_name,
    }
    data = ghostcut_post("/v-w-c/gateway/ve/file/upload/policy/apply", payload)
    return data["body"]


def apply_series_srt_policy(
    id_series: int,
    id_material_video: int,
    material_name: str,
    source_lang: str,
    file_name: str | None = None,
) -> dict[str, Any]:
    payload = {
        "nonce": uuid.uuid4().hex,
        "idSeries": id_series,
        "idMaterialVideo": id_material_video,
        "materialFileType": "srt_series",
        "materialName": material_name,
        "sourceLang": source_lang,
    }
    if file_name:
        payload["fileName"] = file_name

    data = ghostcut_post("/v-w-c/gateway/ve/file/upload/policy/apply", payload)
    return data["body"]


# 1. 上传剧集视频
video_policy = apply_series_video_policy(id_series=123123, material_name="第一集")
video_upload = upload_with_policy(
    local_file_path=r"C:\Users\example\Downloads\episode_1.mp4",
    policy_body=video_policy,
    filename="episode_1.mp4",
)
id_material_video = video_policy["idMaterialVideo"]

# 2. 上传并关联字幕
srt_policy = apply_series_srt_policy(
    id_series=123123,
    id_material_video=id_material_video,
    material_name="第一集英文字幕",
    source_lang="en",
    file_name="episode_1_en.srt",
)
srt_upload = upload_with_policy(
    local_file_path=r"C:\Users\example\Downloads\episode_1_en.srt",
    policy_body=srt_policy,
    filename="episode_1_en.srt",
)

print(video_upload["url"])
print(srt_upload["url"])
print(id_material_video)
print(srt_policy["idMaterialSrt"])
```

## Python：删除已上传文件

```python
def remove_uploaded_file(key: str) -> int:
    data = ghostcut_post("/v-w-c/gateway/ve/file/remove", {"key": key})
    return int(data["body"])


deleted_count = remove_uploaded_file("ve_material_video/A-xxx/uuid/input.mp4")
print(deleted_count)
```

## Agent 决策规则

- 如果用户提供的是本地路径，且目标 GhostCut 功能需要 URL，先走本文件上传流程。
- 如果用户没有指定 `materialFileType`，根据扩展名推断：图片用 `image`，视频用 `video`，`.srt` 用 `srt`。
- 如果用户明确说是“译制出海”“剧集素材”“项目字幕”，不要使用普通 `video` 或 `srt`，应使用 `video_series` 或 `srt_series`。
- 用户问视频素材状态、上传状态、转码状态，或普通上传 / 译制出海上传后的 `processStatus` 时，使用本文“视频素材状态枚举”；不要套用 `/work/status` 的作品处理状态表。
- 上传字幕到译制出海项目前，必须先有 `idMaterialVideo`。
- OSS 上传接口不要加 `AppKey`、`AppSign`；只有 GhostCut 业务接口需要签名。
- 对外返回给后续接口的是 `urlPrefix + filename`，删除接口使用的是 `dir + filename`。
- 如果上传失败、`code != 1000`、响应不是 `{"Status":"OK"}` 或 MD5 不一致，应停止后续处理并报告错误。

## 相关文档

- [API 总览](./00-api-overview.md)：查看功能选择入口和主要调用流程。
- [API 凭证与签名](./02-auth-and-sign.md)：查看公共签名规则和常见鉴权错误。
- [视频去字幕](./21-erase-video-subtitle.md)：本地视频上传后可用于擦除字幕、文字、logo 等区域。
- [为视频压制字幕](./23-burn-subtitles.md)：本地视频或 SRT 上传后可用于字幕压制。
- [视频语音翻译与重新配音](./31-video-voice-translation.md)：本地视频上传后可用于翻译并重新配音。
- [译制出海项目与视频素材](./60-series-project-and-video-materials.md)：上传或导入译制出海项目视频素材。
- [译制出海字幕素材管理](./61-series-subtitle-materials.md)：上传、创建和查询译制出海字幕素材。
