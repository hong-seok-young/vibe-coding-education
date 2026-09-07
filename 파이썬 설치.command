#!/bin/bash
# 바이브 코딩 실습 - 맥용 환경 준비 (더블클릭해서 실행)

# 브라우저로 받은 파일에는 macOS가 "격리(quarantine)" 표시를 자동으로 붙인다.
# 실행되자마자 스스로 그 표시를 지운다 (실패해도 무시하고 계속 진행).
xattr -d com.apple.quarantine "$0" 2>/dev/null

cd "$(dirname "$0")" || exit 1

echo ""
echo " ============================================================"
echo "   바이브 코딩 실습 - 환경 준비 (macOS)"
echo " ============================================================"
echo ""
echo "   실습에 필요한 것을 한 번에 준비합니다 - 파이썬과 부품."
echo "   코드는 실습 때 여러분이 AI와 함께 만들어 갑니다."
echo ""
echo "   이미 깔려 있는 건 그대로 씁니다. 버전은 최신이어도 괜찮습니다."
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
for c in python3 python3.13 python3.12; do
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
  echo "        brew 로 최신 버전인지 확인합니다 (몇 초 걸립니다)..."
  brew upgrade python3 >/dev/null 2>&1

  PY=""
  for c in python3 python3.13 python3.12; do
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
    echo "        파이썬을 설치합니다..."
    brew install python3
    for c in python3 python3.13 python3.12; do
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

  for c in python3 python3.13 python3.12; do
    if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
  done
  if [ -z "$PY" ]; then
    echo ""
    echo " [!] 아직 파이썬을 찾지 못했습니다. 강사에게 문의하세요."
    finish 1
  fi
  echo "        설치 완료 - $($PY --version 2>&1)"
else
  echo "        Homebrew 가 없어 버전 확인은 못 합니다. 있는 그대로 사용합니다."
fi

# ------------------------------------------------------------
# 2단계 - 부품(라이브러리) 설치
#
# 실습 중에 받게 하면 시간이 걸리고, 사내망에서 막히면 그 자리에서 멈춘다.
# $PY -m pip 으로 설치하는 이유: 방금 찾은 그 파이썬에 정확히 깔린다.
# (맥에는 메일 발송용 pywin32 를 설치하지 않는다 - 윈도우 전용 기능이다)
# ------------------------------------------------------------
echo ""
echo " [2/2] 실습에 필요한 부품을 받습니다 (1~2분)..."
if "$PY" -m pip install requests feedparser; then
  echo ""
  echo "        부품 준비 완료 (requests, feedparser)"
elif "$PY" -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests feedparser; then
  echo ""
  echo "        부품 준비 완료 (requests, feedparser)"
else
  echo ""
  echo " [!] 부품을 받지 못했습니다. 파이썬은 준비됐으니 실습은 시작할 수 있지만,"
  echo "     실습 중에 다시 받아야 합니다. 위 오류를 캡처해서 강사에게 보여주세요."
fi

echo ""
echo " ============================================================"
echo "   준비 끝!"
echo " ============================================================"
echo ""
echo "   (메일 발송은 윈도우 전용입니다. 맥에서는 수집까지만 됩니다)"
echo ""
finish 0
