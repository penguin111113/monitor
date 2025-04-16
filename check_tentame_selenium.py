import os
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

URL = "https://www.tentame.net/project/"

def fetch_projects():
    print("🔍 Selenium による新着案件チェック...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(URL)
    time.sleep(3)  # JS読み込み待ち（必要に応じて調整）

    projects = []
    cards = driver.find_elements(By.CLASS_NAME, "project-box")

    for card in cards:
        try:
            title_elem = card.find_element(By.CLASS_NAME, "title")
            title = title_elem.text.strip()

            url = title_elem.get_attribute("href") or URL
            image = card.find_element(By.TAG_NAME, "img").get_attribute("src")
            date = card.find_element(By.CLASS_NAME, "project-box__date").text.strip()

            projects.append({
                "title": title,
                "url": url,
                "image": image,
                "date": date
            })
        except Exception as e:
            print(f"❌ パース失敗: {e}")
            continue

    driver.quit()
    return projects

def load_last_projects():
    if not os.path.exists("last_projects.json"):
        return []
    with open("last_projects.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_current_projects(projects):
    with open("last_projects.json", "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

def detect_new_projects(current, last):
    new = []
    for p in current:
        match = next((lp for lp in last if lp["title"] == p["title"]), None)
        if match is None or match["date"] != p["date"]:
            new.append(p)
    return new

def send_slack_notification(projects):
    if not projects:
        print("ℹ️ 新着はありませんでした。")
        return

    print(f"🆕 新着: {len(projects)} 件")

    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("❌ Slack webhook URL が未設定です。")
        return

    for p in projects:
        message = {
            "attachments": [
                {
                    "fallback": p["title"],
                    "color": "#36a64f",
                    "title": p["title"],
                    "title_link": p["url"],
                    "text": f"🗓 表示日: {p['date']}",
                    "image_url": p["image"]
                }
            ]
        }
        response = requests.post(webhook_url, json=message)
        if response.status_code != 200:
            print(f"❌ Slack通知失敗: {response.status_code} - {response.text}")

def main():
    current_projects = fetch_projects()
    print(f"✅ 現在の案件数: {len(current_projects)}")

    last_projects = load_last_projects()
    new_projects = detect_new_projects(current_projects, last_projects)

    send_slack_notification(new_projects)
    save_current_projects(current_projects)

if __name__ == "__main__":
    main()
