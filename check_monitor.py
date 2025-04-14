import requests
from bs4 import BeautifulSoup
import os

URL = "https://www.fancrew.jp/search/result/4"
LAST_FILE = "last_items.txt"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def fetch_titles():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select(".monitorListItem")
    titles = []

    for item in items:
        title_tag = item.select_one(".monitorListItem__title")
        if title_tag and "画像投稿モニター" in title_tag.text:
            title = title_tag.text.strip()
            titles.append(title)

    return sorted(titles)

def load_last_titles():
    if not os.path.exists(LAST_FILE):
        return []
    with open(LAST_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def save_titles(titles):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        for title in titles:
            f.write(f"{title}\n")

def notify_slack(changes, added=True):
    if not changes:
        return

    change_type = "追加" if added else "削除"
    message = f"*【{change_type}された画像投稿モニター】*\n" + "\n".join(f"- {title}" for title in changes)

    payload = {"text": message}

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code != 200:
        print(f"[ERROR] Slack通知失敗: {response.status_code} {response.text}")
    else:
        print("[INFO] Slack通知成功")

def main():
    current_titles = fetch_titles()
    last_titles = load_last_titles()

    added = list(set(current_titles) - set(last_titles))
    removed = list(set(last_titles) - set(current_titles))

    notify_slack(added, added=True)
    notify_slack(removed, added=False)

    save_titles(current_titles)

if __name__ == "__main__":
    main()
