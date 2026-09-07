@echo off
chcp 65001 >nul 2>&1
title Vibe Coding - Setup

rem ============================================================
rem  Keep the window open so errors stay visible
rem
rem  When double-clicked, an error would close the window instantly and the
rem  user could not see what went wrong. So we call this file once more and
rem  hold the window when that inner run ends or fails.
rem  IMPORTANT: save this file as CRLF, ASCII-only outside echo/title.
rem  LF endings break goto labels; non-ASCII in rem lines breaks parsing.
rem ============================================================
if /i not "%~1"=="__run" (
    call "%~f0" __run
    echo.
    echo    창을 닫으려면 아무 키나 누르세요...
    pause >nul
    exit /b
)

rem Files downloaded via a browser get a Mark of the Web tag, which can block
rem execution on locked-down PCs. Clear it ourselves. No admin rights needed;
rem if it fails we ignore it and continue.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Unblock-File -LiteralPath '%~f0'" >nul 2>&1

cd /d "%~dp0"

echo.
echo  ============================================================
echo    바이브 코딩 실습 - 환경 준비
echo  ============================================================
echo.
echo    실습에 필요한 것을 한 번에 준비합니다 - 파이썬과 부품 3개.
echo    코드는 실습 때 여러분이 AI와 함께 만들어 갑니다.
echo.
echo    이미 깔려 있는 건 그대로 씁니다. 버전은 최신이어도 괜찮습니다.
echo    2~3분 걸립니다. 끝날 때까지 이 창을 닫지 마세요.
echo.

rem ============================================================
rem  Step 1 - Python
rem ============================================================
echo  [1/2] 파이썬을 확인합니다...
call :find_python

if defined PY (
    echo        이미 있습니다.
    goto :python_ready
)

echo        없습니다. 설치를 시작합니다.
echo.

where winget >nul 2>&1
if errorlevel 1 goto :manual_download

echo        python.org 공식 배포판을 받아 설치합니다...
winget install --id Python.Python.3.13 -e --source winget --scope user --accept-package-agreements --accept-source-agreements
call :find_python
if defined PY goto :python_ready

:manual_download
echo.
echo  ------------------------------------------------------------
echo    자동 설치가 안 됩니다. 브라우저를 열어드릴게요.
echo.
echo      1) 노란색 [Download Python 3.x.x] 버튼 클릭
echo      2) 받아진 파일을 실행
echo      3) 첫 화면 맨 아래 [Add python.exe to PATH] 체크  ** 필수 **
echo         (이걸 빠뜨리면 나중에 실행이 안 됩니다)
echo      4) [Install Now] 클릭
echo      5) 설치가 끝나면 이 창으로 돌아오세요
echo  ------------------------------------------------------------
echo.
start "" "https://www.python.org/downloads/"
echo    설치를 마쳤으면 아무 키나 누르세요...
pause >nul
call :find_python
if defined PY goto :python_ready

echo.
echo  [!] 아직 파이썬을 찾지 못했습니다.
echo      [Add python.exe to PATH] 체크를 빠뜨렸을 가능성이 가장 큽니다.
echo      제어판에서 Python 을 제거한 뒤, 그 체크박스를 켜고 다시 설치해 보세요.
echo.
echo      이 창의 내용을 통째로 캡처해서 강사에게 보여주세요.
exit /b 1

:python_ready
echo        확인:
%PY% --version
echo.

rem ============================================================
rem  Step 2 - the three libraries
rem
rem  Installing these during class costs time and stalls if the corporate
rem  network blocks pip. pywin32 is needed in the most failure-prone step.
rem
rem  We use %PY% -m pip so packages land in the exact interpreter we found.
rem  (This is what causes 'installed but missing' on multi-version PCs.)
rem ============================================================
echo  [2/2] 실습에 필요한 부품 3개를 받습니다 (1~2분)...
%PY% -m pip install requests feedparser pywin32
if not errorlevel 1 goto :libs_ready

echo.
echo        실패했습니다. 회사 보안 장비 때문일 수 있어
echo        신뢰할 곳을 지정해서 다시 시도합니다...
echo.
%PY% -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org requests feedparser pywin32
if not errorlevel 1 goto :libs_ready

echo.
echo  [!] 부품을 받지 못했습니다.
echo      파이썬은 준비됐으니 실습은 시작할 수 있지만, 실습 중에 다시 받아야 합니다.
echo      위에 나온 오류 내용을 캡처해서 강사에게 보여주세요.
exit /b 1

:libs_ready
echo.
echo        부품 3개 준비 완료 (requests, feedparser, pywin32)

rem ============================================================
rem  Done
rem ============================================================
echo.
echo  ============================================================
echo    준비 끝!
echo  ============================================================
exit /b 0

rem ============================================================
rem  Find Python; result goes into PY (empty if not found)
rem
rem  PY always holds a directly runnable form. Paths may contain spaces so
rem  they are stored quoted and invoked as %PY% directly.
rem  Never use %PY% inside for /f - the quotes would nest and fail.
rem ============================================================
:find_python
set "PY="

rem (1) py launcher - always present with an official Python install
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PY=py -3"
    goto :eof
)

rem (2) python on PATH, excluding the Microsoft Store stub
for /f "delims=" %%P in ('where python 2^>nul') do (
    echo %%P | find /i "WindowsApps" >nul
    if errorlevel 1 (
        if not defined PY set PY="%%P"
    )
)
if defined PY goto :eof

rem (3) just-installed case: PATH not refreshed yet, check install dirs
for %%V in (316 315 314 313 312 311) do (
    if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
    if not defined PY if exist "C:\Program Files\Python%%V\python.exe" set PY="C:\Program Files\Python%%V\python.exe"
)
goto :eof
