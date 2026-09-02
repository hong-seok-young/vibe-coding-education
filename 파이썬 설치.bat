@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
title 바이브 코딩 실습 - 환경 설치

rem 브라우저로 받은 파일에는 Windows가 "인터넷에서 받음" 표시(Mark of the Web)를
rem 자동으로 붙인다. 보안 정책이 엄격한 PC에서는 이 표시 때문에 파일 복사·실행이
rem 막힐 수 있어, 실행하자마자 스스로 그 표시를 지운다 (관리자 권한 불필요, 실패해도
rem 무시하고 계속 진행 — 지워지지 않았다면 뒤에서 다른 오류로 드러난다).
powershell -NoProfile -ExecutionPolicy Bypass -Command "Unblock-File -LiteralPath '%~f0'" >nul 2>&1

cd /d "%~dp0"

echo.
echo  ============================================================
echo    바이브 코딩 실습 - 환경 설치
echo  ============================================================
echo.
echo    이 실습은 파이썬만 미리 깔아두고, 나머지 코드는 여러분이 AI와
echo    함께 하나하나 만들어 갑니다. 그래서 이 설치 파일은 파이썬만 준비합니다.
echo    이미 깔려 있으면 최신 버전인지도 같이 확인합니다.
echo    1~2분 걸립니다. 끝날 때까지 이 창을 닫지 마세요.
echo.

rem ============================================================
rem  1단계 - 파이썬이 이미 있는지 확인
rem ============================================================
echo  [1/2] 파이썬이 이미 있는지 확인합니다...
call :find_python
if defined PY (
    for /f "tokens=*" %%V in ('%PY% --version 2^>^&1') do (
        echo        이미 있습니다 - %%V
        set "PY_BEFORE=%%V"
    )
) else (
    echo        없습니다.
    set "PY_BEFORE="
)
echo.

where winget >nul 2>&1
if errorlevel 1 (
    if defined PY (
        echo        winget 이 없어 최신 버전인지는 확인하지 못합니다. 있는 그대로 사용합니다.
        goto :prep_env
    )
    echo        winget 도 없어서 직접 받는 방법으로 넘어갑니다.
    goto :manual_download
)

rem ============================================================
rem  1단계 계속 - winget 으로 최신 버전 확인 (이미 있어도 실행)
rem ============================================================
echo  [1/2] winget 으로 최신 버전인지 확인합니다 (몇 초 걸립니다)...
winget upgrade --id Python.Python.3.14 -e --accept-package-agreements --accept-source-agreements --include-unknown >nul 2>&1
winget upgrade --id Python.Python.3.13 -e --accept-package-agreements --accept-source-agreements --include-unknown >nul 2>&1

call :find_python
if defined PY (
    for /f "tokens=*" %%V in ('%PY% --version 2^>^&1') do (
        if "%PY_BEFORE%"=="%%V" (
            echo        이미 최신 버전입니다 - %%V
        ) else (
            echo        최신 버전으로 업데이트했습니다 - %%V
        )
    )
    goto :prep_env
)

echo        설치되어 있지 않아 새로 설치합니다 (python.org 공식 배포판)...
winget install --id Python.Python.3.14 -e --source winget --scope user --accept-package-agreements --accept-source-agreements
call :find_python
if defined PY goto :installed_ok

echo.
echo        3.14 설치가 안 됐습니다. 3.13 으로 다시 시도합니다...
winget install --id Python.Python.3.13 -e --source winget --scope user --accept-package-agreements --accept-source-agreements
call :find_python
if defined PY goto :installed_ok

goto :manual_download

rem ============================================================
rem  2단계 대안 - 브라우저로 직접 받기
rem ============================================================
:manual_download
echo.
echo  ------------------------------------------------------------
echo    자동 설치가 안 됩니다. 브라우저를 열어드릴게요.
echo.
echo      1) 노란색 [Download Python 3.x.x] 버튼 클릭
echo      2) 받아진 파일을 실행
echo      3) 첫 화면 맨 아래 [Add python.exe to PATH] 체크  ★★ 필수 ★★
echo         (이걸 빠뜨리면 나중에 실행이 안 됩니다)
echo      4) [Install Now] 클릭
echo      5) 설치가 끝나면 이 창으로 돌아오세요
echo  ------------------------------------------------------------
echo.
start "" "https://www.python.org/downloads/"
echo    설치를 마쳤으면 아무 키나 누르세요...
pause >nul
call :find_python
if defined PY goto :installed_ok

echo.
echo  [!] 아직 파이썬을 찾지 못했습니다.
echo      3^)번 [Add python.exe to PATH] 체크를 빠뜨렸을 가능성이 가장 큽니다.
echo      제어판에서 Python 을 제거한 뒤, 그 체크박스를 켜고 다시 설치해 보세요.
goto :fail

:installed_ok
for /f "tokens=*" %%V in ('%PY% --version 2^>^&1') do echo        설치 완료 - %%V

rem ============================================================
rem  2단계 - 설정 파일 준비 (라이브러리는 실습하면서 직접 pip install 한다)
rem ============================================================
:prep_env
echo.
echo  [2/2] 설정 파일(.env)을 준비합니다...
if exist "news-report-bot\.env" (
    echo        .env 가 이미 있습니다. 덮어쓰지 않고 그대로 둡니다.
) else (
    if exist "news-report-bot\.env.example" (
        copy "news-report-bot\.env.example" "news-report-bot\.env" >nul
        echo        news-report-bot\.env 를 만들었습니다.
    ) else (
        echo        .env.example 이 없어 건너뜁니다.
    )
)

rem ============================================================
rem  끝
rem ============================================================
echo.
echo  ============================================================
echo    설치 끝. 파이썬 준비 완료입니다.
echo  ============================================================
echo.
echo    다음에 할 일
echo      1) 열리는 메모장에 발급받은 키를 채우고 저장
echo      2) 실습 페이지의 안내대로 pip install 과 코드 작성을 직접 진행
echo.
if exist "news-report-bot\.env" start "" notepad "news-report-bot\.env"
echo    창을 닫으려면 아무 키나 누르세요...
pause >nul
exit /b 0

:fail
echo.
echo  ============================================================
echo    설치를 끝내지 못했습니다.
echo    이 창에 나온 내용을 통째로 캡처해서 강사에게 보여주세요.
echo  ============================================================
echo.
pause >nul
exit /b 1

rem ============================================================
rem  파이썬 찾기 - 결과를 PY 변수에 넣는다 (못 찾으면 비어 있음)
rem ============================================================
:find_python
set "PY="

rem (1) py 런처 - 파이썬을 공식 설치했으면 항상 있다
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PY=py -3"
    goto :eof
)

rem (2) PATH 의 python - 단, 마이크로소프트 스토어 껍데기는 제외
for /f "delims=" %%P in ('where python 2^>nul') do (
    echo %%P | find /i "WindowsApps" >nul
    if errorlevel 1 (
        if not defined PY set PY="%%P"
    )
)
if defined PY goto :eof

rem (3) 방금 설치한 경우 PATH 가 아직 갱신되지 않았을 수 있어 설치 경로를 직접 확인
for %%V in (316 315 314 313 312 311) do (
    if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
    if not defined PY if exist "C:\Program Files\Python%%V\python.exe" set PY="C:\Program Files\Python%%V\python.exe"
)
goto :eof
