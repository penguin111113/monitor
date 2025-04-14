import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.fancrew.jp/search/result/4"

def get_monitor_count():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 件数の書かれた文字列例：『（1 - 20件 / 352件）』
    count_text = soup.select_one(".pager span").text
    match = re.search(r"/\s*([0-9,]+)件", count_text)
    if match:
        count = int(match.group(1).replace(",", ""))
        return count
    else:
        raise Exception("❌ 件数を正しく取得できませんでした。HTML構造が変わった可能性があります。")

if __name__ == "__main__":
    count = get_monitor_count()
    print(f"現在のモニター数: {count}件")
