"""NewsAPI 점검 — 뉴스 수집이 왜 안 되는지 30초 안에 확인하는 파일.

이 파일만 따로 실행하면, NewsAPI가 실제로 뭐라고 답하는지 그대로 보여준다.
프로그램 창에서 "검색 실패"만 뜰 때, 진짜 이유를 찾는 데 쓴다.

실행: python 뉴스api_점검.py
"""

import json
import urllib.error
import urllib.parse
import urllib.request

# 교육용 공용 키. 본인 키로 바꿔서 확인해도 된다.
API_KEY = "90087a9dc92e40719db3bb8795d44754"

# 한국어 키워드 / 영어 키워드를 같이 시험해서, "키 문제"인지 "한국 기사가 없는 것"인지 구분한다.
CASES = [
    ("한국어 키워드 + 언어를 한국어로 지정", {"q": "코스피", "language": "ko"}),
    ("한국어 키워드 (언어 지정 없음)", {"q": "코스피"}),
    ("한국어 키워드 (언어 지정 없음)", {"q": "삼성전자"}),
    ("영어 키워드 + 영어 지정", {"q": "samsung", "language": "en"}),
]


def probe(label: str, extra: dict) -> None:
    params = {"sortBy": "publishedAt", "pageSize": 5, "apiKey": API_KEY, **extra}
    url = "https://newsapi.org/v2/everything?" + urllib.parse.urlencode(params)

    print("=" * 70)
    print(f"[{label}]  q={extra.get('q')}  language={extra.get('language', '(지정 안 함)')}")

    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            code = resp.getcode()
    except urllib.error.HTTPError as exc:
        # NewsAPI는 실패해도 본문에 이유를 담아준다. 그게 진짜 원인이다.
        raw = exc.read().decode("utf-8", "replace")
        try:
            body, code = json.loads(raw), exc.code
        except ValueError:
            print(f"  HTTP {exc.code} — 응답 본문: {raw[:300]}")
            return
    except Exception as exc:  # 인터넷/방화벽 문제
        print(f"  연결 자체가 안 됨: {type(exc).__name__}: {exc}")
        print("  → 회사 네트워크가 newsapi.org 를 막고 있을 수 있다.")
        return

    if body.get("status") != "ok":
        print(f"  HTTP {code} — 실패")
        print(f"  이유: {body.get('message')}")
        print(f"  코드: {body.get('code')}")
        return

    total = body.get("totalResults", 0)
    articles = body.get("articles", [])
    print(f"  HTTP {code} — 성공. 검색 결과 {total}건 (여기서는 최대 5건만 표시)")
    if not articles:
        print("  → 요청은 정상인데 기사가 0건이다. 이 키워드로 걸리는 기사가 없다는 뜻.")
    for art in articles:
        src = (art.get("source") or {}).get("name", "?")
        print(f"    · [{src}] {art.get('title')}  ({art.get('publishedAt')})")


if __name__ == "__main__":
    for label, extra in CASES:
        probe(label, extra)
    print("=" * 70)
    print("""
읽는 방법
  · 첫 번째만 실패하고 두 번째부터 성공한다      → 언어를 한국어로 지정한 게 원인.
  · 전부 "apiKeyInvalid"                        → 인증키가 잘못됐다.
  · 전부 "rateLimited"                          → 오늘 쓸 수 있는 횟수를 다 썼다. 내일 다시.
  · 한국어는 0건인데 영어는 나온다               → 키는 정상. NewsAPI에 한국 기사가 거의 없는 것.
                                                   이 경우 뉴스 수집은 RSS 방식으로 바꾸는 게 낫다.
  · 전부 "연결 자체가 안 됨"                     → 회사 네트워크가 막고 있다.
""")
