import requests
from bs4 import BeautifulSoup
import json
import os
from slack_sdk.webhook import WebhookClient
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
POINTI_URL = "https://pointi.jp/list.php?mode=1"
PREVIOUS_FILE = "previous.json"


def fetch_current_items():
    res = requests.get(POINTI_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    cards = soup.select(".contents_list .itemBox")
    
    items = []
    for card in cards:
        title = card.select_one(".itemTitle")
        point = card.select_one(".itemPoint")
        if title and point:
            items.append({
                "title": title.get_text(strip=True),
                "point": point.get_text(strip=True)
            })
    return items


def load_previous_items():
    if os.path.exists(PREVIOUS_FILE):
        with open(PREVIOUS_FILE, "r") as f:
            return json.load(f)
    return []


def save_current_items(items):
    with open(PREVIOUS_FILE, "w") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def notify_slack(new_items):
    if not new_items:
        return
    webhook = WebhookClient(WEBHOOK_URL)
    for item in new_items:
        text = f"🆕 新しい案件が追加されました！\n*{item['title']}*（{item['point']}）"
        webhook.send(text=text)


def main():
    current = fetch_current_items()
    previous = load_previous_items()
    previous_titles = {item['title'] for item in previous}
    
    new_items = [item for item in current if item['title'] not in previous_titles]
    
    if new_items:
        notify_slack(new_items)
        print(f"{len(new_items)} 件の新規案件を検出して通知しました。")
    else:
        print("新しい案件はありませんでした。")

    save_current_items(current)


if __name__ == "__main__":
    main()
