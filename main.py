import logging
import sys
import os
import shutil
from scraper import fetch_rankings
from matcher import match_items
from emby_client import EmbyClient
from config import COLLECTION_MAPPING, MAX_RANK_SIZE, ENABLE_FOLDER_COPY, COPY_TARGET_DIR, PATH_MAPPING

# 配置日志记录，输出到控制台及文件
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("rankings_sync.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    logging.info("=== 开始执行 JavDB 榜单同步到 Emby 脚本 ===")
    
    # 步骤 1: 从 API 获取榜单数据
    all_rankings = fetch_rankings("movie")
    if not all_rankings:
        logging.error("没有从 API 获取到任何榜单数据，退出程序。")
        return
        
    # 步骤 2: 初始化 Emby 客户端并获取全部影片库
    emby = EmbyClient()
    emby_movies = emby.get_all_movies()
    if not emby_movies:
        logging.error("没有读取到 Emby 中的任何影片，退出程序。")
        return
        
    # 解析从 API 获取的榜单
    for rank_data in all_rankings:
        api_rank_name = rank_data.get("rank_name")
        
        # 只处理我们在配置中定义的目标合集
        if api_rank_name not in COLLECTION_MAPPING:
            continue
            
        target_col_name = COLLECTION_MAPPING[api_rank_name]
        logging.info(f"\n--- 正在处理榜单: {target_col_name} (原名 {api_rank_name}) ---")
        
        # 提取番号 (实测字段为 numbers)
        codes = rank_data.get("numbers", [])[:MAX_RANK_SIZE]
        
        if not codes:
            logging.warning(f"榜单 {target_col_name} 中没有提取到有效的番号。")
            continue
            
        # 步骤 3: 匹配番号
        matched_ids, unmatched_codes = match_items(emby_movies, codes)
        
        # 打印统计信息
        logging.info(f"榜单总条目: {len(codes)}")
        logging.info(f"成功匹配数: {len(matched_ids)}")
        logging.info(f"未匹配的番号: {', '.join(unmatched_codes[:10])}{' ...' if len(unmatched_codes) > 10 else ''}")
        
        # 步骤 4: 更新 Emby 合集
        if matched_ids:
            emby.update_collection(target_col_name, matched_ids)
            
            # --------- 步骤 5: 物理文件夹同步 (可选) ---------
            if ENABLE_FOLDER_COPY and COPY_TARGET_DIR:
                target_dir = os.path.join(COPY_TARGET_DIR, target_col_name)
                logging.info(f"正在同步物理媒体文件夹到: {target_dir}")
                
                # 如果这个榜单文件夹之前存在，先清空它（为了保持完全干净的最新排名数据）
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir, ignore_errors=True)
                os.makedirs(target_dir, exist_ok=True)
                
                # 构建 Emby 影片数据映射 {Id: Path} 以供查询
                emby_movie_map = {str(item.get("Id")): item.get("Path") for item in emby_movies if item.get("Path")}
                
                copied_count = 0
                for item_id in matched_ids:
                    src_file_path = emby_movie_map.get(str(item_id))
                    
                    if src_file_path:
                        for docker_path, host_path in PATH_MAPPING.items():
                            if src_file_path.startswith(docker_path):
                                src_file_path = src_file_path.replace(docker_path, host_path, 1)
                                break
                                
                    if src_file_path and os.path.exists(src_file_path):
                        # 获取影片所处的上一级文件夹路径
                        src_dir = os.path.dirname(src_file_path)
                        dir_name = os.path.basename(src_dir)
                        dest_dir = os.path.join(target_dir, dir_name)
                        
                        try:
                            # 复制整座影片文件夹（含 strm, nfo, jpg 等）
                            shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
                            copied_count += 1
                        except Exception as e:
                            logging.error(f"复制物理文件夹 '{dir_name}' 失败: {e}")
                
                logging.info(f"成功将 {copied_count} 部影片所在文件夹复制到 {target_dir}")
        else:
            logging.warning(f"合集 {target_col_name} 没有任何匹配项，跳过创建。")

    logging.info("=== 榜单同步任务执行完毕 ===")

if __name__ == "__main__":
    main()
