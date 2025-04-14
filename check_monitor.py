import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.fancrew.jp/search/result/4"

def get_monitor_count():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 「通販のモニター（1 - 20件 / 352件）」のテキストを取得
    heading = soup.find("div", class_="monitorResultWrap")
    if heading:
        match = re.search(r"/\s*([0-9,]+)件", heading.text)
        if match:
            return int(match.group(1).replace(",", ""))

    raise Exception("❌ 件数が取得できませんでした。HTML構造の確認が必要です。")

if __name__ == "__main__":
    count = get_monitor_count()
    print(f"現在のモニター数: {count}件")
