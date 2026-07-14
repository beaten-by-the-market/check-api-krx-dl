@echo off
REM Daily ingest wrapper for Windows Task Scheduler (21:00 KST, after the 20:00 NXT close).
REM
REM THIS FILE MUST BE SAVED WITH CRLF LINE ENDINGS.
REM cmd.exe walks a batch file by byte offset assuming CRLF. With LF-only endings it resumes
REM mid-line and executes fragments as commands ("'1000000000' is not recognized..."), which is
REM exactly how the 2026-07-14 21:00 run died with exit 255. .gitattributes pins *.bat to CRLF.
REM
REM Keep this file ASCII-only and logic-free: cmd also eats '%' as variable references and
REM misreads UTF-8 comments as CP949. All logic (incl. the log file) lives in nxt_krx_ingest.py.
REM
REM --budget 1000000000 = the full daily API quota. Nobody else uses the key after 21:00, so we
REM run until KOSCOM refuses; the script catches that as a clean, resumable stop. Manual daytime
REM runs use the 900MB default instead, leaving headroom for ad-hoc queries.
REM
REM Run now:    schtasks /run    /tn "NXT-KRX daily ingest"
REM Unregister: schtasks /delete /tn "NXT-KRX daily ingest" /f
REM Log:        data\logs\ingest_YYYYMMDD.log

"C:\Users\Peter\AppData\Local\Programs\Python\Python313\python.exe" "c:\Users\Peter\github\check-api-krx-dl\.claude\skills\checkapi-data\scripts\nxt_krx_ingest.py" --daily --budget 1000000000 --log "c:\Users\Peter\github\check-api-krx-dl\data\logs"