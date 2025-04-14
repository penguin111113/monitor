import requests
from bs4 import BeautifulSoup
import json
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
URL = "https://www.fancrew.jp/search/result/4"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}
JSON_PATH = "last_items.json"

def get_monitor_items():
    response = requests.get(URL, headers=HEADERS)

    # デバッグ用: HTMLの先頭を出力
    print("=== HTML response preview ===")
    print(response.text[:1000])
    print("=== end preview ===")

    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    for item in soup.select(".monitorListItem"):
        if "画像投稿モニター" in item.text:
            title_tag = item.select_one(".monitorListTitle")
            if title_tag:
                title = title_tag.get_text(strip=True)
                items.append(title)
    return items

def load_last_items():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_items(items):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def send_slack_notification(text):
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL is not set.")
        return
    payload = {"text": text}
    try:
        requests.post(SLACK_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"Slack通知に失敗しました: {e}")

def main():
    current_items = get_monitor_items()
    last_items = load_last_items()

    new_items = [item for item in current_items if item not in last_items]
    removed_items = [item for item in last_items if item not in current_items]

    if new_items or removed_items:
        message = "【Fancrew画像投稿モニターの更新】\n"
        if new_items:
            message += "\n[追加されたモニター]\n" + "\n".join(new_items)
        if removed_items:
            message += "\n[削除されたモニター]\n" + "\n".join(removed_items)
        send_slack_notification(message)
    else:
        print("変化なし")

    save_items(current_items)

if __name__ == "__main__":
    main()