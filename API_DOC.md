# JavDB 榜单 API 接口文档

## 1. 基础信息
*   **接口描述**：获取第三方整理的 JavDB 最新影片排行榜数据。返回按分类结构化的影片番号及数量信息。
*   **请求方式**：`GET`
*   **接口地址**：`http://144.22.152.14:8043/api/v1/rank/share`
*   **鉴权方式**：必须通过 **Headers** 传递 `X-API-Key`，否则会返回 401。

## 2. 请求控制
### 2.1 请求头 (Headers)
| Header Name | 类型 | 是否必填 | 示例值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `X-API-Key` | `string` | **是** | `lUeSG5wb7CB7xYG3JQZj5O8z0Zh5kkAK` | API 授权密钥，不提供会报错 |

### 2.2 请求参数 (Query)
| 参数名 | 类型 | 是否必填 | 默认 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `rank_type` | `string` | 否 | 全部 | 限定榜单类型，如 `movie` (影片榜), `cast` (演员榜) |
| `rank_name` | `string` | 否 | 全部 | 筛选单个特定榜单，如 `javdb-0-daily` |

## 3. 榜单名映射关系对照表
API 实测返回的 `rank_name` 与官方源分类的对照关系：
*   **有码 (Censored: 0)**
    *   `javdb-0-daily`  → JavDB-有码-日榜
    *   `javdb-0-weekly` → JavDB-有码-周榜
    *   `javdb-0-monthly`→ JavDB-有码-月榜
*   **无码 (Uncensored: 1)**
    *   `javdb-1-daily`  → JavDB-无码-日榜
    *   `javdb-1-weekly` → JavDB-无码-周榜
    *   `javdb-1-monthly`→ JavDB-无码-月榜
*   **FC2 (Type: 3)**
    *   `javdb-3-daily`  → JavDB-FC2-日榜
    *   `javdb-3-weekly` → JavDB-FC2-周榜
    *   `javdb-3-monthly`→ JavDB-FC2-月榜

## 4. 响应参数说明 (JSON)
成功请求后 (`HTTP 200`)，返回 `code: 0` 和实际的 `data` 对象。
```json
{
  "code": 0,
  "message": "请求成功",
  "data": {
    "ranks": [
      {
        "rank_type": "movie",
        "rank_name": "javdb-0-daily",
        "numbers": [
          "ABF-340",
          "ABF-338",
          "SNOS-177"
        ],
        "count": 100,
        "sync_time": "2026-04-11T00:00:00Z"
      }
    ]
  }
}
```

### 错误处理
若返回 `code` 非 `0` 或 HTTP 状态码为 `401`，通常是因为 `X-API-Key` 校验失败：
```json
{"code":401,"message":"API Key 或 Token 授权失败"}
```

## 5. 调用示例代码 (Python)
```python
import requests

url = "http://144.22.152.14:8043/api/v1/rank/share"
headers = {
    "X-API-Key": "lUeSG5wb7CB7xYG3JQZj5O8z0Zh5kkAK"
}
response = requests.get(url, headers=headers)
data = response.json()

if data.get("code") == 0:
    for rank in data["data"]["ranks"]:
        print(f"榜单: {rank['rank_name']}, 条目数: {rank['count']}")
```