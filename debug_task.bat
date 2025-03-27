@echo off
cd /d C:\Users\owner\weather-calendar
echo 実行開始：%DATE% %TIME% >> debug_log.txt
"C:\Users\owner\AppData\Local\Programs\Python\Python313\python.exe" weather_converter.py >> debug_log.txt 2>&1
echo 終了：%DATE% %TIME% >> debug_log.txt
echo. >> debug_log.txt