"""뉴스 수집 점검 — 이 PC 에서 뭐가 되고 뭐가 막히는지 확인하는 파일.

    python 한국뉴스_점검.py

수집이 안 될 때, 원인이 「회사 네트워크가 외부를 막아서」 인지 「파이썬이 쓰는 인증서
목록에 회사 인증서가 없어서」 인지 갈라준다. 이 둘은 대응이 완전히 다르다.

사내 PC 에서 실제로 측정한 것 (2026-09-08)
  urllib  (파이썬 기본) : 성공 — 신뢰하는 루트 인증서 67개 = 윈도우 인증서 저장소
  requests               : 실패 — 신뢰하는 루트 인증서 121개 = certifi 번들

회사 보안장비가 HTTPS 를 중간에서 열어보기 때문에, 파이썬은 진짜 인증서 대신 보안장비가
만든 인증서를 받는다. 회사가 윈도우에 심어둔 루트 인증서를 보는 쪽(urllib, feedparser)은
그냥 되고, 자기 목록만 보는 쪽(requests)은 첫 접속부터 실패한다.

pip install 없이 돌아간다 (requests 는 깔려 있으면 같이 시험하고, 없으면 건너뛴다).
"""

import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# 여기만 본인 키워드로 바꿔서 시험해보면 된다.
KEYWORDS = ["코스피", "삼성전자", "반도체 수출"]

NEWS_RSS = "https://news.google.com/rss/search"


def news_url(keyword):
    query = urllib.parse.urlencode(dict(q=keyword, hl="ko", gl="KR", ceid="KR:ko"))
    return NEWS_RSS + "?" + query


def show_trust_stores():
    print("=" * 72)
    print("■ 1단계 · 파이썬이 신뢰하는 인증서 목록 비교")
    print(f"  쓰는 파이썬: {sys.version.split()[0]}")
    try:
        default_ctx = ssl.create_default_context()
        print(f"  urllib 이 쓰는 기본 설정        : 루트 인증서 {len(default_ctx.get_ca_certs())}개"
              "  (윈도우에서는 윈도우 저장소를 읽는다)")
    except Exception as exc:
        print(f"  기본 설정을 못 읽었다: {exc}")
    try:
        import certifi
        certifi_ctx = ssl.create_default_context(cafile=certifi.where())
        print(f"  requests 가 쓰는 certifi 번들   : 루트 인증서 {len(certifi_ctx.get_ca_certs())}개"
              "  (회사 인증서는 여기 없다)")
    except ImportError:
        print("  certifi 가 안 깔려 있다 (requests 를 안 쓰면 상관없다)")
    except Exception as exc:
        print(f"  certifi 목록을 못 읽었다: {exc}")


def try_urllib(keyword):
    try:
        request = urllib.request.Request(news_url(keyword),
                                         headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=20) as response:
            return True, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code} — 주소가 막혔거나 바뀌었다"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def try_requests(keyword):
    try:
        import requests
    except ImportError:
        return None, "requests 가 안 깔려 있다 (안 써도 되니 괜찮다)"
    try:
        response = requests.get(news_url(keyword), timeout=20,
                                headers={"User-Agent": "Mozilla/5.0"})
        return True, response.text
    except Exception as exc:
        return False, f"{type(exc).__name__}: {str(exc)[:160]}"


def count_articles(raw):
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        return None, f"받아왔지만 뉴스 목록 형식이 아니다: {exc}"
    items = root.findall(".//item")
    titles = [(it.findtext("title") or "").strip() for it in items[:3]]
    return items, titles


def main():
    show_trust_stores()

    print()
    print("=" * 72)
    print("■ 2단계 · 같은 주소를 두 방식으로 받아보기")
    urllib_ok = requests_ok = None
    for keyword in KEYWORDS:
        print("-" * 72)
        print(f"[{keyword}]")

        ok, payload = try_urllib(keyword)
        if ok:
            items, titles = count_articles(payload)
            if items is None:
                print(f"  urllib   : 받아왔지만 형식이 이상하다 — {titles}")
            else:
                print(f"  urllib   : 성공, 기사 {len(items)}건")
                for title in titles:
                    print(f"               · {title[:64]}")
                urllib_ok = True if urllib_ok is None else urllib_ok
        else:
            print(f"  urllib   : 실패 — {payload}")
            urllib_ok = False

        ok, payload = try_requests(keyword)
        if ok is None:
            print(f"  requests : 건너뜀 — {payload}")
        elif ok:
            items, _ = count_articles(payload)
            print(f"  requests : 성공, 기사 {len(items) if items else 0}건")
            requests_ok = True if requests_ok is None else requests_ok
        else:
            print(f"  requests : 실패 — {payload}")
            requests_ok = False

    print()
    print("=" * 72)
    print("■ 읽는 방법")
    if urllib_ok and requests_ok is False:
        print("""
  urllib 은 되고 requests 는 막혔다 — 예상했던 그 상황이다.
  프로그램이 requests 를 쓰고 있으면 그게 원인이다. feedparser 나 urllib 으로
  바꾸면 된다. 실습 페이지 STEP 1 의 「막히면」 안내에 넣을 프롬프트가 있다.
  인증서 검증을 끄는 방법은 쓰지 않는다.""")
    elif urllib_ok:
        print("""
  둘 다 된다 — 이 PC 에서는 인증서 문제가 없다. 수집이 0건이면 네트워크가 아니라
  키워드 문제다. 더 넓은 단어로 바꿔본다.""")
    else:
        print("""
  urllib 까지 막혔다 — 회사 네트워크가 구글 뉴스 자체를 막고 있을 가능성이 크다.
  위에 찍힌 에러 문장을 그대로 복사해서 강사에게 보여주면 된다.
  개인 네트워크(휴대폰 핫스팟)에서 다시 실행해보면 네트워크 문제인지 갈린다.""")


if __name__ == "__main__":
    main()
