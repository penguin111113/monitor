from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import os
import time
import requests
from datetime import datetime

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # 環境変数に設定

def fetch_projects():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get("https://www.tentame.net/project/")
    time.sleep(5)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".project_list .item")

    print(f"✅ Selenium 取得件数: {len(items)}")

    projects = []
    for item in items:
        title_tag = item.select_one(".title")
        img_tag = item.select_one("img")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        image_url = img_tag["src"] if img_tag else None

        projects.append({
            "title": title,
            "image": image_url
        })

    return projects

def load_last_projects():
    if os.path.exists("last_projects.json"):
        with open("last_projects.json", "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("⚠️ JSONが壊れています。初期化します。")
                return []
    return []

def save_last_projects(projects):
    with open("last_projects.json", "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def send_to_slack(projects):
    for p in projects:
        payload = {
            "attachments": [
                {
                    "fallback": p["title"],
                    "color": "#36a64f",
                    "title": p["title"],
                    "image_url": p["image"],
                    "footer": f"tentame.net | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        }
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code != 200:
            print(f"❌ Slack通知失敗: {response.text}")
        else:
            print(f"📤 Slack通知: {p['title']}")

def main():
    print("🔍 Selenium による新着案件チェック...")
    current_projects = fetch_projects()
    print(f"✅ 現在の案件数: {len(current_projects)}")

    last_projects = load_last_projects()
    last_titles = {p["title"] for p in last_projects}
    new_projects = []

    today = datetime.now().strftime("%Y-%m-%d")
    for p in current_projects:
        if p["title"] not in last_titles:
            p["date"] = today
            new_projects.append(p)

    print(f"🆕 新着: {len(new_projects)} 件")

    if new_projects:
        send_to_slack(new_projects)
    else:
        print("ℹ️ 新着はありませんでした。")

    save_last_projects(current_projects)

if __name__ == "__main__":
    main()
