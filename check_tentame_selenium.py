import json
import os
import time
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
TARGET_URL = "https://www.tentame.net/project/"
LAST_PROJECTS_FILE = "last_projects.json"

def fetch_projects():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    print("🔍 ページ読み込み中...")
    driver.get(TARGET_URL)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    projects = []
    for item in soup.select(".project-item"):
        name_tag = item.select_one(".project-name")
        point_tag = item.select_one(".project-pt")
        date_tag = item.select_one(".date")
        if name_tag and point_tag and date_tag:
            name = name_tag.text.strip()
            point = point_tag.text.strip()
            date = date_tag.text.strip()
            projects.append({
                "name": name,
                "point": point,
                "date": date
            })
    return projects

def load_last_projects():
    if not os.path.exists(LAST_PROJECTS_FILE):
        return []
    with open(LAST_PROJECTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ JSON読み込みに失敗しました。空のリストを返します。")
            return []

def save_current_projects(projects):
    with open(LAST_PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def notify_new_projects(new_projects):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ Slack Webhook URL が設定されていません")
        return
    for p in new_projects:
        message = f"🆕 新着案件！\n*{p['name']}*\n{p['point']}\n📅 {p['date']}"
        payload = {"text": message}
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code != 200:
            print(f"❌ Slack通知に失敗しました: {response.status_code} {response.text}")

def main():
    print("🔍 Selenium による新着案件チェック...")
    current_projects = fetch_projects()
    print(f"✅ 現在の案件数: {len(current_projects)}")

    last_projects = load_last_projects()
    last_names_dates = {(p['name'], p['date']) for p in last_projects}
    new_projects = [p for p in current_projects if (p['name'], p['date']) not in last_names_dates]

    print(f"🆕 新着: {len(new_projects)} 件")
    if new_projects:
        notify_new_projects(new_projects)
        save_current_projects(current_projects)
    else:
        print("ℹ️ 新着はありませんでした。")

if __name__ == "__main__":
    main()
