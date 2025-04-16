import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# 通知用 Slack Webhook
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

TENTAME_URL = "https://www.tentame.net/project/"
LAST_PROJECTS_FILE = "last_projects.json"


def send_slack_notification(message, image_url=None):
    payload = {
        "attachments": [
            {
                "fallback": message,
                "color": "#36a64f",
                "text": message,
            }
        ]
    }
    if image_url:
        payload["attachments"][0]["image_url"] = image_url

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    response.raise_for_status()


def fetch_projects():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(TENTAME_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    projects = []
    for item in soup.select(".list_block"):
        title_tag = item.select_one(".list_title")
        if not title_tag:
            continue
        title = title_tag.text.strip()
        image_tag = item.select_one("img")
        image_url = image_tag["src"] if image_tag else None

        projects.append({
            "title": title,
            "image": image_url
        })

    return projects


def load_last_projects():
    if not os.path.exists(LAST_PROJECTS_FILE):
        return []
    with open(LAST_PROJECTS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_projects(projects):
    with open(LAST_PROJECTS_FILE, "w") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)


def main():
    print("🔍 新着案件を確認中...")
    current_projects = fetch_projects()
    print(f"✅ 現在の案件数: {len(current_projects)}")

    last_projects = load_last_projects()
    last_titles = {p["title"] for p in last_projects}
    new_projects = [p for p in current_projects if p["title"] not in last_titles]

    print(f"🆕 新着: {len(new_projects)} 件")
    if new_projects:
        for project in new_projects:
            today = datetime.now().strftime("%Y-%m-%d")
            message = f"🆕 新着案件: {project['title']} ({today})"
            send_slack_notification(message, project.get("image"))
    else:
        print("ℹ️ 新着はありませんでした。")

    save_projects(current_projects)


if __name__ == "__main__":
    main()
