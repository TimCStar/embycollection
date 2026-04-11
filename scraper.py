import requests
import logging
from config import RANK_API_URL, RANK_API_KEY, PROXIES

# 从提供的 API 端点获取榜单数据
def fetch_rankings(rank_type="movie"):
    """
    获取指定类型的榜单数据
    """
    logging.info(f"正在从 API 获取榜单数据: {RANK_API_URL}")
    headers = {
        "X-API-Key": RANK_API_KEY
    }
    params = {"rank_type": rank_type}
    
    try:
        response = requests.get(RANK_API_URL, headers=headers, params=params, proxies=PROXIES, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # 校验成功码
        if data.get("code") == 0:
            logging.info("成功获取榜单数据")
            return data.get("data", {}).get("ranks", [])
        else:
            logging.error(f"API 返回业务错误: {data.get('message')}")
            return []
            
    except Exception as e:
        logging.error(f"获取榜单数据失败: {e}")
        return []

