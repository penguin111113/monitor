import requests
from bs4 import BeautifulSoup
import json
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
TARGET_URL = "https://www.tentame.net/project/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_projects():
    response = requests.get(TARGET_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    projects = []
    for item in soup.select(".project-box a.project-link"):
        title = item.select_one(".project-title").get_text(strip=True)
        link = "https://www.tentame.net" + item["href"]
        projects.append({"title": title, "link": link})

    return projects


def load_last_projects():
    if not os.path.exists("last_projects.json"):
        return []
    with open("last_projects.json", "r") as f:
        return json.load(f)


def save_projects(projects):
    with open("last_projects.json", "w") as f:
        json.dump(projects, f, indent=2)


def notify_slack(new_projects):
    if not new_projects:
        return

    message = "*🆕 新着案件が見つかりました！*\n"
    for project in new_projects:
        message += f"- <{project['link']}|{project['title']}>\n"

    requests.post(SLACK_WEBHOOK_URL, json={"text": message})


def main():
    print("🔍 新着案件を確認中...")
    current_projects = fetch_projects()
    last_projects = load_last_projects()

    last_titles = {p["title"] for p in last_projects}
    new_projects = [p for p in current_projects if p["title"] not in last_titles]

    if new_projects:
        print(f"✅ 新着 {len(new_projects)} 件！")
    else:
        print("ℹ️ 変化なし")

    notify_slack(new_projects)
    save_projects(current_projects)


if __name__ == "__main__":
    main()
