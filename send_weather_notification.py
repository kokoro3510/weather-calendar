import os
import requests
from datetime import datetime, timedelta

# === Webhook URL（GitHub Secretsから）===
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ICS_FILE_PATH = "fukushima_all_day.ics"

# ✅ 指定した日付（今日 or 明日）の天気を抽出
def get_weather_summary_from_ics(file_path, days_ahead=1):
    try:
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("[エラー] .icsファイルが見つかりませんでした:", file_path)
        return None

    target_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y%m%d')
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
            if date == target_date:
                date_found = True
        elif line.startswith("SUMMARY:") and inside_event:
            summary = line[8:]
        elif line.startswith("END:VEVENT") and inside_event:
            if date_found and summary:
                label = "明日" if days_ahead == 1 else "今日"
                return f"{label}の天気は「{summary}」です！"
            inside_event = False

    return f"{'明日' if days_ahead == 1 else '今日'}の天気情報が見つかりませんでした"

# ✅ LINE WORKS Webhook に送信
def send_to_lineworks(message):
    if not WEBHOOK_URL:
        print("[エラー] WEBHOOK_URL が設定されていません")
        return
    if message is None:
        print("[送信スキップ] メッセージが None でした")
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

    # 🔥 明日の天気を通知！
    message = get_weather_summary_from_ics(ICS_FILE_PATH, days_ahead=1)
    print("送信メッセージ:", message)
    send_to_lineworks(message)

if __name__ == "__main__":
    main()
