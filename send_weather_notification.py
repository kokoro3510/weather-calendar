import os
import requests
from datetime import datetime, timedelta

# === Webhook URL ===
WEBHOOK_URL = "https://webhook.worksmobile.com/message/beb002e4-ab49-4146-aa76-408c56d4f4e6"
ICS_FILE_PATH = "fukushima_all_day.ics"

def get_tomorrow_summary_from_ics(file_path):
    try:
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("[エラー] .icsファイルが見つかりませんでした:", file_path)
        return None

    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
    summary = None
    inside_event = False
    date_found = False

    for line in lines:
        line = line.strip()
        if line.startswith("BEGIN:VEVENT"):
            inside_event = True
            summary = None
            date_found = False
        elif line.startswith("DTSTART;VALUE=DATE:") and inside_event:
            date = line.split(":")[1]
            if date == tomorrow:
                date_found = True
        elif line.startswith("SUMMARY:") and inside_event:
            summary = line[8:]
        elif line.startswith("END:VEVENT") and inside_event:
            if date_found and summary:
                return f"明日の天気は「{summary}」です！"
            inside_event = False

    return "明日の天気情報が見つかりませんでした"

def send_to_lineworks(message):
    if message is None:
        print("[送信スキップ] メッセージがNoneでした")
        return
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "body": {
            "text": message  # ← ここが超・最重要！！！
        }
    }
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    print("通知結果:", response.status_code, response.text)

def main():
    print("カレントディレクトリ:", os.getcwd())
    print("ファイル一覧:", os.listdir())
    message = get_tomorrow_summary_from_ics(ICS_FILE_PATH)
    print("送信メッセージ:", message)
    send_to_lineworks(message)

if __name__ == "__main__":
    main()