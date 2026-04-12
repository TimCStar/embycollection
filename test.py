import os
import requests
from dotenv import load_dotenv

load_dotenv()
try:
    url = f"{os.getenv('EMBY_SERVER').rstrip('/')}/Users/{os.getenv('EMBY_USER_ID')}/Items"
    params = {
        "IncludeItemTypes": "Movie",
        "Limit": "5",
        "Fields": "Path"
    }
    headers = {"X-Emby-Token": os.getenv("EMBY_API_KEY")}
    res = requests.get(url, headers=headers, params=params)
    items = res.json().get('Items', [])
    for it in items:
        print(f"Id={it.get('Id')}, Path={it.get('Path')}, Exists={os.path.exists(it.get('Path', ''))}")
except Exception as e:
    print(e)
