# 译制出海多作品合并

> 本接口用于把同一剧集下的多个已有视频作品按指定顺序合并成长视频。它是译制出海任务结构中的例外：请求体不使用 `items[]`、`workDto` 或 `videoEditParamsDto`，而是通过 JSON 字符串字段 `data` 提交 `episodes[]`。

## 接口信息

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/series/edit/task/video/merge
Content-Type: application/json
AppKey: your_app_key
AppSign: generated_app_sign
```

接口路径：

```text
gateway/ve/series/edit/task/video/merge
```

## 最小可用请求检查清单

| 检查项 | 要求 |
| --- | --- |
| 剧集 | 已准备 `clipParamMsRequest.idSeries`。待合并作品应属于同一剧集。 |
| 作品 ID | 每个 `episodes[].id_target` 都是已有作品 ID，不是任务 ID、项目 ID 或 `idMaterialVideo`。 |
| 合并顺序 | 服务端按照 `episodes[]` 的数组顺序合并视频。 |
| `data` 类型 | 顶层 `data` 必须是 JSON 字符串，不能直接传对象。 |
| 字幕 | AI 配音或字幕压制作品通常不需要传 `srt_urls`；字幕擦除等作品如需输出合并后的外挂字幕，可按语言传入字幕 URL。 |
| 结果查询 | 创建响应的 `body` 是合并后作品 ID，可直接用于 `/v-w-c/gateway/ve/work/status`。 |
| 异步处理 | 生产接入推荐传 `callback`；轮询用于主动查询和补偿兜底，初始间隔建议 300 秒。 |

## 请求参数

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `clipParamMsRequest.idSeries` | `Long` | 是 | 剧集 ID。 |
| `projectName` | `String` | 是 | 合并任务名称。 |
| `callback` | `String` | 否 | 回调地址。回调验签、重试和幂等规则见[异步任务、轮询和回调机制](./15-async-and-callbacks.md)。 |
| `data` | `String` | 是 | JSON 字符串，内部包含 `episodes` 数组。 |
| `resolution` | `String` | 是 | 输出分辨率，例如 `1080p`。 |
| `videoCount` | `Integer` | 否 | 待合并视频数量，建议与 `episodes` 长度一致。 |
| `sourceLang` | `String` | 原文未说明 | 原语言。原接口请求示例传空字符串。 |
| `lang` | `String` | 原文未说明 | 目标语言。原接口请求示例使用 `en`。 |

`data` 解码后的结构：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `episodes` | `List<Object>` | 是 | 待合并作品列表，数组顺序就是视频合并顺序。 |
| `episodes[].id_target` | `Long` | 是 | 已有作品 ID。 |
| `episodes[].target_type` | `String` | 是 | 固定传 `WORK`。 |
| `episodes[].srt_urls` | `Dict<String, String>` | 否 | 语言与字幕 URL 的映射，可同时传多语言字幕。 |
| `episodes[].start` | `Number` | 否 | 当前作品的截取起始时间。原接口说明未明确时间单位，不能自行猜测；需要截取时应向 GhostCut 确认单位。 |
| `episodes[].end` | `Number` | 否 | 当前作品的截取结束时间。原接口说明未明确时间单位，不能自行猜测。 |

## `id_target` 从哪里获取

`id_target` 是已经生成的视频作品 ID。常规译制出海任务通常按以下流程获得：

1. 调用 [译制出海任务查询](./53-series-edit-task-list.md)，找到要参与合并的成功任务，读取 `task/list.body[].id`。这个值是任务 ID。
2. 将任务 ID 传给 `/v-w-c/gateway/ve/work/status` 的 `idWorks`。
3. 从响应的 `body.content[].id` 读取作品 ID，并填入本接口的 `episodes[].id_target`。

如果上游接口已经明确直接返回作品 ID，也可以直接使用。不要把 `task/list.body[].id`、`idMaterialVideo` 或剧集 ID 填进 `id_target`。

## 请求体示例

下面的请求按第 1、2、3 集顺序合并，并同时生成日语、韩语两种合并字幕：

```json
{
  "callback": "https://example.com/callback",
  "clipParamMsRequest": {
    "idSeries": 10001
  },
  "data": "{\"episodes\":[{\"id_target\":52467933,\"target_type\":\"WORK\",\"start\":null,\"end\":null,\"srt_urls\":{\"ko\":\"https://example.com/episode-01.ko.srt\",\"ja\":\"https://example.com/episode-01.ja.srt\"}},{\"id_target\":52967934,\"target_type\":\"WORK\",\"start\":null,\"end\":null,\"srt_urls\":{\"ko\":\"https://example.com/episode-02.ko.srt\",\"ja\":\"https://example.com/episode-02.ja.srt\"}},{\"id_target\":52497935,\"target_type\":\"WORK\",\"start\":null,\"end\":null,\"srt_urls\":{\"ko\":\"https://example.com/episode-03.ko.srt\",\"ja\":\"https://example.com/episode-03.ja.srt\"}}]}",
  "lang": "en",
  "projectName": "demo-merged-with-srt.mp4",
  "resolution": "1080p",
  "sourceLang": "",
  "videoCount": 3
}
```

如果不需要合并外挂字幕，省略每个元素的 `srt_urls`：

```json
{
  "id_target": 52467933,
  "target_type": "WORK",
  "start": null,
  "end": null
}
```

## 创建响应

```json
{
  "code": 200,
  "msg": "success",
  "body": 50000001,
  "count": 0,
  "trace": "8d7f4f3b6a2f4b9a9e3c1d2f8a7b6c5d"
}
```

这里的 `body` 是合并后作品 ID。与其他常见译制出海任务不同，不需要先把它当作任务 ID 交给 `task/list` 再换取作品 ID；可以直接查询：

```json
{
  "idWorks": [50000001]
}
```

## 完整 Python 示例

```python
import hashlib
import json
import time

import requests


APP_KEY = "your_app_key"
APP_SECRET = "your_app_secret"
BASE_URL = "https://api.zhaoli.com"


def dumps_body(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def make_app_sign(body_str: str) -> str:
    body_md5hex = hashlib.md5(body_str.encode("utf-8")).hexdigest()
    return hashlib.md5((body_md5hex + APP_SECRET).encode("utf-8")).hexdigest()


def ghostcut_post(path: str, payload: dict) -> dict:
    body_str = dumps_body(payload)
    headers = {
        "Content-Type": "application/json",
        "AppKey": APP_KEY,
        "AppSign": make_app_sign(body_str),
    }
    response = requests.post(
        f"{BASE_URL}{path}",
        headers=headers,
        data=body_str.encode("utf-8"),
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") not in (1000, 200):
        raise RuntimeError(json.dumps(data, ensure_ascii=False, indent=2))
    return data


def build_episode(work_id, srt_urls=None, start=None, end=None):
    episode = {
        "id_target": work_id,
        "target_type": "WORK",
        "start": start,
        "end": end,
    }
    if srt_urls:
        episode["srt_urls"] = srt_urls
    return episode


def create_merge_task(id_series, project_name, episodes, callback=None):
    payload = {
        "clipParamMsRequest": {"idSeries": id_series},
        "data": dumps_body({"episodes": episodes}),
        "lang": "en",
        "projectName": project_name,
        "resolution": "1080p",
        "sourceLang": "",
        "videoCount": len(episodes),
    }
    if callback:
        payload["callback"] = callback
    return ghostcut_post(
        "/v-w-c/gateway/ve/series/edit/task/video/merge",
        payload,
    )


def query_work_status(work_id):
    return ghostcut_post(
        "/v-w-c/gateway/ve/work/status",
        {"idWorks": [work_id]},
    )


def extract_merged_srt_urls(content):
    video_script = content.get("videoScriptProcessDto")
    if isinstance(video_script, list):
        video_script = video_script[0] if video_script else None
    if not isinstance(video_script, dict):
        return {}

    script_data = video_script.get("data")
    if isinstance(script_data, str):
        script_data = json.loads(script_data)
    if not isinstance(script_data, dict):
        return {}

    return script_data.get("result_info", {}).get("merged_srt_urls", {})


def wait_for_result(work_id, interval_seconds=300):
    while True:
        result = query_work_status(work_id)
        content = result["body"]["content"][0]
        status = content["processStatus"]

        if status == 1:
            return content
        if isinstance(status, int) and status > 1:
            error = content.get("errorDetail") or content.get("error_detail")
            raise RuntimeError(error or f"processStatus={status}")

        time.sleep(interval_seconds)


episodes = [
    build_episode(
        52467933,
        srt_urls={
            "ko": "https://example.com/episode-01.ko.srt",
            "ja": "https://example.com/episode-01.ja.srt",
        },
    ),
    build_episode(
        52967934,
        srt_urls={
            "ko": "https://example.com/episode-02.ko.srt",
            "ja": "https://example.com/episode-02.ja.srt",
        },
    ),
]

create_result = create_merge_task(
    id_series=10001,
    project_name="demo-merged-with-srt.mp4",
    episodes=episodes,
    callback="https://example.com/callback",
)

merge_work_id = int(create_result["body"])
print("merge work id:", merge_work_id)

final_content = wait_for_result(merge_work_id)
print("videoUrl:", final_content.get("videoUrl"))
print("merged_srt_urls:", extract_merged_srt_urls(final_content))
```

## 结果字段

`/v-w-c/gateway/ve/work/status` 成功后：

| 结果 | 字段路径 |
| --- | --- |
| 合并后视频 | `body.content[0].videoUrl` |
| 合并后多语言字幕 | `body.content[0].videoScriptProcessDto.data.result_info.merged_srt_urls` |

`videoScriptProcessDto.data` 通常是 JSON 字符串，需要先执行 `json.loads()`。解析后示意：

```json
{
  "result_info": {
    "merged_srt_urls": {
      "ko": "https://example.com/merged.ko.srt",
      "ja": "https://example.com/merged.ja.srt"
    }
  }
}
```

## `srt_urls` 使用规则

- `srt_urls` 的键表示字幕语言，值是该集对应语言的字幕 URL。
- 要生成多语言合并字幕时，每个 `episodes[]` 元素可同时传多个语言。
- AI 配音、字幕压制任务生成的作品通常无需传 `srt_urls`。
- 字幕擦除等作品本身没有新字幕；如果合并结果还需要外挂字幕，应为对应作品传 `srt_urls`。
- 各集应尽量使用一致的语言集合。某一集缺少某个语言时，不要用其他集字幕或空字符串替代；应确认业务是否允许该语言在这一集缺失。

## Agent 决策规则

- 用户要把同一剧集下多个已有作品拼成长视频时，使用本接口。
- `episodes[]` 的顺序决定成片顺序，不要按作品 ID 或文件名自行排序。
- `id_target` 必须填作品 ID。不要填 `task/list.body[].id`、`idSeries` 或 `idMaterialVideo`。
- 顶层 `data` 必须通过 `json.dumps({"episodes": episodes})` 生成 JSON 字符串。
- 不要把通用译制出海 `items[] / workDto / videoEditParamsDto` 模板套到本接口。
- 创建响应的 `body` 已经是合并后作品 ID，可直接调用 `/work/status`。
- 合并成功后读取 `videoUrl`；只有传了 `srt_urls` 且需要外挂字幕时，才进一步解析 `merged_srt_urls`。
- `start`、`end` 的时间单位是秒。

## 相关文档

- [译制出海剪辑 API 总览](./51-series-overview.md)：查看模块适用边界和整体流程。
- [译制出海任务查询](./53-series-edit-task-list.md)：使用 `SERIES_CLIP66` 查询长视频合成任务。
- [视频任务状态查询](./11-work-status-query.md)：使用创建响应 `body` 中的作品 ID 查询结果。
- [异步任务、轮询和回调机制](./15-async-and-callbacks.md)：查看 callback、验签、重试、幂等和补偿轮询规则。
- [素材 URL 与格式要求](./03-media-requirements.md)：查看字幕 URL 和文件格式约束。
