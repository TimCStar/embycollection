import requests
import logging
from config import EMBY_SERVER, EMBY_API_KEY, EMBY_USER_ID, LIBRARY_IDS

class EmbyClient:
    def __init__(self):
        self.base_url = EMBY_SERVER.rstrip('/')
        self.api_key = EMBY_API_KEY
        self.user_id = EMBY_USER_ID
        self.headers = {
            "Content-Type": "application/json",
            "X-Emby-Token": self.api_key
        }
        
    def get_all_movies(self):
        """
        获取 Emby 媒体库中的所有影片 (核心优化点: 采用一次性批量拉取策略)
        
        策略选择说明:
        比起对榜单上的 100~900 个番号分别进行上百次单独的 API 搜索查询，
        让 Emby 一次性吐出全部电影的 [编号, 原名] 是最优解（O(1) 连线 vs O(N) 连线）。
        剥离了图片、简介等冗余元数据后，即便库中有 50000 部影片，返回的 JSON 也只有几 MB，
        在 Python 字典中进行匹配仅需几毫秒，对 Emby 的数据库压力和被封禁/卡顿的风险最小。
        """
        logging.info("正在一次性批量获取 Emby 数据建构本地匹配索引，以节省 API 请求数...")
        url = f"{self.base_url}/Users/{self.user_id}/Items"
        
        params = {
            "IncludeItemTypes": "Movie",
            "Recursive": "true",
            # 为了极致压缩回传大小，只要求返回必定需要的匹配字段 OriginalTitle 和为了复制文件必要的 Path。
            # Id 和 Name 是 Emby API 必定默认返回的基础字段。
            "Fields": "OriginalTitle,Path"
        }
        
        if LIBRARY_IDS:
            params["ParentId"] = LIBRARY_IDS
            
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("Items", [])
        logging.info(f"共获取到 {len(items)} 部影片。")
        return items

    def get_collections(self):
        """
        获取当前所有的合集 (Collections)
        """
        url = f"{self.base_url}/Users/{self.user_id}/Items"
        params = {
            "IncludeItemTypes": "BoxSet",
            "Recursive": "true"
        }
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("Items", [])

    def delete_item(self, item_id):
        """
        删除指定的项（用于删除合集本身以清空内容）
        不会删除媒体文件
        """
        url = f"{self.base_url}/Items/{item_id}"
        requests.delete(url, headers=self.headers)

    def create_collection(self, name, item_ids):
        """
        创建新的合集，并添加指定项目
        """
        if not item_ids:
            logging.warning(f"由于没有匹配的影片，跳过创建合集 '{name}'。")
            return
            
        url = f"{self.base_url}/Collections"
        params = {
            "Name": name,
            "Ids": ",".join(item_ids)
        }
        
        response = requests.post(url, headers=self.headers, params=params)
        response.raise_for_status()
        logging.info(f"成功创建/更新合集: {name}")

    def get_collection_items(self, collection_id):
        """获取合集内当前所有的项目 ID"""
        url = f"{self.base_url}/Users/{self.user_id}/Items"
        params = {
            "ParentId": collection_id,
            "Fields": "Id"
        }
        res = requests.get(url, headers=self.headers, params=params)
        res.raise_for_status()
        items = res.json().get("Items", [])
        return [item.get("Id") for item in items]

    def add_items_to_collection(self, collection_id, item_ids):
        """将选定影片添加到该合集"""
        if not item_ids: return
        url = f"{self.base_url}/Collections/{collection_id}/Items"
        params = {"Ids": ",".join(item_ids)}
        requests.post(url, headers=self.headers, params=params).raise_for_status()

    def remove_items_from_collection(self, collection_id, item_ids):
        """从该合集中移除给定影片"""
        if not item_ids: return
        url = f"{self.base_url}/Collections/{collection_id}/Items"
        params = {"Ids": ",".join(item_ids)}
        requests.delete(url, headers=self.headers, params=params).raise_for_status()

    def update_collection(self, name, item_ids):
        """
        更新合集：采取增量更新策略，保留原有合集和它的元数据（如自定义封面）
        自动计算并处理需要新增或移出的榜单影片。
        """
        collections = self.get_collections()
        target_collection = next((c for c in collections if c.get("Name") == name), None)
        
        if target_collection:
            collection_id = target_collection.get("Id")
            logging.info(f"正在增量更新合集: {name} (ID: {collection_id})")
            
            current_ids = self.get_collection_items(collection_id)
            current_ids_set = set(current_ids)
            new_ids_set = set(item_ids)
            
            to_add = [idx for idx in item_ids if idx not in current_ids_set]
            to_remove = [idx for idx in current_ids if idx not in new_ids_set]
            
            if to_remove:
                logging.info(f"   -> 移出 {len(to_remove)} 个已落榜的影片")
                self.remove_items_from_collection(collection_id, to_remove)
                
            if to_add:
                logging.info(f"   -> 增加 {len(to_add)} 个新上榜的影片")
                self.add_items_to_collection(collection_id, to_add)
                
            if not to_add and not to_remove:
                logging.info("   -> 该榜单目前已经是最新，无需任何修改。")
        else:
            logging.info(f"首次创建合集并分配内容: {name}")
            self.create_collection(name, item_ids)

