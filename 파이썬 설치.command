#!/bin/bash
# 바이브 코딩 실습 - 맥용 환경 설치 (더블클릭해서 실행)

# 브라우저로 받은 파일에는 macOS가 "격리(quarantine)" 표시를 자동으로 붙인다.
# 실행되자마자 스스로 그 표시를 지운다 (실패해도 무시하고 계속 진행).
xattr -d com.apple.quarantine "$0" 2>/dev/null

cd "$(dirname "$0")" || exit 1

echo ""
echo " ============================================================"
echo "   바이브 코딩 실습 - 환경 설치 (macOS)"
echo " ============================================================"
echo ""
echo "   이 실습은 파이썬만 미리 깔아두고, 나머지 코드는 여러분이 AI와"
echo "   함께 하나하나 만들어 갑니다. 그래서 이 설치 파일은 파이썬만 준비합니다."
echo "   이미 깔려 있으면 최신 버전인지도 같이 확인합니다."
echo "   끝날 때까지 이 창을 닫지 마세요."
echo ""

finish() {
  echo ""
  echo "   창을 닫으려면 아무 키나 누르세요..."
  read -r -n 1 -s
  exit "$1"
}

# ------------------------------------------------------------
# 1단계 - 파이썬 확인 (이미 있으면 최신 버전인지도 같이 확인)
# ------------------------------------------------------------
echo " [1/2] 파이썬이 이미 있는지 확인합니다..."
PY=""
for c in python3.14 python3.13 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$c"
    break
  fi
done

PY_BEFORE=""
if [ -n "$PY" ]; then
  PY_BEFORE="$($PY --version 2>&1)"
  echo "        이미 있습니다 - $PY_BEFORE"
else
  echo "        없습니다."
fi

if command -v brew >/dev/null 2>&1; then
  echo ""
  echo " [1/2] brew 로 최신 버전인지 확인합니다 (몇 초 걸립니다)..."
  brew upgrade python@3.14 >/dev/null 2>&1
  brew upgrade python@3.13 >/dev/null 2>&1
  brew upgrade python3 >/dev/null 2>&1

  PY=""
  for c in python3.14 python3.13 python3; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
  done

  if [ -n "$PY" ]; then
    PY_AFTER="$($PY --version 2>&1)"
    if [ "$PY_BEFORE" = "$PY_AFTER" ]; then
      echo "        이미 최신 버전입니다 - $PY_AFTER"
    else
      echo "        최신 버전으로 업데이트했습니다 - $PY_AFTER"
    fi
  else
    echo ""
    echo " [1/2] 파이썬을 설치합니다..."
    brew install python@3.14 || brew install python3
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
elif [ -z "$PY" ]; then
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

  for c in python3.14 python3.13 python3; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
  done
  if [ -z "$PY" ]; then
    echo ""
    echo " [!] 아직 파이썬을 찾지 못했습니다. 강사에게 문의하세요."
    finish 1
  fi
  echo "        설치 완료 - $($PY --version 2>&1)"
else
  echo "        Homebrew 가 없어 최신 버전인지는 확인하지 못합니다. 있는 그대로 사용합니다."
fi

# ------------------------------------------------------------
# 2단계 - 설정 파일 준비 (라이브러리는 실습하면서 직접 pip install 한다)
# ------------------------------------------------------------
echo ""
echo " [2/2] 설정 파일(.env)을 준비합니다..."
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
echo "   설치 끝. 파이썬 준비 완료입니다."
echo " ============================================================"
echo ""
echo "   다음에 할 일"
echo "     1) 열리는 편집기에 발급받은 키를 채우고 저장"
echo "     2) 실습 페이지의 안내대로 pip install 과 코드 작성을 직접 진행"
echo ""
[ -f "news-report-bot/.env" ] && open -e "news-report-bot/.env"
finish 0
