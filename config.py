import os
from dotenv import load_dotenv

# 加载 .env 环境变量文件
load_dotenv()

# Emby 服务器配置
EMBY_SERVER = os.getenv("EMBY_SERVER", "http://localhost:8096")
EMBY_API_KEY = os.getenv("EMBY_API_KEY", "")
EMBY_USER_ID = os.getenv("EMBY_USER_ID", "")

# 可选：限制扫描的库 ID（逗号分隔），为空则扫描所有电影
LIBRARY_IDS = os.getenv("LIBRARY_IDS", "") 

# 排行榜 API 配置
RANK_API_URL = os.getenv("RANK_API_URL", "http://144.22.152.14:8043/api/v1/rank/share")
RANK_API_KEY = os.getenv("RANK_API_KEY", "")

# 代理设置（如果需要）
PROXIES = {
    # "http": "http://127.0.0.1:7890",
    # "https": "http://127.0.0.1:7890"
}

# 榜单名称映射：API 返回的 rank_name 映射为你期望的 Emby 合集名称
COLLECTION_MAPPING = {
    "javdb-0-daily": "JavDB-有码-日榜",
    "javdb-0-weekly": "JavDB-有码-周榜",
    "javdb-0-monthly": "JavDB-有码-月榜",
    "javdb-1-daily": "JavDB-无码-日榜",
    "javdb-1-weekly": "JavDB-无码-周榜",
    "javdb-1-monthly": "JavDB-无码-月榜",
    "javdb-3-daily": "JavDB-FC2-日榜",
    "javdb-3-weekly": "JavDB-FC2-周榜",
    "javdb-3-monthly": "JavDB-FC2-月榜",
    "library-vl_bestrated": "JAVLibrary-高分榜",
    "library-vl_mostwanted": "JAVLibrary-最想要",
    "library-star_mostfav": "JAVLibrary-热门演员"
}

# 限制保存的榜单大小（例如只取前 100）
MAX_RANK_SIZE = int(os.getenv("MAX_RANK_SIZE", "100"))

# ----------------- 物理文件/文件夹同步设置 -----------------
# 是否物理复制匹配的影视所在的文件夹到指定目录（适用于 strm / 本地直接拷贝分类）
ENABLE_FOLDER_COPY = os.getenv("ENABLE_FOLDER_COPY", "True").lower() in ('true', '1', 't')
# 复制的目标根目录，将会在此目录下根据榜单名称创建子文件夹
COPY_TARGET_DIR = os.getenv("COPY_TARGET_DIR", "/root")

# 路径映射：如果 Emby 运行在 Docker 中，而脚本运行在宿主机上，
# Emby API 返回的路径是容器内路径（如 /media/movies），
# 宿主机的真实路径可能是 /home/user/media/movies。
# 可以在此处配置映射，格式为：{"容器内路径前缀": "宿主机路径前缀"}
# 例如：{"/media": "/home/user/media"}
PATH_MAPPING = {
    "/strm": "/root/strm"
}

