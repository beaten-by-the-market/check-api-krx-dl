@echo off
REM NXT 틱 + KRX/NXT 1분봉 일일 수집 (Windows 작업 스케줄러용)
REM
REM 등록 (관리자 권한 불필요, NXT 장 마감 20:00 이후인 21:00 실행):
REM   schtasks /create /tn "NXT-KRX daily ingest" /tr "\"c:\Users\Peter\github\check-api-krx-dl\.claude\skills\checkapi-data\scripts\run_daily.bat\"" /sc daily /st 21:00
REM 해제:
REM   schtasks /delete /tn "NXT-KRX daily ingest" /f
REM 즉시 실행:
REM   schtasks /run /tn "NXT-KRX daily ingest"
REM
REM 로그: data\logs\ingest_YYYYMMDD.log  (중단돼도 ingest_log 기준으로 다음날 이어서 진행)

setlocal
set PY=C:\Users\Peter\AppData\Local\Programs\Python\Python313\python.exe
set DIR=c:\Users\Peter\github\check-api-krx-dl\.claude\skills\checkapi-data\scripts
set LOGDIR=c:\Users\Peter\github\check-api-krx-dl\data\logs

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM YYYYMMDD (로캘 무관하게 WMIC 대신 python 으로 뽑는다)
for /f %%d in ('"%PY%" -c "import datetime;print(datetime.date.today().strftime('%%Y%%m%%d'))"') do set TODAY=%%d

cd /d "%DIR%"
echo ===== %DATE% %TIME% 시작 ===== >> "%LOGDIR%\ingest_%TODAY%.log"
"%PY%" nxt_krx_ingest.py --daily >> "%LOGDIR%\ingest_%TODAY%.log" 2>&1
echo ===== %DATE% %TIME% 종료 (exit %ERRORLEVEL%) ===== >> "%LOGDIR%\ingest_%TODAY%.log"
endlocal