import json
import time
import os
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
LAST_PROJECTS_FILE = "last_projects.json"

def fetch_projects():
    print("🔍 Selenium による新着案件チェック...")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    driver.get("https://www.tentame.net/project/")
    time.sleep(5)  # JavaScriptでの描画を待機（必要に応じて調整）

    projects = []
    elements = driver.find_elements(By.CSS_SELECTOR, ".project-list .project-item")

    for elem in elements:
        try:
            title = elem.find_element(By.CSS_SELECTOR, ".project-title").text.strip()
            image = elem.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
            link = elem.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            projects.append({
                "title": title,
                "image": image,
                "link": link,
                "date": datetime.now().strftime("%Y-%m-%d")
            })
        except Exception as e:
            print(f"⚠️ データ取得中にエラー: {e}")

    driver.quit()
    return projects

def load_last_projects():
    if not os.path.exists(LAST_PROJECTS_FILE):
        return []
    with open(LAST_PROJECTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_last_projects(projects):
    with open(LAST_PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def send_slack_notification(new_projects):
    for p in new_projects:
        message = {
            "attachments": [
                {
                    "fallback": p["title"],
                    "title": p["title"],
                    "title_link": p["link"],
                    "image_url": p["image"],
                    "footer": f"掲載日: {p['date']}"
                }
            ]
        }
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        if response.status_code != 200:
            print(f"❌ Slack通知失敗: {response.status_code}, {response.text}")
        else:
            print(f"📢 通知: {p['title']}")

def main():
    current_projects = fetch_projects()
    print(f"✅ 現在の案件数: {len(current_projects)}")

    last_projects = load_last_projects()
    last_titles = {p["title"] for p in last_projects}

    new_projects = [
        p for p in current_projects
        if p["title"] not in last_titles or p["date"] != datetime.now().strftime("%Y-%m-%d")
    ]

    print(f"🆕 新着: {len(new_projects)} 件")

    if new_projects:
        send_slack_notification(new_projects)
        save_last_projects(current_projects)
    else:
        print("ℹ️ 新着はありませんでした。")

if __name__ == "__main__":
    main()
