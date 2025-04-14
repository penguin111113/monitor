import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.fancrew.jp/search/result/4"

def get_monitor_count():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 件数が書かれている部分の全テキストを対象に検索
    match = re.search(r"\(\d+\s*-\s*\d+件\s*/\s*([\d,]+)件\)", soup.text)
    if match:
        return int(match.group(1).replace(",", ""))

    raise Exception("❌ 件数が取得できませんでした。HTML構造の確認が必要です。")

if __name__ == "__main__":
    count = get_monitor_count()
    print(f"現在のモニター数: {count}件")
