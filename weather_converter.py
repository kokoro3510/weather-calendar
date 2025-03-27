import requests
import subprocess
import os

# Gitリポジトリのディレクトリ（あなたの環境に合わせて！）
REPO_DIR = "C:/Users/owner/weather-calendar"

# .icsファイルの名前
ICS_FILENAME = "fukushima_all_day.ics"
ICS_PATH = os.path.join(REPO_DIR, ICS_FILENAME)

# 天気予報元URL
SOURCE_URL = "https://weather.masuipeo.com/fukushima.ics"

def convert_to_all_day_ics(data):
    lines = data.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("DTSTART:"):
            date = line[8:16]
            new_lines.append(f"DTSTART;VALUE=DATE:{date}")
        elif line.startswith("DTEND:"):
            date = line[6:14]
            new_lines.append(f"DTEND;VALUE=DATE:{date}")
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

def update_ics_file():
    response = requests.get(SOURCE_URL)
    if response.status_code == 200:
        converted = convert_to_all_day_ics(response.text)
        with open(ICS_PATH, "w", encoding="utf-8") as f:
            f.write(converted)
        print("✅ .ics ファイルを更新しました")
    else:
        print("❌ 天気データ取得に失敗")

def git_push():
    try:
        subprocess.run(["git", "add", ICS_FILENAME], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "⛅ 天気を自動更新"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push"], cwd=REPO_DIR, check=True)
        print("✅ GitHubへ自動push完了")
    except subprocess.CalledProcessError:
        print("⚠ Git push に失敗しました（コミットなし or 設定ミス？）")

if __name__ == "__main__":
    update_ics_file()
    git_push()