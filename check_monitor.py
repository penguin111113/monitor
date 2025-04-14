import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.fancrew.jp/search/result/4"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def get_monitor_count():
    res = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, 'html.parser')

    count_elem = soup.find("div", class_="searchResultCount")
    if count_elem:
        print("取得できたテキスト:", count_elem.text)  # デバッグ用
        match = re.search(r"/\s*([\d,]+)件", count_elem.text)
        if match:
            return int(match.group(1).replace(",", ""))

    raise Exception("❌ 件数が取得できませんでした。HTML構造の確認が必要です。")

if __name__ == "__main__":
    count = get_monitor_count()
    print(f"現在のモニター数: {count}件")