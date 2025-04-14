import requests
from bs4 import BeautifulSoup
import hashlib
import os
import json

# 通知設定（Slack Webhook URL）
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# 監視対象URL
URL = "https://www.fancrew.jp/search/result/4"

# User-Agent ヘッダー
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# 保存用ファイル
DATA_FILE = "last_items.json"


def get_monitor_items():
    print("HTMLを取得中...")
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    monitor_items = []

    # 「画像投稿モニター」のコンテンツのみ抽出
    for item in soup.select(".monitorListItem"):
        badge = item.select_one(".monitorListItem__badge")
        if badge and "画像投稿モニター" in badge.text:
            title_elem = item.select_one(".monitorListItem__name")
            if title_elem:
                title = title_elem.text.strip()
                link = item.select_one("a")
                href = link["href"] if link else ""
                monitor_items.append({
                    "title": title,
                    "link": href
                })

    print(f"取得したモニター件数: {len(monitor_items)}")
    return monitor_items


def load_previous_items():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_current_items(items):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def send_slack_notification(added, removed):
    if not SLACK_WEBHOOK_URL:
        print("SlackのWebhook URLが設定されていません。")
        return

    message = ""
    if added:
        message += f"【追加されたモニター】\n"
        for item in added:
            message += f"- {item['title']}: https://www.fancrew.jp{item['link']}\n"
    if removed:
        message += f"\n【削除されたモニター】\n"
        for item in removed:
            message += f"- {item['title']}: https://www.fancrew.jp{item['link']}\n"

    if message:
        response = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
        print(f"Slack通知のレスポンス: {response.status_code}")


def main():
    current_items = get_monitor_items()
    previous_items = load_previous_items()

    current_set = {json.dumps(i, ensure_ascii=False) for i in current_items}
    previous_set = {json.dumps(i, ensure_ascii=False) for i in previous_items}

    added_items = [json.loads(i) for i in current_set - previous_set]
    removed_items = [json.loads(i) for i in previous_set - current_set]

    if added_items or removed_items:
        send_slack_notification(added_items, removed_items)
        save_current_items(current_items)
    else:
        print("変更はありません。")


if __name__ == "__main__":
    main()