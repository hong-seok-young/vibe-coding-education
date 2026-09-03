"""한국 뉴스 수집 점검 — 인증키 없이 되는 방법이 실제로 되는지 확인하는 파일.

구글 뉴스 RSS는 인증키도, 가입도, 호출 한도도 없다. 한국어 키워드가 그대로 통한다.
이 파일을 실행하면 내 PC/회사 네트워크에서 실제로 기사가 몇 건 잡히는지 바로 보인다.

실행: python 한국뉴스_점검.py
(pip install 필요 없음 — 파이썬에 기본 포함된 기능만 쓴다)
"""

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


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
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
        print(f"  연결 자체가 안 됨: {type(exc).__name__}: {exc}")
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
  · 구글 뉴스 RSS에서 기사가 잘 나온다   → 이걸로 가면 된다. 인증키가 아예 필요 없다.
  · 구글만 막히고 언론사 RSS는 나온다     → 회사가 구글 뉴스를 막은 것. 언론사 RSS로 간다.
  · 전부 "연결 자체가 안 됨"              → 회사 네트워크가 외부를 막고 있다.
                                            개인 네트워크(핫스팟)에서 다시 시험해본다.
""")
