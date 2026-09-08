"""DART 점검 — "0건"이 왜 0건인지 확인하는 파일.

DART 목록 조회는 회사 이름으로 검색할 수 없다. 기간 안의 공시를 전부 받아온 뒤
직접 골라내야 한다. 그래서 0건이 나오는 이유가 여러 가지다.

  · 그 기간에 공시가 아예 없다 (주말·공휴일)
  · 공시는 있지만 그 회사 것이 없다 (하루치만 보면 흔하다)
  · 공시가 너무 많아서 뒷페이지까지 못 봤고, 그 회사 것이 뒤에 있었다
  · 인증키 문제

이 파일은 기간을 1일 / 3일 / 7일로 늘려가며 각각 몇 건이 잡히는지 보여준다.

실행: python dart_점검.py
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, timedelta

# ── 여기만 본인 값으로 바꾼다 ─────────────────────────────
API_KEY = "여기에_DART_인증키_붙여넣기"
WATCH = ["삼성물산", "GS건설"]   # 지켜볼 회사 이름 (여러 개면 쉼표로)
# ────────────────────────────────────────────────────────

KST_OFFSET = timedelta(hours=9)


# 인터넷 접속은 파이썬 기본 기능인 urllib 으로 한다. urllib 은 윈도우 인증서
# 저장소를 보기 때문에 회사 인증서가 이미 신뢰돼 있어 별도 설정이 필요 없다.
# requests 로 바꾸면 certifi 목록만 보게 되어 첫 접속부터 실패한다.


def fetch_page(begin: date, end: date, page: int) -> dict:
    params = urllib.parse.urlencode({
        "crtfc_key": API_KEY,
        "bgn_de": begin.strftime("%Y%m%d"),
        "end_de": end.strftime("%Y%m%d"),
        "page_no": page,
        "page_count": 100,
    })
    url = "https://opendart.fss.or.kr/api/list.json?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check(days: int) -> None:
    end = date.today()
    begin = end - timedelta(days=days - 1)
    print("=" * 70)
    print(f"[최근 {days}일] {begin} ~ {end}")

    total = 0
    matched = []
    matched_corps = Counter()
    page = 1
    total_page = 1

    while page <= total_page:
        try:
            body = fetch_page(begin, end, page)
        except urllib.error.HTTPError as exc:
            print(f"  HTTP {exc.code} — 요청이 거부됐다.")
            return
        except Exception as exc:
            text = str(exc)
            print(f"  연결 자체가 안 됨: {type(exc).__name__}: {text}")
            if "CERTIFICATE" in text:
                print("  → 인증서 문제다. 한국뉴스_점검.py 를 실행하면 requests 와")
                print("     urllib 중 무엇이 막히는지 갈라준다.")
            else:
                print("  → 회사 네트워크가 opendart.fss.or.kr 을 막고 있을 수 있다.")
            return

        status = body.get("status")
        if status == "013":
            print("  이 기간에 공시가 아예 없다 (주말·공휴일이면 정상)")
            return
        if status != "000":
            print(f"  DART 응답 오류 [{status}] {body.get('message')}")
            if status == "020":
                print("  → 하루 호출 한도 초과. 내일 다시.")
            if status in ("010", "011", "012"):
                print("  → 인증키가 잘못됐거나 아직 활성화되지 않았다.")
            return

        rows = body.get("list", [])
        total += len(rows)
        total_page = int(body.get("total_page", 1) or 1)

        for row in rows:
            corp = row.get("corp_name", "")
            if any(name in corp for name in WATCH):
                matched.append(f"[{corp}] {row.get('report_nm','')} ({row.get('rcept_dt','')})")
                matched_corps[corp] += 1

        page += 1

    print(f"  기간 안의 전체 공시: {total}건 (페이지 {total_page}개를 전부 확인)")
    print(f"  '{', '.join(WATCH)}' 관련: {len(matched)}건")
    for line in matched[:10]:
        print(f"    · {line}")
    if len(matched) > 10:
        print(f"    ... 외 {len(matched) - 10}건")
    if matched_corps:
        print("  걸린 회사별 건수 (부분일치가 뭘 끌어왔는지 확인):")
        for name, count in matched_corps.most_common():
            print(f"    {name}: {count}건")


if __name__ == "__main__":
    if API_KEY.startswith("여기에"):
        print("먼저 이 파일을 열어서 API_KEY 에 발급받은 DART 인증키를 붙여넣으세요.")
        sys.exit(1)

    print(f"지켜볼 회사: {', '.join(WATCH)}")
    print()
    for days in (1, 3, 7):
        check(days)

    print("=" * 70)
    print("""
읽는 방법
  · 1일은 0건인데 7일은 몇 건 나온다     → 정상이다. 그 회사가 매일 공시하지는 않는다.
                                          프로그램의 조회 기간을 늘리면 된다.
  · 전체 공시는 많은데 관련은 0건         → 그 회사가 그 기간에 공시를 안 냈거나,
                                          이름이 DART 에 등록된 이름과 다른 것이다.
                                          아래 회사별 집계에서 실제 이름을 확인한다.
  · 이름을 짧게 넣으면 오히려 나빠진다     → "삼성" 으로 넣으면 최근 일주일에 140건이
                                          걸리는데 그중 94건이 삼성자산운용 ETF 서류이고
                                          삼성전자는 0건이다(실측). 구체적으로 넣는다.
  · 전부 "이 기간에 공시가 아예 없다"      → 주말·공휴일이다. 평일 기준으로 다시.
  · 인증키 관련 오류가 뜬다               → 발급 직후면 잠시 뒤 다시 시도해본다.
""")
