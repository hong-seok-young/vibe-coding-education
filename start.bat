@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 바이브 코딩 교육 프로그램

echo ============================================
echo   바이브 코딩 교육 프로그램
echo ============================================
echo.

REM Node.js 설치 여부 확인
where node >nul 2>nul
if errorlevel 1 (
  echo [!] Node.js 가 설치되어 있지 않습니다.
  echo.
  echo     https://nodejs.org 에서 LTS 버전을 설치한 뒤
  echo     이 파일을 다시 실행해주세요.
  echo.
  pause
  exit /b 1
)

for /f "delims=" %%v in ('node -v') do echo Node.js %%v 확인
echo.

REM 처음 실행이면 패키지 설치 (몇 분 걸릴 수 있음)
if not exist "node_modules" (
  echo 처음 실행입니다. 필요한 패키지를 설치합니다... ^(2~3분^)
  echo.
  call npm install
  if errorlevel 1 (
    echo.
    echo [!] 패키지 설치에 실패했습니다.
    echo     사내 프록시 환경이면 dX팀에 문의해주세요.
    pause
    exit /b 1
  )
  echo.
)

echo 서버를 시작합니다.
echo    http://localhost:5173  ^<- 브라우저가 자동으로 열립니다
echo 종료하려면 이 창에서 Ctrl+C 를 누르거나 창을 닫으세요.
echo.

REM 서버가 뜰 때까지 잠깐 기다린 뒤 브라우저를 연다
start /min "" cmd /c "timeout /t 5 >nul & explorer http://localhost:5173"

call npm run dev

pause
