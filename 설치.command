#!/bin/bash
# 바이브 코딩 실습 - 맥용 환경 설치 (더블클릭해서 실행)
cd "$(dirname "$0")" || exit 1

echo ""
echo " ============================================================"
echo "   바이브 코딩 실습 - 환경 설치 (macOS)"
echo " ============================================================"
echo ""
echo "   파이썬과 실습에 필요한 라이브러리를 한 번에 설치합니다."
echo "   끝날 때까지 이 창을 닫지 마세요."
echo ""

finish() {
  echo ""
  echo "   창을 닫으려면 아무 키나 누르세요..."
  read -r -n 1 -s
  exit "$1"
}

# ------------------------------------------------------------
# 1단계 - 파이썬 확인
# ------------------------------------------------------------
echo " [1/4] 파이썬이 이미 있는지 확인합니다..."
PY=""
for c in python3.14 python3.13 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$c"
    break
  fi
done

if [ -n "$PY" ]; then
  echo "        이미 있습니다 - $($PY --version 2>&1)"
else
  echo "        없습니다. 지금 설치합니다."
  echo ""
  echo " [2/4] 파이썬을 설치합니다..."
  if command -v brew >/dev/null 2>&1; then
    brew install python@3.14 || brew install python3
  else
    echo ""
    echo "  ------------------------------------------------------------"
    echo "    Homebrew 가 없어 자동 설치를 못 합니다."
    echo "    브라우저를 열어드릴 테니 아래대로 해주세요."
    echo ""
    echo "      1) 노란색 [Download Python 3.x.x] 버튼 클릭"
    echo "      2) 받아진 .pkg 파일을 열어 계속 눌러 설치"
    echo "      3) 설치가 끝나면 이 창으로 돌아오세요"
    echo "  ------------------------------------------------------------"
    echo ""
    open "https://www.python.org/downloads/"
    echo "    설치를 마쳤으면 아무 키나 누르세요..."
    read -r -n 1 -s
  fi

  for c in python3.14 python3.13 python3; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
  done
  if [ -z "$PY" ]; then
    echo ""
    echo " [!] 아직 파이썬을 찾지 못했습니다. 강사에게 문의하세요."
    finish 1
  fi
  echo "        설치 완료 - $($PY --version 2>&1)"
fi

# ------------------------------------------------------------
# 3단계 - 실습 라이브러리 설치
# ------------------------------------------------------------
echo ""
echo " [3/4] 실습에 필요한 라이브러리를 설치합니다..."
if [ ! -f "news-report-bot/requirements.txt" ]; then
  echo " [!] news-report-bot/requirements.txt 를 찾을 수 없습니다."
  echo "     이 파일이 저장소 폴더 안에 그대로 있어야 합니다."
  finish 1
fi

if ! "$PY" -m pip install --user -r news-report-bot/requirements.txt --disable-pip-version-check; then
  # 최신 맥에서는 시스템 파이썬을 보호하느라 위 명령이 막힌다. 그때만 아래로 넘어간다.
  echo ""
  echo "        시스템 파이썬 보호 설정에 막혔습니다. 사용자 영역에만 설치를 다시 시도합니다..."
  if ! "$PY" -m pip install --user --break-system-packages -r news-report-bot/requirements.txt --disable-pip-version-check; then
    echo ""
    echo " [!] 라이브러리 설치에 실패했습니다."
    echo "     위에 나온 에러 메시지를 그대로 복사해서 강사에게 보여주세요."
    finish 1
  fi
fi

if ! "$PY" -c "import anthropic, requests, feedparser, dotenv" >/dev/null 2>&1; then
  echo " [!] 설치는 됐는데 불러오기가 안 됩니다. 강사에게 문의하세요."
  finish 1
fi
echo "        라이브러리 4개 확인 완료."

# ------------------------------------------------------------
# 4단계 - 설정 파일 준비
# ------------------------------------------------------------
echo ""
echo " [4/4] 설정 파일(.env)을 준비합니다..."
if [ -f "news-report-bot/.env" ]; then
  echo "        .env 가 이미 있습니다. 덮어쓰지 않고 그대로 둡니다."
elif [ -f "news-report-bot/.env.example" ]; then
  cp "news-report-bot/.env.example" "news-report-bot/.env"
  echo "        news-report-bot/.env 를 만들었습니다."
else
  echo "        .env.example 이 없어 건너뜁니다."
fi

echo ""
echo " ============================================================"
echo "   설치 끝. 준비 완료입니다."
echo " ============================================================"
echo ""
echo "   다음에 할 일"
echo "     1) 열리는 편집기에 발급받은 키 4종을 채우고 저장"
echo "     2) 이 폴더에서 실행:  $PY news-report-bot/main.py --dry-run"
echo ""
[ -f "news-report-bot/.env" ] && open -e "news-report-bot/.env"
finish 0
