#!/usr/bin/env python3
"""GhostCut API helper for signed JSON requests, uploads, and status queries."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import sys
import uuid
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://api.zhaoli.com"


def import_requests():
    try:
        import requests
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise SystemExit("Missing dependency: install requests before running this script.") from exc
    return requests


def dumps_body(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def make_app_sign(body_str: str, app_secret: str) -> str:
    body_md5hex = hashlib.md5(body_str.encode("utf-8")).hexdigest()
    return hashlib.md5((body_md5hex + app_secret).encode("utf-8")).hexdigest()


def get_credentials(args: argparse.Namespace) -> tuple[str, str]:
    app_key = args.app_key or os.environ.get("GHOSTCUT_APP_KEY")
    app_secret = args.app_secret or os.environ.get("GHOSTCUT_APP_SECRET")
    if not app_key or not app_secret:
        raise SystemExit(
            "Missing credentials. Set GHOSTCUT_APP_KEY and GHOSTCUT_APP_SECRET, "
            "or pass --app-key and --app-secret."
        )
    return app_key, app_secret


def get_app_secret(args: argparse.Namespace) -> str:
    app_secret = args.app_secret or os.environ.get("GHOSTCUT_APP_SECRET")
    if not app_secret:
        raise SystemExit("Missing AppSecret. Set GHOSTCUT_APP_SECRET or pass --app-secret.")
    return app_secret


def load_payload(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    path = Path(value)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def api_post(
    path: str,
    payload: dict[str, Any],
    app_key: str,
    app_secret: str,
    base_url: str = DEFAULT_BASE_URL,
    timeout: int = 30,
) -> dict[str, Any]:
    requests = import_requests()
    body_str = dumps_body(payload)
    headers = {
        "Content-Type": "application/json",
        "AppKey": app_key,
        "AppSign": make_app_sign(body_str, app_secret),
    }
    response = requests.post(
        f"{base_url.rstrip('/')}{path}",
        headers=headers,
        data=body_str.encode("utf-8"),
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 1000:
        raise RuntimeError(f"GhostCut API failed: {json.dumps(data, ensure_ascii=False)}")
    return data


def file_base64_md5(local_file_path: Path) -> str:
    digest = hashlib.md5(local_file_path.read_bytes()).digest()
    return base64.b64encode(digest).decode("utf-8")


def infer_material_file_type(local_file_path: Path) -> str:
    suffix = local_file_path.suffix.lower()
    if suffix == ".srt":
        return "srt"
    if suffix in {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".mpg", ".m3u8", ".webm"}:
        return "video"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return "image"
    guessed, _ = mimetypes.guess_type(str(local_file_path))
    if guessed and guessed.startswith("video/"):
        return "video"
    if guessed and guessed.startswith("image/"):
        return "image"
    return "image"


def upload_with_policy(
    local_file_path: Path,
    policy_body: dict[str, Any],
    filename: str | None = None,
    timeout: int = 120,
) -> dict[str, str]:
    requests = import_requests()
    upload_name = filename or local_file_path.name
    key = f"{policy_body['dir']}{upload_name}"
    form_data = {
        "key": key,
        "OSSAccessKeyId": policy_body["accessid"],
        "policy": policy_body["policy"],
        "signature": policy_body["signature"],
        "callback": policy_body["base64CallbackBody"],
        "success_action_status": "200",
    }

    with local_file_path.open("rb") as file_obj:
        response = requests.post(
            policy_body["host"],
            data=form_data,
            files={"file": (upload_name, file_obj)},
            timeout=timeout,
        )
    response.raise_for_status()
    if response.text.strip() != '{"Status":"OK"}':
        raise RuntimeError(f"OSS upload failed: {response.text}")

    server_md5 = response.headers.get("Content-MD5")
    if server_md5 and server_md5 != file_base64_md5(local_file_path):
        raise RuntimeError("OSS upload md5 mismatch")

    return {"url": f"{policy_body['urlPrefix']}{upload_name}", "key": key}


def command_sign(args: argparse.Namespace) -> None:
    app_secret = get_app_secret(args)
    payload = load_payload(args.payload)
    body_str = dumps_body(payload)
    print(make_app_sign(body_str, app_secret))


def command_post(args: argparse.Namespace) -> None:
    app_key, app_secret = get_credentials(args)
    data = api_post(
        path=args.path,
        payload=load_payload(args.payload),
        app_key=app_key,
        app_secret=app_secret,
        base_url=args.base_url,
        timeout=args.timeout,
    )
    print(json.dumps(data, ensure_ascii=False, indent=2))


def command_upload(args: argparse.Namespace) -> None:
    app_key, app_secret = get_credentials(args)
    local_file_path = Path(args.file).expanduser().resolve()
    if not local_file_path.is_file():
        raise SystemExit(f"File not found: {local_file_path}")

    material_file_type = args.material_file_type or infer_material_file_type(local_file_path)
    payload: dict[str, Any] = {
        "nonce": uuid.uuid4().hex,
        "materialFileType": material_file_type,
    }
    if args.id_series is not None:
        payload["idSeries"] = args.id_series
    if args.id_material_video is not None:
        payload["idMaterialVideo"] = args.id_material_video
    if args.material_name:
        payload["materialName"] = args.material_name
    if args.file_name:
        payload["fileName"] = args.file_name
    if args.source_lang:
        payload["sourceLang"] = args.source_lang
    if args.expire_seconds is not None:
        payload["expireSeconds"] = args.expire_seconds

    policy = api_post(
        path="/v-w-c/gateway/ve/file/upload/policy/apply",
        payload=payload,
        app_key=app_key,
        app_secret=app_secret,
        base_url=args.base_url,
        timeout=args.timeout,
    )["body"]
    upload_result = upload_with_policy(
        local_file_path=local_file_path,
        policy_body=policy,
        filename=args.filename,
        timeout=args.upload_timeout,
    )
    result = {"upload": upload_result, "policyBody": policy}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def classify_status(process_status: Any) -> str:
    if process_status == 1:
        return "success"
    if isinstance(process_status, int) and process_status < 1:
        return "processing"
    return "failed"


def command_work_status(args: argparse.Namespace) -> None:
    app_key, app_secret = get_credentials(args)
    data = api_post(
        path="/v-w-c/gateway/ve/work/status",
        payload={"idWorks": args.ids},
        app_key=app_key,
        app_secret=app_secret,
        base_url=args.base_url,
        timeout=args.timeout,
    )
    content = data.get("body", {}).get("content", [])
    summary = [
        {
            "id": item.get("id"),
            "state": classify_status(item.get("processStatus")),
            "processStatus": item.get("processStatus"),
            "videoUrl": item.get("videoUrl"),
            "srcSrtUrl": item.get("srcSrtUrl"),
            "tgtSrtUrl": item.get("tgtSrtUrl"),
            "errorDetail": item.get("errorDetail") or item.get("error_detail"),
        }
        for item in content
    ]
    print(json.dumps({"summary": summary, "raw": data}, ensure_ascii=False, indent=2))


def command_point_balance(args: argparse.Namespace) -> None:
    app_key, app_secret = get_credentials(args)
    data = api_post(
        path="/v-w-c/gateway/ve/point/query",
        payload={"notZero": True, "isValid": True},
        app_key=app_key,
        app_secret=app_secret,
        base_url=args.base_url,
        timeout=args.timeout,
    )
    assets = data.get("body", {}).get("pointAssets", [])
    total_balance = sum(float(asset.get("pointBalance") or 0) for asset in assets)
    print(
        json.dumps(
            {
                "summary": {
                    "totalPointBalance": total_balance,
                    "assetCount": len(assets),
                },
                "assets": assets,
                "raw": data,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def command_task_list(args: argparse.Namespace) -> None:
    app_key, app_secret = get_credentials(args)
    payload = load_payload(args.payload)
    if args.id_series is not None:
        payload["idSeries"] = args.id_series
    if args.ids:
        payload["ids"] = args.ids
    if args.task_type:
        payload["taskType"] = args.task_type
    if args.task_type_in:
        payload["taskTypeIn"] = args.task_type_in
    payload.setdefault("deleted", 0)
    payload.setdefault("pageNumber", 1)
    payload.setdefault("pageSize", 20)

    data = api_post(
        path="/v-w-c/gateway/ve/series/edit/task/list",
        payload=payload,
        app_key=app_key,
        app_secret=app_secret,
        base_url=args.base_url,
        timeout=args.timeout,
    )
    print(json.dumps(data, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GhostCut API helper")
    parser.add_argument("--app-key", help="GhostCut AppKey. Defaults to GHOSTCUT_APP_KEY.")
    parser.add_argument("--app-secret", help="GhostCut AppSecret. Defaults to GHOSTCUT_APP_SECRET.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=int, default=30)
    subparsers = parser.add_subparsers(dest="command", required=True)

    sign = subparsers.add_parser("sign", help="Print AppSign for a JSON payload.")
    sign.add_argument("--payload", required=True, help="JSON string or path to a JSON file.")
    sign.set_defaults(func=command_sign)

    post = subparsers.add_parser("post", help="POST a signed GhostCut JSON request.")
    post.add_argument("--path", required=True, help="API path, for example /v-w-c/gateway/ve/work/status.")
    post.add_argument("--payload", required=True, help="JSON string or path to a JSON file.")
    post.set_defaults(func=command_post)

    upload = subparsers.add_parser("upload", help="Upload a local file and print URL/key.")
    upload.add_argument("--file", required=True, help="Local file path.")
    upload.add_argument("--filename", help="Object filename used for OSS upload.")
    upload.add_argument("--material-file-type", help="image, video, srt, video_series, srt_series, etc.")
    upload.add_argument("--id-series", type=int)
    upload.add_argument("--id-material-video", type=int)
    upload.add_argument("--material-name")
    upload.add_argument("--file-name")
    upload.add_argument("--source-lang")
    upload.add_argument("--expire-seconds", type=int)
    upload.add_argument("--upload-timeout", type=int, default=120)
    upload.set_defaults(func=command_upload)

    work_status = subparsers.add_parser("work-status", help="Query /v-w-c/gateway/ve/work/status.")
    work_status.add_argument("ids", nargs="+", help="Work IDs, or Series task/project IDs when following Series docs.")
    work_status.set_defaults(func=command_work_status)

    point_balance = subparsers.add_parser("point-balance", help="Query current AppKey point card balance.")
    point_balance.set_defaults(func=command_point_balance)

    task_list = subparsers.add_parser("task-list", help="Query Series Editing task/list.")
    task_list.add_argument("--payload", help="Optional JSON string or path to a JSON file.")
    task_list.add_argument("--id-series", type=int)
    task_list.add_argument("--ids", type=int, nargs="+")
    task_list.add_argument("--task-type")
    task_list.add_argument("--task-type-in", nargs="+")
    task_list.set_defaults(func=command_task_list)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
