@echo off
chcp 65001 >nul 2>&1
title 바이브 코딩 실습 - 환경 준비

rem ============================================================
rem  창이 바로 닫히는 것을 막는다
rem
rem  더블클릭으로 실행하면, 중간에 오류가 나도 창이 즉시 닫혀서 무엇이
rem  잘못됐는지 볼 수 없다. 그래서 자기 자신을 한 번 더 불러 실행하고,
rem  그 실행이 끝나거나 실패하면 창을 붙잡아 둔다.
rem  (이 파일은 CRLF 줄바꿈으로 저장해야 한다. LF 로 저장하면 cmd 가
rem   라벨을 찾지 못해 아무 메시지 없이 창이 닫힌다 — .gitattributes 참고)
rem ============================================================
if /i not "%~1"=="__run" (
    call "%~f0" __run
    echo.
    echo    창을 닫으려면 아무 키나 누르세요...
    pause >nul
    exit /b
)

rem 브라우저로 받은 파일에는 Windows가 "인터넷에서 받음" 표시(Mark of the Web)를
rem 붙인다. 보안 정책이 엄격한 PC에서는 이 표시 때문에 실행이 막힐 수 있어
rem 스스로 지운다. (관리자 권한 불필요, 실패해도 무시하고 계속 진행)
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
rem  1단계 - 파이썬
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
rem  2단계 - 부품(라이브러리) 3개
rem
rem  실습 중에 받게 하면 시간이 걸리고, 사내망에서 막히면 그 자리에서 멈춘다.
rem  특히 메일 발송에 쓰는 pywin32 는 가장 많이 막히는 구간에 필요하다.
rem
rem  %PY% -m pip 으로 설치하는 이유: 방금 찾은 그 파이썬에 정확히 깔린다.
rem  (여러 버전이 깔린 PC에서 "설치했는데 없다"는 문제가 여기서 생긴다)
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
rem  끝
rem ============================================================
echo.
echo  ============================================================
echo    준비 끝!
echo  ============================================================
echo.
echo    남은 준비물
echo      1) DART 인증키 발급받아 메모장에 붙여두기
echo      2) 아웃룩이 로그인되어 있는지 확인
echo      3) 살펴볼 키워드 3개 정해오기
exit /b 0

rem ============================================================
rem  파이썬 찾기 - 결과를 PY 에 넣는다 (못 찾으면 비어 있음)
rem
rem  PY 는 항상 "그대로 실행하면 되는 형태"로 넣는다.
rem  경로에 공백이 있을 수 있어 따옴표째로 넣고, %PY% 로 직접 실행한다.
rem  (for /f 안에서 %PY% 를 쓰면 따옴표가 겹쳐 실패하므로 그렇게 쓰지 않는다)
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

rem (3) 방금 설치해서 PATH 가 아직 갱신되지 않은 경우 설치 경로를 직접 확인
for %%V in (316 315 314 313 312 311) do (
    if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
    if not defined PY if exist "C:\Program Files\Python%%V\python.exe" set PY="C:\Program Files\Python%%V\python.exe"
)
goto :eof
