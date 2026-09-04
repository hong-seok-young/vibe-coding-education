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
echo    실습에 필요한 것을 한 번에 준비합니다 - 파이썬과 부품 3개.
echo    코드는 실습 때 여러분이 AI와 함께 만들어 갑니다.
echo.
echo    이미 깔려 있는 건 그대로 씁니다. 버전은 최신이어도 괜찮습니다.
echo    2~3분 걸립니다. 끝날 때까지 이 창을 닫지 마세요.
echo.

rem ============================================================
rem  1단계 - 파이썬이 이미 있는지 확인
rem ============================================================
echo  [1/2] 파이썬이 이미 있는지 확인합니다...
call :find_python
if defined PY (
    for /f "tokens=*" %%V in ('%PY% --version 2^>^&1') do echo        이미 있습니다 - %%V
    goto :installed_ok
)
echo        없습니다.
echo.

where winget >nul 2>&1
if errorlevel 1 (
    echo        winget 이 없어서 직접 받는 방법으로 넘어갑니다.
    goto :manual_download
)

echo        파이썬을 설치합니다 (python.org 공식 배포판)...
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
for /f "tokens=*" %%V in ('%PY% --version 2^>^&1') do echo        준비 완료 - %%V

rem ============================================================
rem  2단계 - 부품(라이브러리) 3개 설치
rem
rem  실습 중에 받게 하면 시간이 걸리고, 사내망에서 막히면 그 자리에서 멈춘다.
rem  특히 메일 발송에 쓰는 pywin32 는 실습에서 가장 많이 막히는 구간에 필요하다.
rem  여기서 %PY% -m pip 으로 설치하는 이유: 방금 찾은 그 파이썬에 정확히 깔린다.
rem  (여러 버전이 깔린 PC에서 "설치했는데 없다"는 문제가 여기서 생긴다)
rem ============================================================
echo.
echo  [2/2] 실습에 필요한 부품 3개를 받습니다 (1~2분)...
%PY% -m pip install --upgrade pip >nul 2>&1
%PY% -m pip install requests feedparser pywin32
if not errorlevel 1 goto :libs_ok

echo.
echo        받아오는 데 실패했습니다. 회사 보안 장비 때문일 수 있어
echo        신뢰할 곳을 지정해서 다시 시도합니다...
%PY% -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org requests feedparser pywin32
if not errorlevel 1 goto :libs_ok

echo.
echo  [!] 부품을 받지 못했습니다. 파이썬은 준비됐으니 실습은 시작할 수 있지만,
echo      실습 중에 다시 받아야 합니다. 위에 나온 빨간 글씨를 캡처해서
echo      강사에게 보여주세요.
goto :done

:libs_ok
echo.
echo        부품 3개 준비 완료 (requests, feedparser, pywin32)

rem ============================================================
rem  끝
rem ============================================================
:done
echo.
echo  ============================================================
echo    준비 끝!
echo  ============================================================
echo.
echo    남은 준비물
echo      1) DART 인증키 발급받아 메모장에 붙여두기
echo      2) 아웃룩이 로그인되어 있는지 확인
echo      3) 살펴볼 키워드 3개 정해오기
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
