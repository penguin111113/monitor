import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

TENTAME_URL = "https://www.tentame.net/project/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def fetch_projects():
    response = requests.get(TENTAME_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    project_items = soup.select(".project_list li a")

    projects = []
    for item in project_items:
        url = "https://www.tentame.net" + item.get("href")
        title = item.select_one(".project_name").text.strip()
        image_tag = item.select_one("img")
        image_url = "https://www.tentame.net" + image_tag.get("src") if image_tag else None
        projects.append({
            "title": title,
            "url": url,
            "image": image_url
        })
    return projects

def load_last_projects():
    if not os.path.exists("last_projects.json"):
        return []
    with open("last_projects.json", "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_projects(projects):
    with open("last_projects.json", "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def notify_slack(new_projects):
    for proj in new_projects:
        payload = {
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*🆕 新着案件:*\n*{proj['title']}*\n<{proj['url']}|案件を見る>"}},
            ]
        }
        if proj["image"]:
            payload["blocks"].append({
                "type": "image",
                "image_url": proj["image"],
                "alt_text": proj["title"]
            })

        requests.post(SLACK_WEBHOOK_URL, json=payload)

def main():
    print("🔍 新着案件を確認中...")
    current_projects = fetch_projects()
    last_projects = load_last_projects()

    last_titles = {proj["title"] for proj in last_projects}
    new_projects = [proj for proj in current_projects if proj["title"] not in last_titles]

    print(f"✅ 現在の案件数: {len(current_projects)}")
    print(f"🆕 新着: {len(new_projects)} 件")

    if new_projects:
        notify_slack(new_projects)
        save_projects(current_projects)
        print("📢 Slack に通知しました。")
    else:
        print("ℹ️ 新着はありませんでした。")

if __name__ == "__main__":
    main()
