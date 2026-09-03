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
echo.
echo    설치하는 버전은 3.12 입니다. 최신 버전(3.13 이상)을 쓰면 회사
echo    네트워크에서 인터넷 자료를 못 받아오는 문제가 있어서 일부러 3.12 로
echo    맞춥니다. 이미 3.13 이상이 깔려 있어도 3.12 를 따로 깔아드립니다.
echo    1~2분 걸립니다. 끝날 때까지 이 창을 닫지 마세요.
echo.

rem ============================================================
rem  1단계 - 파이썬이 이미 있는지 확인
rem ============================================================
echo  [1/1] 파이썬 3.12 가 이미 있는지 확인합니다...
call :find_python312
if defined PY (
    for /f "tokens=*" %%V in ('%PY% --version 2^>^&1') do echo        이미 있습니다 - %%V
    goto :installed_ok
)
echo        3.12 는 없습니다.

rem 다른 버전이 깔려 있으면 알려준다 (지우지는 않는다 - 3.12 를 나란히 깔면 된다)
call :find_any_python
if defined ANYPY (
    for /f "tokens=*" %%V in ('%ANYPY% --version 2^>^&1') do (
        echo        참고: 다른 버전이 깔려 있습니다 - %%V
    )
    echo        지우지 않아도 됩니다. 3.12 를 나란히 설치하고, 실습에서는 3.12 를 씁니다.
)
echo.

where winget >nul 2>&1
if errorlevel 1 (
    echo        winget 이 없어서 직접 받는 방법으로 넘어갑니다.
    goto :manual_download
)

echo        winget 으로 파이썬 3.12 를 설치합니다 (python.org 공식 배포판)...
winget install --id Python.Python.3.12 -e --source winget --scope user --accept-package-agreements --accept-source-agreements
call :find_python312
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
echo      1) 다운로드가 시작됩니다 (python-3.12.10-amd64.exe)
echo      2) 받아진 파일을 실행
echo      3) 첫 화면 맨 아래 [Add python.exe to PATH] 체크  ★★ 필수 ★★
echo         (이걸 빠뜨리면 나중에 실행이 안 됩니다)
echo      4) [Install Now] 클릭
echo      5) 설치가 끝나면 이 창으로 돌아오세요
echo  ------------------------------------------------------------
echo.
start "" "https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe"
echo    설치를 마쳤으면 아무 키나 누르세요...
pause >nul
call :find_python312
if defined PY goto :installed_ok

echo.
echo  [!] 아직 파이썬 3.12 를 찾지 못했습니다.
echo      3^)번 [Add python.exe to PATH] 체크를 빠뜨렸을 가능성이 가장 큽니다.
echo      제어판에서 Python 을 제거한 뒤, 그 체크박스를 켜고 다시 설치해 보세요.
goto :fail

:installed_ok
for /f "tokens=*" %%V in ('%PY% --version 2^>^&1') do echo        설치 완료 - %%V

rem ============================================================
rem  끝
rem ============================================================
echo.
echo  ============================================================
echo    설치 끝. 파이썬 준비 완료입니다.
echo  ============================================================
echo.
echo    실습에서 프로그램을 실행할 때는 python 이 아니라
echo    py -3.12 로 실행하세요. 그래야 3.12 로 돌아갑니다.
echo.
echo    다음에 할 일
echo      1) DART 인증키를 발급받아 메모장에 붙여두기
echo      2) 실습 페이지의 안내대로 pip install 과 코드 작성을 직접 진행
echo.
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
rem  파이썬 3.12 찾기 - 결과를 PY 변수에 넣는다 (못 찾으면 비어 있음)
rem
rem  최신 버전이 아니라 3.12 를 콕 집어 찾는다. 3.13 이상은 사내망에서
rem  인터넷 자료를 못 받아오는 문제가 있어 실습에 쓸 수 없다.
rem ============================================================
:find_python312
set "PY="

rem (1) py 런처로 3.12 를 지정해서 확인 - 공식 설치판이면 항상 있다
py -3.12 --version >nul 2>&1
if not errorlevel 1 (
    set "PY=py -3.12"
    goto :eof
)

rem (2) 설치 경로를 직접 확인 (방금 설치해서 PATH 가 아직 갱신되지 않은 경우)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PY="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :eof
)
if exist "C:\Program Files\Python312\python.exe" (
    set PY="C:\Program Files\Python312\python.exe"
    goto :eof
)
goto :eof

rem ============================================================
rem  버전 상관없이 파이썬이 있는지 - 안내용으로만 쓴다
rem ============================================================
:find_any_python
set "ANYPY="
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "ANYPY=py -3"
    goto :eof
)
for /f "delims=" %%P in ('where python 2^>nul') do (
    echo %%P | find /i "WindowsApps" >nul
    if errorlevel 1 (
        if not defined ANYPY set ANYPY="%%P"
    )
)
goto :eof
