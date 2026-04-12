import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = f"{os.getenv('EMBY_SERVER').rstrip('/')}/Users/{os.getenv('EMBY_USER_ID')}/Items"
params = {
    "IncludeItemTypes": "Movie",
    "Recursive": "true",
    "Limit": "1",
    "Fields": "Path,MediaSources"
}
headers = {"X-Emby-Token": os.getenv("EMBY_API_KEY")}
res = requests.get(url, headers=headers, params=params)
print(res.json().get('Items', []))
