import requests
from bs4 import BeautifulSoup

URL = "https://www.fancrew.jp/search/result/4"

def get_monitor_count():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.select('.monitorListItem')
    return len(items)

if __name__ == "__main__":
    count = get_monitor_count()
    print(f"現在のモニター数: {count}件")
