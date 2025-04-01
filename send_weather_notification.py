import os
import requests
from datetime import datetime, timedelta

# === Webhook URL を環境変数から取得（GitHub Secrets対応）===
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# === .icsファイルのパス ===
ICS_FILE_PATH = "fukushima_all_day.ics"

# ✅ 明日の天気を.icsファイルから抽出
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

# ✅ LINE WORKSのWebhookに送信（body.text形式で）
def send_to_lineworks(message):
    if not WEBHOOK_URL:
        print("[エラー] WEBHOOK_URLが設定されていません（GitHub Secretsを確認）")
        return
    if message is None:
        print("[送信スキップ] メッセージがNoneでした")
        return

    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "body": {
            "text": message
        }
    }

    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    print("通知結果:", response.status_code, response.text)

# ✅ 実行メイン
def main():
    print("カレントディレクトリ:", os.getcwd())
    print("ファイル一覧:", os.listdir())
    message = get_tomorrow_summary_from_ics(ICS_FILE_PATH)
    print("送信メッセージ:", message)
    send_to_lineworks(message)

if __name__ == "__main__":
    main()
