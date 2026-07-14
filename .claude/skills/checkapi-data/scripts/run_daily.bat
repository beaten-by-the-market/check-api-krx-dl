@echo off
REM Daily ingest wrapper for Windows Task Scheduler (21:00 KST, after the 20:00 NXT close).
REM Keep this file ASCII-only and logic-free: cmd.exe eats '%' as variable refs and
REM misreads UTF-8 comments as CP949, which silently breaks batch files.
REM All logic (incl. the log file) lives in nxt_krx_ingest.py --daily --log.
REM
REM --budget 1000000000 = the full daily API quota. Nobody else uses the key after 21:00,
REM so we run until KOSCOM itself refuses ("일 최대 사용량 ... 초과"), which the script
REM catches and turns into a clean, resumable stop. Manual daytime runs use the 900MB
REM default instead, leaving headroom for ad-hoc queries.
REM
REM Run now:      schtasks /run    /tn "NXT-KRX daily ingest"
REM Unregister:   schtasks /delete /tn "NXT-KRX daily ingest" /f
REM Log:          data\logs\ingest_YYYYMMDD.log

"C:\Users\Peter\AppData\Local\Programs\Python\Python313\python.exe" "c:\Users\Peter\github\check-api-krx-dl\.claude\skills\checkapi-data\scripts\nxt_krx_ingest.py" --daily --budget 1000000000 --log "c:\Users\Peter\github\check-api-krx-dl\data\logs"