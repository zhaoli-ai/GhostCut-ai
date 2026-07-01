# 点卡余额查询

> 本文说明如何查询当前 `AppKey` 对应商户的点卡余额。该接口是同步查询接口，不创建异步任务，也不需要轮询或 callback。

## 什么时候调用

当用户想了解账户余额、点卡余额、可用点数、商户剩余点数，或在提交处理任务前确认是否还有可用点卡时，调用本文接口。

## 接口

```http
POST https://api.zhaoli.com/v-w-c/gateway/ve/point/query
Content-Type: application/json
AppKey: <your_app_key>
AppSign: <generated_app_sign>
```

请求体固定传：

```json
{
  "notZero": true,
  "isValid": true
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `notZero` | `boolean` | 是 | 固定传 `true`，只查询余额不为 0 的点卡资产。 |
| `isValid` | `boolean` | 是 | 固定传 `true`，只查询当前有效的点卡资产。 |

签名规则和 `api_post` 封装方式见[API 凭证与签名](./02-auth-and-sign.md)。

## 响应读取

接口成功时，外层通常返回 `code=1000`，点卡资产列表位于 `body.pointAssets`。

示例响应结构：

```json
{
  "body": {
    "pointAssets": [
      {
        "id": 2209040,
        "company": "A-00b4943646344cfc",
        "uid": "00b4943646344cfcb0be3759800b2cba",
        "ctime": 1782836374297,
        "lutime": 1782836374297,
        "pointAmount": 3.0,
        "pointBalance": 3.0,
        "expireTime": 1785428374292,
        "orderNo": "",
        "remark": "邀请用户~获得奖励点卡"
      },
      {
        "id": 1308671,
        "company": "A-00b4943646344cfc",
        "uid": "00b4943646344cfcb0be3759800b2cba",
        "ctime": 1717640417453,
        "lutime": 1782808236584,
        "pointAmount": 1000000.0,
        "pointBalance": 651768.8,
        "expireTime": 1843006817450,
        "orderNo": "",
        "remark": "赠送点卡"
      }
    ]
  },
  "code": 1000,
  "count": 2,
  "msg": "success"
}
```

常用字段：

| 字段 | 说明 |
| --- | --- |
| `body.pointAssets[]` | 当前 `AppKey` 对应商户的有效点卡资产列表。 |
| `pointAmount` | 该点卡资产原始点数。 |
| `pointBalance` | 该点卡资产当前剩余点数。 |
| `expireTime` | 过期时间，通常为毫秒时间戳。 |
| `remark` | 点卡来源或备注。 |
| `ctime` / `lutime` | 创建时间和最后更新时间，通常为毫秒时间戳。 |
| `uid` / `company` | 用户和商户标识。 |
| `count` | 返回的点卡资产数量。 |

响应中还可能包含 `activityNumber`、`idZlPointPackage`、`isCdKey`、`orderNo` 等点卡资产元数据；查询余额时通常不需要参与计算。

如果只需要展示总余额，可对所有 `pointAssets[].pointBalance` 求和。

## Python 查询示例

在 skill 根目录中，也可以直接使用随附脚本：

```bash
python scripts/ghostcut_api.py point-balance
```

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


def query_point_balance() -> dict:
    result = api_post("/v-w-c/gateway/ve/point/query", {
        "notZero": True,
        "isValid": True,
    })

    assets = result.get("body", {}).get("pointAssets", [])
    total_balance = sum(float(asset.get("pointBalance") or 0) for asset in assets)

    return {
        "total_balance": total_balance,
        "asset_count": len(assets),
        "assets": assets,
        "raw": result,
    }


if __name__ == "__main__":
    balance = query_point_balance()
    print(f"可用点卡总余额: {balance['total_balance']}")
    print(f"有效点卡数量: {balance['asset_count']}")
```

## Agent 决策规则

- 用户问账户余额、点卡余额、可用点数、剩余点数、商户余额时，调用本文接口。
- 请求体中的 `notZero` 和 `isValid` 都固定传 `true`。
- 本接口不创建处理任务，不返回 `work_id`，也不需要查 `/work/status`。
- 外层 `code=1000` 表示查询请求成功；余额数据读取 `body.pointAssets[].pointBalance`。
- 如果返回空列表，表示当前筛选条件下没有有效且余额不为 0 的点卡资产。

## 相关文档

- [API 凭证与签名](./02-auth-and-sign.md)：查看认证和签名规则。
- [API 总览](./00-api-overview.md)：查看功能选择入口和主要调用流程。
