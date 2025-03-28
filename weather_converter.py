import os
import requests
import subprocess

# Gitリポジトリのディレクトリ（GitHub Actions用）
REPO_DIR = os.getcwd()

# .icsファイルの名前
ICS_FILENAME = "fukushima_all_day.ics"
ICS_PATH = os.path.join(REPO_DIR, ICS_FILENAME)

# 天気予報元URL（masuipeo 週間天気予報）
SOURCE_URL = "https://weather.masuipeo.com/fukushima.ics"

def convert_to_all_day_ics(data):
    weather_icons = {
        "晴": "☀",
        "曇": "☁",
        "くもり": "☁",  # 漢字でもひらがなでも対応！
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
            new_lines.append(f"SUMMARY:{new_summary}")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

def update_ics_file():
    response = requests.get(SOURCE_URL)
    if response.status_code == 200:
        converted = convert_to_all_day_ics(response.text)
        with open(ICS_PATH, "w", encoding="utf-8-sig") as f:
            f.write(converted)
        print("✅ .ics ファイルを更新しました")
    else:
        print("❌ 天気データ取得に失敗")

def git_push():
    try:
        subprocess.run(["git", "add", ICS_FILENAME], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "🌤 天気アイコン付きで自動更新"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        print("✅ GitHubへ自動push完了")
    except subprocess.CalledProcessError:
        print("⚠ Git push に失敗しました（コミットなし or 既に最新）")

if __name__ == "__main__":
    update_ics_file()
    git_push()