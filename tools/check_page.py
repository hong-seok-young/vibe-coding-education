"""만들어진 실습 HTML 을 점검한다.

    python3 tools/build_page.py && python3 tools/check_page.py

실제 교육 준비 중에 한 번씩 놓쳤던 것들을 그대로 검사한다.
  · 태그 짝이 맞는지 (프롬프트를 고치다 </li> 를 빠뜨린 적이 있다)
  · 페이지 수·체크박스 수가 기대치와 같은지
  · 붙여넣기용 프롬프트에 역슬래시가 들어있지 않은지 — 사내 AI 툴이 파일을
    만들 때 역슬래시를 날려서 프로그램이 안 열린 사례가 있다. 설명문 안의
    <code> 예시는 붙여넣는 글이 아니라서 검사 대상이 아니다
  · 낡은 표현이 남아있지 않은지 (결과창 -> 결과 칸 처럼 바꾼 말들)
  · 정답 코드 버튼에 박힌 main.py 가 지금 저장소의 main.py 와 같은지

<script> 안의 자바스크립트 문법은 여기서 보지 않는다. node 가 있으면
    node --check <(추출한 스크립트)
로 따로 확인한다.
"""

import base64
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PAGE = os.path.join(REPO, "DART 뉴스 크롤링 및 메일발송 프로그램 만들기.html")

EXPECTED_PAGES = 10        # 사전 준비 + STEP 7개 + API 목록 + The APPS
EXPECTED_CHECKBOXES = 13   # 사전 준비 6개 + STEP 페이지 7개
PAIRED_TAGS = ("div", "ul", "li", "p", "section", "details", "pre", "code", "span", "strong", "em")
# 낡은 표현 + 2026-09-08 검증에서 틀린 것으로 확인돼 되돌아오면 안 되는 처방들.
# VERIFY_X509_STRICT 제거는 사내 PC 에서 먹히지 않았다 (self-signed certificate in
# certificate chain). SMTP 는 포트가 막힌 게 아니라 STARTTLS 단계에서 끊긴다.
# "search.naver.com" — 예전에 네이버 검색 페이지를 긁던 방식. 금지어는 그 방식이지
# 네이버 API 자체가 아니다 (참고 페이지에서 정식 API 로 안내한다).
STALE_WORDS = ("결과창", "NewsAPI", "search.naver.com", ".env", "python3.12", "맥OS", "macOS",
               ".command", "VERIFY_X509_STRICT", "Authority Key Identifier",
               "certifi 를 지정", "포트를 막아")

problems = []


def fail(message):
    problems.append(message)


def main():
    with open(PAGE, encoding="utf-8") as f:
        page = f.read()

    for tag in PAIRED_TAGS:
        opened = len(re.findall(r"<%s[\s>]" % tag, page))
        closed = len(re.findall(r"</%s>" % tag, page))
        if opened != closed:
            fail(f"<{tag}> 짝이 안 맞는다: 열림 {opened}, 닫힘 {closed}")

    pages = len(re.findall(r'class="page"', page))
    if pages != EXPECTED_PAGES:
        fail(f"페이지 수가 {pages} 다 (기대 {EXPECTED_PAGES})")

    boxes = page.count('type="checkbox"')
    if boxes != EXPECTED_CHECKBOXES:
        fail(f"체크박스가 {boxes} 개다 (기대 {EXPECTED_CHECKBOXES})")

    prompts = re.findall(r'<pre[^>]*class="[^"]*prompt[^"]*"[^>]*>(.*?)</pre>', page, re.S)
    if not prompts:
        fail("붙여넣기용 프롬프트 블록을 찾지 못했다")
    for i, block in enumerate(prompts, 1):
        text = html.unescape(re.sub(r"<[^>]+>", "", block))
        if "\\" in text:
            fail(f"프롬프트 #{i} 에 역슬래시가 있다")

    for word in STALE_WORDS:
        if word in page:
            fail(f"낡은 표현 '{word}' 이 {page.count(word)} 번 남아있다")

    embedded = re.search(r'MAIN_PY_B64\s*=\s*"([A-Za-z0-9+/=]+)"', page)
    if not embedded:
        fail("정답 코드(main.py)가 페이지에 박혀있지 않다")
    else:
        with open(os.path.join(REPO, "news-report-bot", "main.py"), "rb") as f:
            if base64.b64decode(embedded.group(1)) != f.read():
                fail("박혀있는 main.py 가 지금 저장소의 main.py 와 다르다 — build_page.py 를 다시 실행할 것")

    index = os.path.join(REPO, "index.html")
    if not os.path.exists(index):
        fail("index.html 이 없다 — build_page.py 를 다시 실행할 것")
    else:
        with open(index, encoding="utf-8") as f:
            if f.read() != page:
                fail("index.html 이 실습 페이지와 다르다 — build_page.py 를 다시 실행할 것")

    if problems:
        print(f"문제 {len(problems)}건")
        for p in problems:
            print("  -", p)
        return 1

    print(f"이상 없음 — 페이지 {pages}장, 체크박스 {boxes}개, 프롬프트 {len(prompts)}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
