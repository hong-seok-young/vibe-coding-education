#!/usr/bin/env bash
# macOS: 더블클릭으로 실행 / Linux: bash start.command
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "  바이브 코딩 교육 프로그램"
echo "============================================"
echo

if ! command -v node >/dev/null 2>&1; then
  echo "[!] Node.js 가 설치되어 있지 않습니다."
  echo
  echo "    https://nodejs.org 에서 LTS 버전을 설치한 뒤"
  echo "    이 파일을 다시 실행해주세요."
  echo
  read -r -p "엔터를 누르면 닫힙니다..."
  exit 1
fi

echo "Node.js $(node -v) 확인"
echo

# 처음 실행이면 패키지 설치 (몇 분 걸릴 수 있음)
if [ ! -d node_modules ]; then
  echo "처음 실행입니다. 필요한 패키지를 설치합니다... (2~3분)"
  echo
  if ! npm install; then
    echo
    echo "[!] 패키지 설치에 실패했습니다."
    echo "    사내 프록시 환경이면 dX팀에 문의해주세요."
    read -r -p "엔터를 누르면 닫힙니다..."
    exit 1
  fi
  echo
fi

echo "서버를 시작합니다."
echo "   http://localhost:5173  ← 브라우저가 자동으로 열립니다"
echo "종료하려면 이 창에서 Ctrl+C 를 누르세요."
echo

# 서버가 뜰 때까지 잠깐 기다린 뒤 브라우저를 연다.
# 브라우저를 못 열어도(서버 환경 등) 실행은 계속되게 한다.
(
  sleep 4
  open "http://localhost:5173" 2>/dev/null \
    || xdg-open "http://localhost:5173" 2>/dev/null \
    || true
) &

npm run dev
