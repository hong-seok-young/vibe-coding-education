"""한국 뉴스 수집 점검 — 인증키 없이 되는 방법이 실제로 되는지 확인하는 파일.

구글 뉴스 RSS는 인증키도, 가입도, 호출 한도도 없다. 한국어 키워드가 그대로 통한다.
이 파일을 실행하면 내 PC/회사 네트워크에서 실제로 기사가 몇 건 잡히는지 바로 보인다.

실행: python 한국뉴스_점검.py
(pip install 필요 없음 — 파이썬에 기본 포함된 기능만 쓴다)
"""

import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

# 여기만 본인 키워드로 바꿔서 시험해보면 된다.
KEYWORDS = ["코스피", "삼성전자", "반도체 수출"]

# 언론사 RSS도 같이 시험한다 (키워드 검색은 안 되지만, 해당 분야 최신 기사가 통째로 온다)
PRESS_FEEDS = [
    ("연합뉴스 경제", "https://www.yna.co.kr/rss/economy.xml"),
    ("한국경제", "https://rss.hankyung.com/feed/economy.xml"),
    ("매일경제", "https://www.mk.co.kr/rss/30100041/"),
]


def make_ssl_context() -> ssl.SSLContext:
    """사내망(HTTPS를 중간에서 검사하는 환경)을 통과할 수 있는 설정.

    회사 보안 장비가 만든 인증서에는 Authority Key Identifier 항목이 없는데,
    파이썬 3.13 부터 이 항목을 요구하는 검사가 기본으로 켜져서 연결이 거부된다.
    그 검사만 끈다. 인증서 검증 자체는 그대로 켜둔다.
    """
    ctx = ssl.create_default_context()   # 윈도우에서는 윈도우 인증서 저장소를 함께 읽는다
    ctx.verify_flags &= ~getattr(ssl, "VERIFY_X509_STRICT", 0)
    return ctx


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20, context=make_ssl_context()) as resp:
        return resp.read().decode("utf-8", "replace")


def show_feed(label: str, url: str) -> None:
    print("=" * 70)
    print(f"[{label}]")
    try:
        raw = fetch(url)
    except urllib.error.HTTPError as exc:
        print(f"  HTTP {exc.code} — 이 주소가 막혔거나 주소가 바뀌었다.")
        return
    except Exception as exc:
        text = str(exc)
        print(f"  연결 자체가 안 됨: {type(exc).__name__}: {text}")

        if "unable to get local issuer certificate" in text:
            print("  → 회사 보안 장비의 인증서를 파이썬이 신뢰하지 않아서 막힌 것이다.")
            print("     pip install truststore 를 실행하면 윈도우가 이미 신뢰하는")
            print("     목록을 파이썬도 쓰게 되어 해결되는 경우가 많다.")
        elif "CERTIFICATE_VERIFY_FAILED" in text:
            print("  → 인증서 검사에서 막혔다. 이 파일은 사내망 대응을 이미 넣어뒀는데도")
            print("     막혔다면, 이 메시지를 그대로 복사해서 강사나 AI에게 보여주면 된다.")
            print(f"     (지금 쓰는 파이썬: {sys.version.split()[0]})")
        else:
            print("  → 회사 네트워크가 이 사이트를 막고 있을 수 있다.")
        return

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        print(f"  받아왔지만 뉴스 목록 형식이 아니다: {exc}")
        print(f"  받은 내용 앞부분: {raw[:200]}")
        return

    items = root.findall(".//item")
    print(f"  기사 {len(items)}건")
    if not items:
        print("  → 형식은 맞는데 기사가 0건이다.")
        return
    for item in items[:5]:
        title = (item.findtext("title") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        print(f"    · {title[:70]}")
        print(f"      {pub}")


if __name__ == "__main__":
    print("■ 구글 뉴스 RSS — 인증키 없이 한국어 키워드로 검색")
    for keyword in KEYWORDS:
        query = urllib.parse.quote(keyword)
        show_feed(
            f"구글 뉴스 RSS · '{keyword}'",
            f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko",
        )

    print()
    print("■ 언론사 RSS — 키워드 검색은 없지만 최신 기사가 통째로 온다")
    for label, url in PRESS_FEEDS:
        show_feed(label, url)

    print("=" * 70)
    print("""
읽는 방법
  · 구글 뉴스 RSS에서 기사가 잘 나온다        → 이걸로 가면 된다. 인증키가 아예 필요 없다.
  · 구글만 막히고 언론사 RSS는 나온다          → 회사가 구글 뉴스를 막은 것. 언론사 RSS로 간다.
  · "unable to get local issuer..."       → 회사 인증서를 파이썬이 못 믿는 상태다.
                                             pip install truststore 로 해결되는 경우가 많다.
  · 전부 "연결 자체가 안 됨"                   → 회사 네트워크가 외부를 막고 있다.
                                             개인 네트워크(핫스팟)에서 다시 시험해본다.
""")
