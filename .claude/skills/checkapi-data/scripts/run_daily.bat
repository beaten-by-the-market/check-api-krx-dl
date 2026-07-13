@echo off
REM Daily ingest wrapper for Windows Task Scheduler.
REM Keep this file ASCII-only and logic-free: cmd.exe eats '%' as variable refs and
REM misreads UTF-8 comments as CP949, which silently breaks batch files.
REM All logic (incl. the log file) lives in nxt_krx_ingest.py --daily --log.
REM
REM Register (runs 21:00 KST daily, after the 20:00 NXT close):
REM   see references/nxt-analysis.md
REM Run now:      schtasks /run    /tn "NXT-KRX daily ingest"
REM Unregister:   schtasks /delete /tn "NXT-KRX daily ingest" /f
REM Log:          data\logs\ingest_YYYYMMDD.log

"C:\Users\Peter\AppData\Local\Programs\Python\Python313\python.exe" "c:\Users\Peter\github\check-api-krx-dl\.claude\skills\checkapi-data\scripts\nxt_krx_ingest.py" --daily --log "c:\Users\Peter\github\check-api-krx-dl\data\logs"