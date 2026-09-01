@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
title 바이브 코딩 실습 - 환경 설치
cd /d "%~dp0"

echo.
echo  ============================================================
echo    바이브 코딩 실습 - 환경 설치
echo  ============================================================
echo.
echo    파이썬과 실습에 필요한 라이브러리를 한 번에 설치합니다.
echo    3~5분 걸립니다. 끝날 때까지 이 창을 닫지 마세요.
echo.

rem ============================================================
rem  1단계 - 파이썬이 이미 있는지 확인
rem ============================================================
echo  [1/4] 파이썬이 이미 있는지 확인합니다...
call :find_python
if defined PY (
    for /f "tokens=*" %%V in ('%PY% --version 2^>^&1') do echo        이미 있습니다 - %%V
    echo        설치를 건너뜁니다.
    goto :install_packages
)
echo        없습니다. 지금 설치합니다.
echo.

rem ============================================================
rem  2단계 - winget 으로 공식 배포판 설치
rem ============================================================
echo  [2/4] 파이썬을 내려받아 설치합니다 (python.org 공식 배포판)...
echo.
where winget >nul 2>&1
if errorlevel 1 (
    echo        이 PC에는 winget 이 없습니다. 직접 받는 방법으로 넘어갑니다.
    goto :manual_download
)

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
rem  3단계 - 실습 라이브러리 설치
rem ============================================================
:install_packages
echo.
echo  [3/4] 실습에 필요한 라이브러리를 설치합니다...
if not exist "news-report-bot\requirements.txt" (
    echo  [!] news-report-bot\requirements.txt 를 찾을 수 없습니다.
    echo      이 배치 파일이 저장소 폴더 안에 그대로 있어야 합니다.
    goto :fail
)
%PY% -m pip install --upgrade pip --quiet --disable-pip-version-check
%PY% -m pip install -r "news-report-bot\requirements.txt" --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo  [!] 라이브러리 설치에 실패했습니다.
    echo      회사 네트워크가 pypi.org 를 막고 있을 수 있습니다.
    echo      위에 빨간 글씨로 나온 에러 메시지를 그대로 복사해서 강사에게 보여주세요.
    goto :fail
)

%PY% -c "import anthropic, requests, feedparser, dotenv" >nul 2>&1
if errorlevel 1 (
    echo  [!] 설치는 됐는데 불러오기가 안 됩니다. 강사에게 문의하세요.
    goto :fail
)
echo        라이브러리 4개 확인 완료.

%PY% -c "import win32com.client" >nul 2>&1
if errorlevel 1 (
    echo  [!] 메일 발송용 pywin32 가 확인되지 않습니다. 아웃룩 발송이 안 될 수 있습니다.
    echo      pip install pywin32 로 직접 설치해 보세요.
) else (
    echo        아웃룩 연동(pywin32) 확인 완료.
)

rem ============================================================
rem  4단계 - 설정 파일 준비
rem ============================================================
echo.
echo  [4/4] 설정 파일(.env)을 준비합니다...
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
echo    설치 끝. 준비 완료입니다.
echo  ============================================================
echo.
echo    다음에 할 일
echo      1) 열리는 메모장에 발급받은 키 4종을 채우고 저장
echo      2) 이 폴더에서 실행:  py -3 news-report-bot\main.py --dry-run
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
