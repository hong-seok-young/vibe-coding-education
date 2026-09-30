"""단계별 정답 코드 파일을 만든다.

    python tools/make_stage_files.py

실습 페이지의 「정답 코드 파일 받기」 버튼은 단계마다 다른 파일을 내려줘야 한다.
STEP 0 에서 완성본을 받으면 실습이 통째로 사라지기 때문이다. 그래서 완성본
news-report-bot/main.py 하나를 원본으로 두고, 뒤 단계 기능을 덜어내는 방식으로
STEP 0~5 의 스냅샷을 만든다.

  STEP 5 = main.py 그대로 (완성본)
  STEP 4 = 5 에서 전체 실행 빼기
  STEP 3 = 4 에서 메일 발송 빼기
  STEP 2 = 3 에서 보고서 빼기
  STEP 1 = 2 에서 DART 빼기
  STEP 0 = 1 에서 뉴스 빼기 (버튼은 다섯 개 다 있고 누르면 안내만 나온다)

덜어낼 때 그 기능을 부르던 자리도 같이 손봐야 한다 (아래 CALL_PATCHES).

알파 실습(STEP 6~8)은 고도화 완성본 news-report-bot/고도화_main.py 를 원본으로
같은 방식으로 만든다.

  STEP 8 = 고도화_main.py 그대로
  STEP 7 = 8 에서 보고서 고도화 빼기 (보고서는 기본 보고서로)
  STEP 6 = 7 에서 스코어링 빼기

만들고 나면 tools/check_stage_files.py 로 아홉 개가 다 열리는지 확인한다.
"""

import ast
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(REPO, "news-report-bot", "main.py")
PLUS_SRC = os.path.join(REPO, "news-report-bot", "고도화_main.py")
OUT_DIR = os.path.join(REPO, "news-report-bot", "단계별")

# 단계마다 "여기서 새로 생기는 함수" — 앞 단계 파일에는 없어야 한다.
STAGE_FUNCS = {
    1: ["collect_news"],
    2: ["dart_fetch_all", "collect_dart"],
    3: ["merge", "collected_summary", "escape_html", "build_report_html", "save_report"],
    4: ["send_mail"],
    5: ["run_all"],
}

# 단계마다 버튼이 실제로 연결되는 시점. 아직 안 만든 기능의 버튼은 안내만 띄운다.
BUTTON_STAGE = {
    "뉴스 수집하기": 1,
    "DART 수집하기": 2,
    "보고서 만들기": 3,
    "메일 보내기": 4,
    "전체 실행": 5,
}

# 뒤 단계 함수를 앞 단계에서 부르고 있는 자리. (없애려는 함수, 그 호출을 지운 모습)
CALL_PATCHES = [
    # 보고서(STEP 3) 전에는 모아두는 정리가 없다 — 수집 결과를 칸에만 보여준다.
    ("merge", "    merge(items)\n", ""),
    ("collected_summary",
     '    render(news_box, items, tail=collected_summary("뉴스 %d건" % len(items)))\n',
     '    render(news_box, items, tail="뉴스 %d건 가져왔습니다." % len(items))\n'),
    ("collected_summary",
     "    render(dart_box, items, tail=collected_summary(tail))\n",
     "    render(dart_box, items, tail=tail)\n"),
]

NOT_READY = '''def not_ready():
    """아직 연결하지 않은 버튼. 다음 단계에서 실제 동작을 붙인다."""
    log("이 버튼은 아직 준비 중입니다. 다음 단계에서 연결합니다.")


'''


def source_of(tree, src_lines, name):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            start = node.lineno - 1
            # 바로 위에 붙은 주석 줄까지 함께 가져온다
            while start > 0 and src_lines[start - 1].lstrip().startswith("#"):
                start -= 1
            end = node.end_lineno
            while end < len(src_lines) and src_lines[end].strip() == "":
                end += 1
            return start, end
    raise SystemExit("함수를 찾지 못했다: " + name)


def build_stage(stage, src):
    if stage == 5:
        return src                            # 완성본은 main.py 그대로
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)

    # 1) 이 단계보다 뒤에 나오는 함수를 잘라낸다 (뒤에서부터 지워야 줄 번호가 안 밀린다)
    drop = []
    for st, names in STAGE_FUNCS.items():
        if st > stage:
            for n in names:
                drop.append(source_of(tree, lines, n))
    for start, end in sorted(drop, reverse=True):
        del lines[start:end]
    text = "".join(lines)

    # 2) 잘라낸 함수를 부르던 자리를 손본다
    for func, old, new in CALL_PATCHES:
        gone = any(func in names for st, names in STAGE_FUNCS.items() if st > stage)
        if gone and old in text:
            text = text.replace(old, new)

    # 3) 아직 연결 안 된 버튼은 안내만 띄우게
    pending = [label for label, st in BUTTON_STAGE.items() if st > stage]
    if pending:
        for label in pending:
            for st, names in STAGE_FUNCS.items():
                if BUTTON_STAGE[label] == st:
                    text = text.replace('("%s", %s),' % (label, names[-1]),
                                        '("%s", not_ready),' % label)
        text = text.replace("# ── 창 조립 ", NOT_READY + "# ── 창 조립 ")

    # 4) 머리말을 단계에 맞게
    text = text.replace(
        '"""이슈 리포트 봇 — 완성본 (실습 정답 코드)',
        '"""이슈 리포트 봇 — STEP %d 까지 만든 상태 (실습 정답 코드)' % stage, 1)
    if stage < 5:
        text = text.replace(
            "2026-09-08 사내 PC 에서 뉴스 20건 + DART 공시 2건 수집 -> 아웃룩 자동 발송까지\n"
            "실제로 확인했다. 각 STEP 주석은 실습 페이지의 STEP 번호와 같다.",
            "실습 페이지 STEP %d 까지 따라왔을 때 나와야 하는 모습이다. 아직 붙이지 않은\n"
            "버튼은 눌러도 진행 상황 칸에 안내만 나온다. 완성본은 STEP 5 파일이다." % stage, 1)
    return text


# ── 알파 실습 ────────────────────────────────────────────────
# 단계마다 새로 생기는 것 (함수든 설정값이든 이름으로 적는다)
PLUS_STAGE_NAMES = {
    7: ["KEYWORD_POINT", "IMPORTANT_POINT", "IMPORTANT_DART", "score_item", "score_items"],
    8: ["TOP_N", "REPORT_STYLE", "REPORT_SCRIPT", "report_item_html", "build_report_plus"],
}
BASIC_REPORT_PAGE = (
    '    page = ("<!doctype html><html lang=ko><head><meta charset=utf-8>"\n'
    '            "<title>오늘의 이슈 리포트</title></head>"\n'
    '            "<body style=\\"background:#f6f7f6;padding:24px\\">"\n'
    '            + build_report_html() + "</body></html>")\n')
PLUS_CALL_PATCHES = [
    (7, '    items = score_items(items, "뉴스")\n', ""),
    (7, '    items = score_items(items, "DART")\n', ""),
    (8, "    page = build_report_plus()\n", BASIC_REPORT_PAGE),
]
PLUS_BANNERS = {7: "# STEP 7. 스코어링", 8: "# STEP 8. 보고서 고도화"}


def span_of(tree, src_lines, name):
    """함수든 설정값(대입문)이든 이름으로 찾아 위에 붙은 주석까지 범위를 준다."""
    for node in tree.body:
        hit = (isinstance(node, ast.FunctionDef) and node.name == name) or (
            isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets))
        if hit:
            start = node.lineno - 1
            while (start > 0 and src_lines[start - 1].lstrip().startswith("#")
                   and not src_lines[start - 1].lstrip().startswith("# ═")):
                start -= 1
            end = node.end_lineno
            while end < len(src_lines) and src_lines[end].strip() == "":
                end += 1
            return start, end
    raise SystemExit("찾지 못했다: " + name)


def build_plus_stage(stage, src):
    if stage == 8:
        return src                            # 고도화 완성본은 그대로
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    drop = [span_of(tree, lines, n) for st, names in PLUS_STAGE_NAMES.items()
            if st > stage for n in names]
    for start, end in sorted(set(drop), reverse=True):
        del lines[start:end]
    text = "".join(lines)
    # 빠진 단계의 구분 제목(═══ 세 줄)도 지운다
    for st, title in PLUS_BANNERS.items():
        if st > stage:
            i = text.index(title)
            a = text.rindex("# ═", 0, i)
            b = text.index(chr(10), text.index("# ═", i)) + 1
            while text[b:b + 1] == chr(10):
                b += 1
            text = text[:a] + text[b:]
    for st, old, new in PLUS_CALL_PATCHES:
        if st > stage:
            assert old in text, old
            text = text.replace(old, new)
    text = text.replace(
        '"""이슈 리포트 봇 — 고도화 완성본 (알파 실습 정답 코드)',
        '"""이슈 리포트 봇 — STEP %d 까지 만든 상태 (알파 실습 정답 코드)' % stage, 1)
    return text


def main():
    src = io.open(SRC, encoding="utf-8").read()
    os.makedirs(OUT_DIR, exist_ok=True)
    for stage in range(6):
        text = build_stage(stage, src)
        ast.parse(text)                       # 문법이 깨졌으면 여기서 멈춘다
        path = os.path.join(OUT_DIR, "STEP%d.py" % stage)
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        print("  STEP%d.py  %5d줄  %6.1f KB" % (
            stage, text.count(chr(10)), len(text.encode("utf-8")) / 1024))
    print("완성본(STEP5)이 main.py 와 같은가:",
          io.open(os.path.join(OUT_DIR, "STEP5.py"), encoding="utf-8").read() == src)

    plus = io.open(PLUS_SRC, encoding="utf-8").read()
    for stage in (6, 7, 8):
        text = build_plus_stage(stage, plus)
        ast.parse(text)
        path = os.path.join(OUT_DIR, "STEP%d.py" % stage)
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        print("  STEP%d.py  %5d줄  %6.1f KB" % (
            stage, text.count(chr(10)), len(text.encode("utf-8")) / 1024))
    print("고도화 완성본(STEP8)이 고도화_main.py 와 같은가:",
          io.open(os.path.join(OUT_DIR, "STEP8.py"), encoding="utf-8").read() == plus)


if __name__ == "__main__":
    main()
