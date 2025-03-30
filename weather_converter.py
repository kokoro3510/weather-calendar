import os
import requests
import subprocess
import chardet
import datetime

# GitHub Actions用ディレクトリ
REPO_DIR = os.getcwd()
ICS_FILENAME = "fukushima_all_day.ics"
ICS_PATH = os.path.join(REPO_DIR, ICS_FILENAME)

# 週間天気予報の元データURL
SOURCE_URL = "https://weather.masuipeo.com/fukushima.ics"

def detect_encoding(byte_data):
    result = chardet.detect(byte_data)
    print(f"📌 推定文字コード: {result['encoding']}")
    return result['encoding'] if result['encoding'] else 'utf-8'

def convert_to_all_day_ics(data):
    weather_icons = {
        "晴": "☀",
        "曇": "☁",
        "くもり": "☁",
        "雨": "☔",
        "雪": "❄",
        "雷": "⚡",
        "霧": "🌫",
    }

    lines = data.splitlines()
    new_lines = []

    for line in lines:
        if line.startswith("DTSTART:"):
            date = line[8:16]
            new_lines.append(f"DTSTART;VALUE=DATE:{date}")
        elif line.startswith("DTEND:"):
            date = line[6:14]
            new_lines.append(f"DTEND;VALUE=DATE:{date}")
        elif line.startswith("SUMMARY:"):
            summary = line[8:]
            icon = ""
            for key, emoji in weather_icons.items():
                if key in summary:
                    icon = emoji
                    break
            new_summary = f"{icon} {summary}"
            print(f"🔍 SUMMARY変換: {new_summary}")
            new_lines.append(f"SUMMARY:{new_summary}")
        else:
            new_lines.append(line)

    # ✅ タイムスタンプ追加で差分確保
    timestamp = datetime.datetime.now().isoformat()
    new_lines.append(f"X-GENERATED:{timestamp}")

    return "\n".join(new_lines)

def update_ics_file():
    response = requests.get(SOURCE_URL)
    if response.status_code == 200:
        byte_data = response.content
        encoding = detect_encoding(byte_data)
        text = byte_data.decode(encoding)

        converted = convert_to_all_day_ics(text)
        with open(ICS_PATH, "w", encoding="utf-8-sig") as f:
            f.write(converted)

        print("✅ .ics ファイルを更新しました")
    else:
        print("❌ 天気データ取得に失敗")

def git_push():
    try:
        subprocess.run(["git", "add", ICS_FILENAME], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "🌤 文字コード自動判定＋絵文字＋タイムスタンプ付き"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        print("✅ GitHubへ自動push完了")
    except subprocess.CalledProcessError:
        print("⚠ Git push に失敗しました（コミットなし or 既に最新）")

if __name__ == "__main__":
    update_ics_file()
    git_push()
