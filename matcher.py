import re
import logging

def normalize_code(code):
    """
    归一化番号格式
    规则：转为大写，去除连字符 '-'，去除所有括号、空格等无关字符
    例如：ABP-123 -> ABP123, [ABP-123] -> ABP123, abp 123 -> ABP123
    """
    if not code:
        return ""
    
    # 转换为大写
    code = code.upper()
    # 移除非字母数字字符
    code = re.sub(r'[^A-Z0-9]', '', code)
    
    return code

def match_items(emby_items, ranking_codes):
    """
    将排行榜中的番号与 Emby 媒体库中的项进行匹配
    emby_items: 从 Emby 获取的视频列表
    ranking_codes: 从排行榜中获取的番号列表
    返回: 匹配上的 Emby Item ID 列表，未匹配的番号列表
    """
    # 构建 Emby 影片字典，键为归一化后的番号，值为 Item ID
    emby_dict = {}
    for item in emby_items:
        # 提取文件名或名称作为原始番号
        # 实际情况中，Emby item_name 可能包含额外信息，所以如果名称就是番号或包含番号，可以做模糊/精确匹配
        name = item.get("Name", "")
        # 先以最基础的方式归一化名称
        norm_name = normalize_code(name)
        emby_dict[norm_name] = item.get("Id")
        
        # 如果有 OriginalTitle 也可以放入
        if "OriginalTitle" in item:
            emby_dict[normalize_code(item["OriginalTitle"])] = item.get("Id")

    matched_ids = []
    unmatched_codes = []

    # 遍历榜单中的番号，寻找匹配项
    for code in ranking_codes:
        norm_code = normalize_code(code)
        
        # 简单匹配：遍历寻找包含关系或者直接匹配
        found_id = None
        for e_code, e_id in emby_dict.items():
            if norm_code and norm_code in e_code:
                found_id = e_id
                break
        
        if found_id:
            matched_ids.append(found_id)
        else:
            unmatched_codes.append(code)
            
    # 去重并保持原始顺序
    matched_ids = list(dict.fromkeys(matched_ids))
    
    return matched_ids, unmatched_codes
