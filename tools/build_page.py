"""실습 HTML 을 만든다 — 저장소 루트의 페이지 하나를 통째로 다시 쓴다.

    python3 tools/build_page.py

단계별 내용은 steps.py, 사전 준비 페이지는 prep.html 에 있다. 페이지의
"정답 코드 파일 받기" 버튼용으로 news-report-bot/main.py 를 base64 로 박아 넣기
때문에, main.py 를 고친 뒤에도 이걸 다시 실행해야 페이지에 반영된다.

만든 뒤 확인할 것 — 태그 짝, 체크박스 수, <script> 안의 문법(node --check),
그리고 브라우저로 열어서 페이지 이동이 되는지.
"""

import os
import re
import html as h

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

from steps import STEPS

# 사내 AI 툴은 파일/폴더를 직접 만들거나 읽지 못하는 대화형 도구라 (프롬프트를 넣으면
# 그에 맞는 .py 파일을 다운로드해 주는 방식), 매 단계마다 "앞에서 만든 것에 이걸 더해서
# 전체를 통째로 다시 파일로 달라"는 요청을 프롬프트 끝에 붙인다. (그래야 학생이 어디에
# 뭘 끼워 넣을지 고민하지 않고, 매 단계마다 완성된 파일 하나만 들고 갈 수 있다.)
#
# 프롬프트에는 "내가 받아서 덮어쓸 거야" 같은 말을 넣지 않는다. AI는 파일을 내려주기만
# 하고, 같은 이름으로 또 받으면 브라우저가 "main (2).py" 처럼 번호를 붙여 저장하기 때문에
# 학생 입장에서 "덮어쓰기"가 실제로 일어나지 않는다. 그래서 요청은 어디까지나 "앞에 것에
# 더해서 전체를 다시 달라"로만 하고, 받은 파일을 어떻게 다루는지는 아래 안내문에서 따로
# 설명한다.
#
# 단, STEP 0 은 AI를 처음 쓰기 시작하는 단계라 아직 내 PC에 아무 파일도 없다. 앞 단계가
# 없으니 "앞에 것에 더해서"라는 말도 성립하지 않아, 첫 단계만 "새로 만들어주고 + 저장·실행
# 방법도 알려달라"로 따로 쓴다. (사전 준비는 파이썬 설치뿐이고 폴더/파일을 미리 주지 않는다.)
_NO_BACKSLASH = (
    " 그리고 코드에 역슬래시 문자는 쓰지 말아줘. 받은 파일에서 역슬래시가 사라져서 프로그램이 "
    "안 열린 적이 있어 — 줄바꿈이 필요하면 chr(10) 을 쓰면 된다고 들었어."
)
_FIRST_FILE_SUFFIX = (
    "\n\n코드는 채팅창에 쓰지 말고 .py 파일로 첨부해줘. 파일을 어디에 어떤 이름으로 저장하고 "
    "어떻게 실행하면 창이 뜨는지도 순서대로 알려줘." + _NO_BACKSLASH
)
_FULL_FILE_SUFFIX = (
    "\n\n코드는 채팅창에 쓰지 말고, 앞에 만들어준 것에 이걸 더해서 전체를 통째로 .py 파일로 "
    "다시 첨부해줘. 되던 기능은 하나도 빼지 말고, 바뀐 부분만 잘라서 주지 말고 항상 전체를." + _NO_BACKSLASH
)
for _step in STEPS:
    if _step["part"] == 4:      # 알파 실습은 여러 파일짜리 프로젝트라 「.py 파일 하나로」 문구를 붙이지 않는다
        continue
    _step["prompt"] = _step["prompt"] + (
        _FIRST_FILE_SUFFIX if _step["id"] == "s0" else _FULL_FILE_SUFFIX
    )


LINEBREAK = chr(10)


def esc(s):
    return h.escape(s)


# ── prep.html 에서 섹션 A~E 추출 ──────────────────
prep_src = open(f"{HERE}/prep.html", encoding="utf-8").read()


def between(text, start_marker, end_marker, start_from=0):
    i = text.index(start_marker, start_from)
    j = text.index(end_marker, i + len(start_marker))
    return text[i:j], i, j


sections_prep, _, _ = between(
    prep_src,
    '  <section class="group">\n    <div class="group-head">\n      <span class="num">A</span>',
    '\n\n  <div class="callout">',
)

# 파이썬 및 실습 도구 설치.bat 은 페이지 안에 내장하지도, 깃허브 링크로 받게 하지도 않는다.
# base64로 박아넣고 Blob 으로 강제 다운로드시키는 방식은 "HTML smuggling"과 패턴이
# 같아 회사 PC 보안 소프트웨어가 다운로드 자체를 막았고(실제 확인됨), 깃허브 링크로
# 바꿔도 사용자 입장에서 낯선 화면으로 튄다는 문제가 있었다. 그래서 이 파일은 실습
# 폴더 안에 이미 들어있는 로컬 파일로 취급하고(더블클릭만 안내), 이 페이지 하나만
# 따로 받은 예외적인 경우에만 파이썬 공식 사이트 링크로 안내한다.

PART_LABELS = {1: "실습 1 · 수집", 2: "실습 2 · 보고서", 3: "실습 3 · 메일 발송", 4: "알파 실습 · 고도화"}

# ── STEP 카드 렌더링 (한 STEP = 한 페이지) ──────────────────

# STEP 0 페이지에 넣는 완성 창 그림. tools/program-window.png 을 base64 로 박아
# 넣어서 HTML 파일 하나만 있어도 그림이 보이게 한다 (이미지 파일을 따로 들고 다니지
# 않아도 된다). 그림은 _lab/capture.py 로 main.py 를 실제로 띄워 찍는다 —
# 화면을 긁으면 사내 보안 워터마크가 같이 찍히므로 PrintWindow 방식을 쓴다.
import base64 as _b64

with open(f"{HERE}/program-window.png", "rb") as _f:
    SHOT_B64 = _b64.b64encode(_f.read()).decode("ascii")

# STEP 1~5 페이지에 넣는 「그 단계를 마친 화면」. tools/capture_steps.py 로 찍는다.
# 그림이 없는 단계는 그냥 비워둔다 (아직 안 찍었거나, 메일 발송이 필요한 단계).
STEP_SHOTS = {}
_SHOT_SPECS = [   # (단계, 파일, 설명, 세로로 긴 그림인가)
    ("s1", "step1.png", "뉴스 수집을 마친 프로그램 화면", False),
    ("s2", "step2.png", "DART 수집까지 마친 프로그램 화면", False),
    ("s3", "step3-report.png", "「보고서 만들기」 를 누르면 브라우저에 뜨는 보고서", True),
    ("s4", "step4-mail.png", "아웃룩으로 받은 메일", True),
]
for _sid, _file, _cap, _tall in _SHOT_SPECS:
    _path = f"{HERE}/step-shots/{_file}"
    if not os.path.exists(_path):
        continue
    with open(_path, "rb") as _f:
        _b = _b64.b64encode(_f.read()).decode("ascii")
    _cls = "shot tall" if _tall else "shot"
    STEP_SHOTS[_sid] = (LINEBREAK + f'    <figure class="{_cls}">' + LINEBREAK +
                        f'      <img src="data:image/png;base64,{_b}" alt="{_cap}">' + LINEBREAK +
                        f'      <figcaption>{_cap}</figcaption>' + LINEBREAK +
                        '    </figure>' + LINEBREAK)

SHOT_HTML = f'''
    <figure class="shot">
      <img src="data:image/png;base64,{SHOT_B64}"
           alt="완성된 프로그램 창 — 입력 칸 세 개, 버튼 다섯 개, 결과 칸 세 개">
    </figure>
'''


# 받는 파일 이름 — 몇 단계까지 된 파일인지 이름만 보고 알 수 있게
STAGE_FILE_NAMES = {
    "s0": "STEP0_뼈대.py", "s1": "STEP1_뉴스수집.py", "s2": "STEP2_DART수집.py",
    "s3": "STEP3_보고서.py", "s4": "STEP4_메일발송.py", "s5": "STEP5_통합실행.py",
}
CRITERIA_TMPL = '''    <div class="criteria-box">
      <p class="criteria-label">성공 기준</p>
      <ul>
{}
      </ul>
    </div>
'''
DOWNLOAD_TMPL = '''    <details class="answer-details">
      <summary>안 되면? 이 단계까지 만든 프로그램 받기</summary>
      <p class="tiny" style="margin-top: 4px;">이 STEP 을 마쳤을 때 나와야 하는 파일이다.
        완성본이 아니라 <strong>딱 여기까지만</strong> 들어있으니, 받아서 그대로 실행하고
        다음 단계를 이어가면 된다.</p>
      <div class="actions" style="margin-top: 8px;">
        <button type="button" class="btn primary download-stage-btn"
                data-stage="{num}" data-file="{file}">
          <span class="arrow">⬇</span> STEP {num} 까지의 프로그램 받기 <small class="dl-name">{file}</small>
        </button>
      </div>
    </details>'''


def render_step_page(step, index, total):
    showcase = step["part"] == 4          # 알파 실습: 사례 설명 + 프롬프트만, 실습은 자율
    # 설치는 사전 준비의 bat 한 번으로 끝난다 — STEP 마다 설치 명령을 보여주지 않는다.
    lib_html = ""

    criteria_html = "\n".join(f'          <li>{esc(c)}</li>' for c in step["criteria"])

    # 이 단계에서 만들 것을 줄글 대신 번호 목록으로 보여준다 (todo 가 있는 단계만).
    if step.get("todo"):
        items = LINEBREAK.join(f'        <li>{esc(t)}</li>' for t in step["todo"])
        todo_html = f'<ol class="step-todo">{LINEBREAK}{items}{LINEBREAK}      </ol>'
    else:
        todo_html = "<p class=" + chr(34) + "step-desc" + chr(34) + ">" + esc(step["desc"]) + "</p>"
    intro = SHOT_HTML if step["id"] == "s0" else STEP_SHOTS.get(step["id"], "")

    # todo 중 설명이 필요한 항목을 풀어주는 상자 (note 가 있는 단계만). items 는 HTML 그대로.
    note_html = ""
    if step.get("note"):
        n = step["note"]
        items = LINEBREAK.join(f'        <li>{t}</li>' for t in n["items"])
        note_html = (f'    <div class="workflow-note">{LINEBREAK}'
                     f'      <p class="workflow-note-title">{esc(n["title"])}</p>{LINEBREAK}'
                     f'      <ol>{LINEBREAK}{items}{LINEBREAK}      </ol>{LINEBREAK}    </div>{LINEBREAK}')

    trouble_html = ""
    if step.get("trouble"):
        t = step["trouble"]
        # 왜 그 에러가 나는지 먼저 풀어주는 목록 (있을 때만). items 는 HTML 그대로.
        why_html = ""
        if t.get("visual"):
            why_html = LINEBREAK + "      " + t["visual"]
        if t.get("items"):
            lis = LINEBREAK.join(f'        <li>{x}</li>' for x in t["items"])
            why_html = f'{LINEBREAK}      <ol class="trouble-list">{LINEBREAK}{lis}{LINEBREAK}      </ol>'
        if t.get("flow"):
            why_html += (f'{LINEBREAK}      <p class="trouble-flow-title">인증서는 언제 보나 — 접속할 때, 데이터를 받기 전</p>'
                         f'{LINEBREAK}      <pre class="trouble-flow">{esc(t["flow"])}</pre>')
        trouble_html = f'''
    <details class="answer-details">
      <summary>{esc(t['summary'])}</summary>{why_html}
      <p class="tiny" style="margin-top: 4px;">{t['body']}</p>
      <details class="prompt-box" style="margin-top: 10px;">
        <summary class="prompt-box-head">
          <span class="prompt-label">이어서 넣을 프롬프트 보기</span>
          <span class="prompt-hint">클릭!</span>
          <button class="copy-btn" data-copy="trouble-{step['id']}">복사</button>
        </summary>
        <pre class="prompt-text" id="trouble-{step['id']}">{esc(t['prompt'])}</pre>
      </details>
    </details>'''

    return f'''
  <section class="page" data-page="{step['id']}" id="{step['id']}">
    <div class="page-head">
      <span class="page-eyebrow">{PART_LABELS[step['part']]}</span>
      <div class="page-title-row">
        <h2>STEP {step['num']} · {esc(step['title'])}</h2>
        {"" if showcase else '<span class="step-time">' + esc(step['time']) + '</span>'}
      </div>
      {todo_html}
    </div>
{note_html}{step.get("visual", "")}{intro}{lib_html}
    <details class="prompt-box">
      <summary class="prompt-box-head">
        <span class="prompt-label">{"이렇게 만들려면 — 프롬프트 보기" if showcase else "모범 프롬프트 보기"}</span>
        <span class="prompt-hint">클릭!</span>
        <button class="copy-btn" data-copy="prompt-{step['id']}">복사</button>
      </summary>
      <pre class="prompt-text" id="prompt-{step['id']}">{esc(step['prompt'])}</pre>
    </details>

{"" if showcase else CRITERIA_TMPL.format(criteria_html)}
{trouble_html}
{"" if showcase else DOWNLOAD_TMPL.format(num=step['num'], file=STAGE_FILE_NAMES[step['id']])}
  </section>'''


step_pages_html = "\n".join(render_step_page(s, i, len(STEPS)) for i, s in enumerate(STEPS))

# ── TOC ──────────────────────────────────────────────────
TOC_LABELS = {
    "s0": "뼈대", "s1": "구글 뉴스", "s2": "DART",
    "s3": "HTML 보고서", "s4": "아웃룩 발송", "s5": "통합 실행",
    "s6": "목적별 수집", "s7": "스코어링", "s8": "보고서 고도화",
}

toc_part1 = "\n".join(
    f'      <a class="toc-link" data-page="{s["id"]}" href="#{s["id"]}"><span class="toc-badge">{s["num"]}</span>{TOC_LABELS[s["id"]]}</a>'
    for s in STEPS if s["part"] == 1
)
toc_part2 = "\n".join(
    f'      <a class="toc-link" data-page="{s["id"]}" href="#{s["id"]}"><span class="toc-badge">{s["num"]}</span>{TOC_LABELS[s["id"]]}</a>'
    for s in STEPS if s["part"] == 2
)
toc_part3 = "\n".join(
    f'      <a class="toc-link" data-page="{s["id"]}" href="#{s["id"]}"><span class="toc-badge">{s["num"]}</span>{TOC_LABELS[s["id"]]}</a>'
    for s in STEPS if s["part"] == 3
)
toc_part4 = "\n".join(
    f'      <a class="toc-link" data-page="{s["id"]}" href="#{s["id"]}"><span class="toc-badge">{s["num"]}</span>{TOC_LABELS[s["id"]]}</a>'
    for s in STEPS if s["part"] == 4
)

ALL_PAGE_IDS = ["intro", "prep"] + [s["id"] for s in STEPS] + ["apis", "apps"]
# 알파 실습 맨 앞에 실전 사례 한 장 — STEP 6 바로 앞
ALL_PAGE_IDS.insert(ALL_PAGE_IDS.index("s6"), "case")

# ── 알파 실습 · 실전 사례 ──────────────────────────────────
# 영업팀 과제로 실제로 만든 수주레이더. 고도화 STEP 6~8 이 어디로 가는지 먼저 보여준다.
CASE_URL = "https://hong-seok-young.github.io/xicna-sujoo-radar/"
CASE_PROMPT = """이 수주 레이더를 내 PC 없이 매주 자동으로 돌게 해줘. GitHub 에 올려서 쓸 거야.

1. GitHub Actions 로 두 가지 예약 실행
   - 매일 06:00(한국 시간) — 뉴스 RSS 만 받아서 쌓기
   - 금요일 06:40 — 7일치로 보고서 만들고 영업팀에 메일. 안 되면 07:40, 09:40 에 한 번씩 다시
2. 매일 모은 뉴스는 Actions 캐시로 다음 실행에 넘기기 (금요일 작업이 7일치를 쓰게)
3. 보내기 전에 오늘 이미 보냈는지 확인 — 다시 시도할 때 두 번 가지 않게
4. 보고서가 너무 작거나(20KB 미만) 핵심 칸이 빠졌으면 실패로 처리
5. 보고서는 GitHub Pages 에 올리고, 날짜별로 따로 보관 + 지난 보고서 목록 페이지
6. 영업팀 메일 — 본문은 짧게, 웹 링크와 보고서 파일 첨부
7. 실패하거나 일부 출처만 실패했으면 담당자에게만 알림. 금요일 11:00 까지 안 나갔으면 그것도 알림
8. 인증키와 메일 비밀번호는 GitHub Secrets 에만 — 코드와 저장소에는 절대 넣지 않기"""
CASE_PAGE = f'''
  <section class="page" data-page="case" id="case">
    <div class="page-head">
      <span class="page-eyebrow">알파 실습 · 고도화</span>
      <div class="page-title-row">
        <h2>실전 사례 — 자이씨앤에이 수주레이더</h2>
      </div>
      <p class="step-desc">영업팀 과제로 <strong>실제로 만든 결과물</strong>이다. 이어지는 STEP 6~8 이
        이런 모습으로 가는 길이다.</p>
    </div>

    <a class="case-go" href="{CASE_URL}" target="_blank" rel="noopener">
      <span><b>수주레이더 열어보기</b><small>{CASE_URL}</small></span>
      <span class="case-go-arrow">→</span>
    </a>

<p class="v-title">기본 실습에서 실전 사례까지 — 네 덩어리</p><div class="xf-pipe"><div><b>① 수집</b><small>출처 4종 · 매체 44개</small><em>STEP 6</em></div><div><b>② 거르기 · 점수</b><small>100점 · S/A 등급</small><em>STEP 7</em></div><div><b>③ 보고서</b><small>영업 우선순위 한 장</small><em>STEP 8</em></div><div class="auto"><b>④ 자동화</b><small>PC 없이 매주 발송</small><em>아래</em></div></div>
    <div class="xf"><p class="xf-title"><span class="xf-badge">실전 사례에서는</span>PC 를 켜지 않아도 매주 금요일 아침에 나간다</p><div class="xf-cmp"><div class="xf-side"><span>기본 실습 · 우리가 만든 것</span>내 PC 에서 버튼을 눌러야 돈다 · 아웃룩으로 발송</div><div class="xf-arrow">→</div><div class="xf-side real"><span>실전 사례 · 수주레이더</span>GitHub 서버가 정해진 시각에 알아서 실행 · 웹 페이지 갱신 · 메일 발송</div></div><p class="xf-h">과정 — 실제 워크플로 흐름</p><figure class="dg"><div class="dg-scroll"><svg viewBox="0 0 960 360" role="img" aria-label="매일 수집 워크플로와 금요일 발송 워크플로가 캐시로 이어지는 자동화 흐름"><defs><marker id="mk-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk " d="M0,0 L10,5 L0,10 z"/></marker><marker id="mk-a-k" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk k" d="M0,0 L10,5 L0,10 z"/></marker><marker id="mk-a-drop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk drop" d="M0,0 L10,5 L0,10 z"/></marker></defs><rect class="lane" x="8" y="10" width="944" height="120" rx="10"/><text class="lane-t" x="20" y="28">매일 06:00 — GitHub 서버가 알아서 실행</text><rect class="bx " x="24" y="44" width="136" height="54" rx="7"/><text class="h " x="92" y="67.5" text-anchor="middle">뉴스 보관함 꺼내기</text><text class="s" x="92" y="82.5" text-anchor="middle">어제까지 모은 것</text><rect class="bx " x="177" y="44" width="136" height="54" rx="7"/><text class="h " x="245" y="67.5" text-anchor="middle">새 뉴스 받기</text><text class="s" x="245" y="82.5" text-anchor="middle">언론사 44곳</text><polyline class="ln " points="160,71 173,71" marker-end="url(#mk-a)"/><rect class="bx " x="330" y="44" width="136" height="54" rx="7"/><text class="h " x="398" y="67.5" text-anchor="middle">보관함에 더하기</text><text class="s" x="398" y="82.5" text-anchor="middle">10일치까지</text><polyline class="ln " points="313,71 326,71" marker-end="url(#mk-a)"/><rect class="bx out" x="483" y="44" width="136" height="54" rx="7"/><text class="h " x="551" y="67.5" text-anchor="middle">보관함 넣어두기</text><text class="s" x="551" y="82.5" text-anchor="middle">다음 날 · 금요일용</text><polyline class="ln " points="466,71 479,71" marker-end="url(#mk-a)"/><rect class="bx " x="636" y="44" width="136" height="54" rx="7"/><text class="h " x="704" y="67.5" text-anchor="middle">금 11:00 감시</text><text class="s" x="704" y="82.5" text-anchor="middle">발송 성공했나?</text><rect class="bx drop" x="789" y="44" width="136" height="54" rx="7"/><text class="h " x="857" y="67.5" text-anchor="middle">담당자에게 알림</text><text class="s" x="857" y="82.5" text-anchor="middle">안 나갔으면</text><polyline class="ln drop" points="772,71 785,71" marker-end="url(#mk-a-drop)"/><rect class="lane" x="8" y="150" width="944" height="200" rx="10"/><text class="lane-t" x="20" y="168">금요일 06:40 — 안 되면 07:40 · 09:40 에 다시</text><rect class="bx " x="24" y="186" width="136" height="58" rx="7"/><text class="h " x="92" y="211.5" text-anchor="middle">오늘 이미 보냈나?</text><text class="s" x="92" y="226.5" text-anchor="middle">두 번 보내지 않게</text><rect class="bx " x="177" y="186" width="136" height="58" rx="7"/><text class="h " x="245" y="211.5" text-anchor="middle">모으기 · 점수 · 보고서</text><text class="s" x="245" y="226.5" text-anchor="middle">STEP 6~8 전부</text><polyline class="ln " points="160,215 173,215" marker-end="url(#mk-a)"/><rect class="bx " x="330" y="186" width="136" height="58" rx="7"/><text class="h " x="398" y="211.5" text-anchor="middle">보고서 점검</text><text class="s" x="398" y="226.5" text-anchor="middle">너무 짧으면 실패 처리</text><polyline class="ln " points="313,215 326,215" marker-end="url(#mk-a)"/><rect class="bx out" x="483" y="186" width="136" height="58" rx="7"/><text class="h " x="551" y="211.5" text-anchor="middle">웹 페이지에 올리기</text><text class="s" x="551" y="226.5" text-anchor="middle">지난 보고서 모음에도</text><polyline class="ln " points="466,215 479,215" marker-end="url(#mk-a)"/><rect class="bx k" x="636" y="186" width="136" height="58" rx="7"/><text class="h " x="704" y="211.5" text-anchor="middle">영업팀 메일</text><text class="s" x="704" y="226.5" text-anchor="middle">링크 + 보고서 첨부</text><polyline class="ln " points="619,215 632,215" marker-end="url(#mk-a)"/><rect class="bx " x="789" y="186" width="136" height="58" rx="7"/><text class="h " x="857" y="211.5" text-anchor="middle">올린 내용 저장</text><text class="s" x="857" y="226.5" text-anchor="middle">안 되면 3번까지 다시</text><polyline class="ln " points="772,215 785,215" marker-end="url(#mk-a)"/><polyline class="ln " points="551,98 551,140 245,140 245,182" marker-end="url(#mk-a)"/><text class="al " x="398" y="135" text-anchor="middle">모아둔 7일치 뉴스를 넘김</text><polyline class="ln " points="704,186 704,102" marker-end="url(#mk-a)"/><text class="al" x="712" y="160" text-anchor="start">보냈는지 확인</text><polyline class="ln drop" points="92,244 92,282" marker-end="url(#mk-a-drop)"/><rect class="bx drop" x="24" y="286" width="136" height="46" rx="7"/><text class="h " x="92" y="313.0" text-anchor="middle">보냈으면 건너뜀</text><polyline class="ln drop" points="398,244 398,282" marker-end="url(#mk-a-drop)"/><rect class="bx drop" x="330" y="286" width="136" height="46" rx="7"/><text class="h " x="398" y="305.5" text-anchor="middle">실패하면</text><text class="s" x="398" y="320.5" text-anchor="middle">담당자에게만 알림</text><text class="note" x="704" y="300" text-anchor="middle">인증키는 GitHub 비밀 보관함에만</text><text class="note" x="704" y="318" text-anchor="middle">프로그램 안에는 없다</text></svg></div><figcaption>PC 를 켜둘 필요가 없다. 매일 모은 뉴스는 보관함에 쌓였다가 금요일 작업으로 넘어가고, 중복 발송과 미발송은 앞뒤에서 한 번씩 확인한다.</figcaption></figure><div class="xf-nums"><div class="xf-num"><b>매일</b><small>06:00 수집</small></div><div class="xf-num"><b>금요일</b><small>06:40 발송</small></div><div class="xf-num"><b>3번</b><small>발송 시도 06:40 · 07:40 · 09:40</small></div><div class="xf-num"><b>0대</b><small>켜둘 PC</small></div></div></div>
    <details class="prompt-box">
      <summary class="prompt-box-head">
        <span class="prompt-label">이렇게 만들려면 — 프롬프트 보기</span>
        <span class="prompt-hint">클릭!</span>
        <button class="copy-btn" data-copy="prompt-case">복사</button>
      </summary>
      <pre class="prompt-text" id="prompt-case">{esc(CASE_PROMPT)}</pre>
    </details>
  </section>'''
MAIN_PY_URL = "https://github.com/hong-seok-young/vibe-coding-education/blob/claude/vibe-coding-education-program-lgtqes/news-report-bot/main.py"
ZIP_URL = "https://github.com/hong-seok-young/vibe-coding-education/archive/refs/heads/claude/vibe-coding-education-program-lgtqes.zip"

# "정답 코드 파일 받기" 버튼용 — 완성본 main.py 를 base64 로 페이지에 박아 넣고
# 버튼 클릭 시 Blob 으로 풀어서 다운로드시킨다. 이 방식(HTML smuggling과 같은 패턴)이
# 회사 보안 소프트웨어에 막힐 수 있다는 걸 알고도, 사용자가 위험을 감수하고 요청해서 반영함.
import base64

# 단계마다 "그 단계까지 만든 상태" 파일을 따로 싣는다. 완성본 하나만 싣고 매 단계
# 내려주면 STEP 0 에서 이미 다 된 프로그램을 받게 되어 실습이 사라진다.
# 파일은 tools/make_stage_files.py 가 main.py 에서 만들어낸다.
STAGE_B64 = {}
for _s in range(6):          # 기본 실습 0~5 — 알파 실습은 사례 설명만이라 받을 파일이 없다
    with open(f"{REPO}/news-report-bot/단계별/STEP{_s}.py", "rb") as _f:
        STAGE_B64[_s] = base64.b64encode(_f.read()).decode("ascii")
STAGE_B64_JS = "{" + ",".join('"%d":"%s"' % (k, v) for k, v in STAGE_B64.items()) + "}"

# 크롬 탭 아이콘. 별도 파일을 두면 HTML 만 옮겼을 때 아이콘이 깨지므로
# SVG 를 주소 안에 그대로 적어 넣는다 (파일 하나로 다닐 수 있게).
_Q = chr(39)          # 작은따옴표. SVG 안에 큰따옴표를 쓰므로 바깥은 이걸로 감싼다
FAVICON = (
    '<link rel="icon" href=' + _Q + 'data:image/svg+xml,'
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="14" fill="%23c96a1a"/>'
    '<rect x="14" y="15" width="30" height="34" rx="3" fill="%23fff"/>'
    '<rect x="19" y="21" width="20" height="5" fill="%23c96a1a"/>'
    '<rect x="19" y="30" width="20" height="3" fill="%23e0b18c"/>'
    '<rect x="19" y="37" width="13" height="3" fill="%23e0b18c"/>'
    '<path d="M46 31h5a3 3 0 0 1 3 3v11a3 3 0 0 1-3 3H31" fill="none" '
    'stroke="%23fff" stroke-width="4" stroke-linecap="round"/>'
    '</svg>' + _Q + '>'
)

fonts_head = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
      media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap"></noscript>'''

STYLE = '''<style>
  :root {
    --paper: #eef0ee;
    --surface: #ffffff;
    --surface-2: #e6e9e6;
    --ink: #1c2321;
    --ink-soft: #454e4b;
    --muted: #6b7570;
    --line: #d5d9d4;
    --line-strong: #b9c0ba;
    --accent: #c96a1a;
    --accent-ink: #ffffff;
    --accent-wash: #fbe9d7;
    --good: #3f7a52;
    --good-wash: #e3f0e6;
    --bad: #b3452f;
    --bad-wash: #f8e6e1;
    --focus: #2f6fb0;
    --shadow: 0 1px 2px rgba(20, 24, 22, 0.06), 0 6px 20px -8px rgba(20, 24, 22, 0.12);
    --toc-w: 250px;
  }

  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper: #14181a;
      --surface: #1b2022;
      --surface-2: #222829;
      --ink: #e9ece9;
      --ink-soft: #c2c9c4;
      --muted: #92a09a;
      --line: #2c3436;
      --line-strong: #3a4345;
      --accent: #e69a4e;
      --accent-ink: #201002;
      --accent-wash: #3a2712;
      --good: #7ec293;
      --good-wash: #1c2c20;
      --bad: #e8836d;
      --bad-wash: #34201b;
      --focus: #7db3e8;
      --shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 10px 28px -10px rgba(0, 0, 0, 0.5);
    }
  }

  :root[data-theme="dark"] {
    --paper: #14181a;
    --surface: #1b2022;
    --surface-2: #222829;
    --ink: #e9ece9;
    --ink-soft: #c2c9c4;
    --muted: #92a09a;
    --line: #2c3436;
    --line-strong: #3a4345;
    --accent: #e69a4e;
    --accent-ink: #201002;
    --accent-wash: #3a2712;
    --good: #7ec293;
    --good-wash: #1c2c20;
    --bad: #e8836d;
    --bad-wash: #34201b;
    --focus: #7db3e8;
    --shadow: 0 1px 2px rgba(0, 0, 0, 0.3), 0 10px 28px -10px rgba(0, 0, 0, 0.5);
  }

  * { box-sizing: border-box; }

  body {
    background: var(--paper);
    color: var(--ink);
    font-family: "IBM Plex Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    line-height: 1.6;
  }

  code, .mono {
    font-family: "IBM Plex Mono", ui-monospace, monospace;
  }

  /* ── 플로팅 목차 ── */

  .toc-toggle {
    display: none;
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 30;
    width: 40px;
    height: 40px;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    border: 1px solid var(--line-strong);
    background: var(--surface);
    color: var(--ink);
    box-shadow: var(--shadow);
    cursor: pointer;
    font-size: 16px;
  }

  .toc-toggle:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }

  .toc-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(10, 12, 11, 0.4);
    z-index: 24;
  }

  .toc {
    position: fixed;
    top: 0;
    left: 0;
    width: var(--toc-w);
    height: 100vh;
    overflow-y: auto;
    background: var(--surface);
    border-right: 1px solid var(--line);
    padding: 22px 14px 30px;
    z-index: 25;
  }

  .toc-brand {
    font-size: 13px;
    font-weight: 700;
    color: var(--ink);
    padding: 0 10px;
    margin-bottom: 4px;
  }

  .toc-close {
    display: none;
    position: absolute;
    top: 14px;
    right: 12px;
    width: 30px;
    height: 30px;
    border-radius: 8px;
    border: 1px solid var(--line);
    background: var(--surface);
    color: var(--muted);
    cursor: pointer;
    font-size: 14px;
  }

  .toc-group-label {
    font-size: 10.5px;
    font-weight: 700;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 14px 10px 4px;
  }

  .toc-link {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 7px 10px;
    border-radius: 8px;
    font-size: 13px;
    color: var(--ink-soft);
    text-decoration: none;
    position: relative;
  }

  .toc-link:hover { background: var(--surface-2); color: var(--ink); }

  .toc-link:focus-visible { outline: 2px solid var(--focus); outline-offset: -2px; }

  .toc-link.current {
    background: var(--accent-wash);
    color: var(--accent);
    font-weight: 600;
  }

  .toc-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 999px;
    border: 1.5px solid var(--line-strong);
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 10.5px;
    font-weight: 600;
    color: var(--muted);
    flex-shrink: 0;
  }

  .toc-link.done .toc-badge {
    background: var(--good);
    border-color: var(--good);
    color: #fff;
  }

  .toc-link.done .toc-badge::before { content: "✓"; }
  .toc-link.done .toc-badge > * { display: none; }

  @media (max-width: 900px) {
    .toc-toggle { display: flex; }
    .toc-backdrop.show { display: block; }
    .toc {
      transform: translateX(-100%);
      transition: transform 0.2s ease;
      box-shadow: var(--shadow);
    }
    .toc.open { transform: translateX(0); }
    .toc-close { display: block; }
    .content-outer { margin-left: 0 !important; }
  }

  @media (prefers-reduced-motion: reduce) {
    .toc { transition: none; }
  }

  /* ── 본문 레이아웃 ── */

  .content-outer {
    margin-left: var(--toc-w);
    min-height: 100vh;
  }

  .wrap {
    max-width: 720px;
    margin: 0 auto;
    padding: 40px 24px 90px;
  }

  h1 {
    font-size: clamp(24px, 4vw, 30px);
    font-weight: 700;
    margin: 0 0 8px;
    letter-spacing: -0.01em;
    text-wrap: balance;
  }

  h2 {
    font-size: 20px;
    font-weight: 700;
    margin: 0;
    text-wrap: balance;
  }

  .lede {
    color: var(--ink-soft);
    font-size: 15px;
    max-width: 62ch;
    margin: 0 0 20px;
  }

  .lede strong { color: var(--ink); }

  @media (prefers-reduced-motion: reduce) {
  }

  /* ── 페이지 전환 ── */

  .page { display: none; }
  .page.active { display: block; animation: fadeIn 0.15s ease; }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @media (prefers-reduced-motion: reduce) {
    .page.active { animation: none; }
  }

  /* prep 페이지 내부 (기존 체크리스트 스타일) */

  section.group { margin-bottom: 0; }

  .group-head { display: flex; align-items: baseline; gap: 10px; margin-bottom: 4px; }

  .group-head .num {
    font-size: 13px;
    font-weight: 600;
    color: var(--accent);
    background: var(--accent-wash);
    border-radius: 6px;
    padding: 2px 8px;
  }

  .group-head h2 { font-size: 17px; }

  .group-sub { color: var(--muted); font-size: 13.5px; margin: 0 0 14px 0; }

  .page-inner > section.group { margin-bottom: 30px; }

  .items { display: flex; flex-direction: column; gap: 10px; }

  .item {
    display: grid;
    grid-template-columns: 28px 1fr;
    gap: 14px;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 14px 16px;
    transition: border-color 0.15s ease, background 0.15s ease;
  }

  /* 체크할 게 없는 설명 카드 (사전 준비 D) */
  .item.item-info { grid-template-columns: 1fr; }

  .item:has(.check:checked) { border-color: var(--good); background: var(--good-wash); }

  @media (prefers-reduced-motion: reduce) { .item { transition: none; } }

  .check-col { display: flex; justify-content: center; padding-top: 2px; }

  .check {
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 1.5px solid var(--line-strong);
    background: var(--surface);
    cursor: pointer;
    display: grid;
    place-content: center;
    flex-shrink: 0;
  }

  .check:focus-visible {
    outline: 2px solid var(--focus);
    outline-offset: 2px;
  }

  .check::after {
    content: "";
    width: 10px;
    height: 6px;
    border-left: 2px solid var(--accent-ink);
    border-bottom: 2px solid var(--accent-ink);
    transform: rotate(-45deg) translateY(-1px);
    opacity: 0;
  }

  .check:checked { background: var(--good); border-color: var(--good); }
  .check:checked::after { opacity: 1; }

  .item-title {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    font-weight: 600;
    font-size: 15px;
    margin: 0 0 4px;
  }

  .tag {
    font-size: 11px;
    font-weight: 600;
    padding: 1px 7px;
    border-radius: 999px;
    letter-spacing: 0.02em;
  }

  .tag.required { background: var(--accent-wash); color: var(--accent); }
  .tag.free { background: var(--good-wash); color: var(--good); }
  .tag.partial { background: var(--accent-wash); color: var(--accent); }

  .item p { margin: 0 0 8px; font-size: 13.5px; color: var(--ink-soft); }
  .item p:last-child { margin-bottom: 0; }
  .item .warn { color: var(--accent); }

  .actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: inherit;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
    padding: 7px 13px;
    border-radius: 8px;
    border: 1px solid var(--line-strong);
    color: var(--ink);
    background: var(--surface);
    cursor: pointer;
  }

  .btn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .btn.primary { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
  .btn .arrow { font-size: 15px; line-height: 1; }

  .tiny { font-size: 12px; color: var(--muted); margin: 10px 0 0; }

  .item > span:last-child { min-width: 0; }

  /* 사전 준비 · RSS 와 API 비교 (좁은 표라 최소 너비를 풀어준다) */
  /* .apitable 의 min-width: 640px 가 뒤에 와서 이기지 않도록 두 클래스로 지정한다 */
  .apitable.rss-vs-api { min-width: 0; margin-top: 6px; }
  .rss-vs-api td, .rss-vs-api th { font-size: 12.5px; }
  /* RSS vs API 비교표 — 열마다 색을 입혀 좌우 비교가 한눈에 */
  .apitable.rss-vs-api { table-layout: fixed; border-collapse: separate; border-spacing: 6px 0; width: 100%; }
  .rss-vs-api col.c-label { width: 58px; }
  .rss-vs-api thead th { text-align: center; font-size: 13px; font-weight: 700; padding: 8px 6px; border: 0;
                         border-radius: 8px 8px 0 0; letter-spacing: 0.04em; }
  .rss-vs-api thead th.c-rss { background: var(--good); color: var(--surface); }
  .rss-vs-api thead th.c-api { background: var(--accent); color: var(--accent-ink); }
  .rss-vs-api tbody th { text-align: left; font-weight: 700; color: var(--ink); padding: 9px 4px; border-bottom: 1px solid var(--line); }
  .rss-vs-api tbody td { text-align: center; padding: 9px 8px; color: var(--ink); border-bottom: 1px solid rgba(0, 0, 0, 0.06); line-height: 1.45; }
  .rss-vs-api tbody td.c-rss { background: var(--good-wash); }
  .rss-vs-api tbody td.c-api { background: var(--accent-wash); }
  .rss-vs-api tbody tr:last-child td { border-bottom: 0; border-radius: 0 0 8px 8px; }
  .rss-vs-api tbody tr:last-child th { border-bottom: 0; }
  .rss-vs-api td small { display: block; font-size: 11px; color: var(--muted); }

  /* 사전 준비 · 뉴스 소스 목록 */
  .news-sources { margin: 4px 0 0; padding-left: 18px; font-size: 13px; color: var(--ink-soft); line-height: 1.75; }
  .news-sources li { margin-bottom: 3px; }
  .news-sources a { color: var(--accent); }

  /* STEP 0 의 완성 창 그림 */
  .shot { margin: 14px 0 6px; }
  .shot.tall { max-width: 560px; margin-left: auto; margin-right: auto; }
  .shot figcaption { margin-top: 6px; font-size: 12px; color: var(--muted); text-align: center; }
  .shot img {
    display: block; width: 100%; height: auto; background: #fff;
    border: 1px solid var(--line-strong); border-radius: 6px; box-shadow: var(--shadow);
  }

  /* API 목록 표 — 좁은 화면에서는 표 자체만 가로 스크롤된다 */
  .apitable-wrap { overflow-x: auto; margin-top: 10px; -webkit-overflow-scrolling: touch; }
  .apitable { width: 100%; min-width: 640px; border-collapse: collapse; font-size: 13px; }
  .apitable th, .apitable td {
    text-align: left; padding: 9px 12px 9px 0; vertical-align: top;
    border-bottom: 1px solid var(--line);
  }
  .apitable thead th {
    color: var(--muted); font-weight: 600; font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.04em;
    border-bottom: 1px solid var(--line-strong); white-space: nowrap;
  }
  .apitable tbody tr:last-child td { border-bottom: none; }
  .apitable .api-name { font-weight: 600; color: var(--ink); white-space: nowrap; }
  .apitable .api-sub { display: block; color: var(--muted); font-size: 11px; font-weight: 400; }
  .apitable .api-quota { color: var(--muted); white-space: nowrap; }
  .apitable .api-quota .tag { margin: 0 0 3px; }
  .apitable .tag.free { background: var(--surface); border: 1px solid var(--good); }
  .apitable .api-pick { color: var(--accent); font-weight: 600; }
  /* 한 줄짜리 목록 표 */
  .apitable.compact { min-width: 600px; }
  .apitable.compact td { padding: 6px 10px; white-space: nowrap; vertical-align: middle; }
  .apitable.compact td.api-use { white-space: normal; color: var(--ink-soft); }
  .apitable.compact .api-name a { color: inherit; text-decoration: none; border-bottom: 1px dashed currentColor; }
  .apitable.compact .api-name a:hover { color: var(--accent); border-bottom-style: solid; }
  .apitable.compact .api-fee .tag { margin: 0; }
  .apitable.compact tr.api-cat td { padding: 14px 10px 5px; font-size: 11.5px; font-weight: 700;
                                    color: var(--good); letter-spacing: 0.03em; border-bottom: 1px solid var(--good); }
  .apitable.compact tbody tr.api-cat:first-child td { padding-top: 6px; }
  .filetable { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
  .filetable th, .filetable td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); }
  .filetable th { color: var(--muted); font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; }
  .filetable td:last-child, .filetable th:last-child { text-align: right; }

  .install-details { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--line); }
  .install-details summary { cursor: pointer; font-size: 13px; font-weight: 600; color: var(--ink-soft); }
  .install-details summary:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .install-details[open] summary { color: var(--ink); margin-bottom: 8px; }

  /* 번호가 보이도록 flex 를 쓰지 않는다 — flex 자식이 되면 li 의 번호 표식이 사라진다 */
  .install-list { margin: 0; padding-left: 20px; font-size: 13px; color: var(--ink-soft); line-height: 1.75; }
  .install-list li { margin-bottom: 4px; }
  .trouble-list { margin: 0 0 10px; padding-left: 20px; font-size: 13px; color: var(--ink-soft); line-height: 1.75; }
  .trouble-list li { margin-bottom: 4px; }
  .trouble-list li::marker { color: var(--accent); font-weight: 600; }
  .trouble-list strong { color: var(--ink); }
  .trouble-flow-title { font-size: 13px; font-weight: 700; color: var(--ink); margin: 4px 0 6px; }
  .trouble-flow { margin: 0 0 12px; padding: 12px 14px; background: var(--surface); border: 1px solid var(--line);
                  border-radius: 8px; font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 12.5px;
                  line-height: 1.7; color: var(--ink-soft); white-space: pre; overflow-x: auto; }
  .install-list li::marker { color: var(--accent); font-weight: 600; }
  .install-list strong { color: var(--ink); font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 0.95em; }
  .prep-fallback { margin-top: 12px; }
  .prep-fallback > summary { cursor: pointer; }
  .prep-fallback > summary strong { color: var(--ink); }

  .kv { display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; font-size: 13px; margin-top: 8px; }
  .kv dt { color: var(--muted); }
  .kv dd { margin: 0; }

  code {
    background: var(--surface-2);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 0.92em;
  }

  /* 쳐 넣는 명령어 조각만 눌러서 복사된다. 파일 이름·화면 문구 같은 건 해당 없다 */
  code.cmd, code.cmd-text {
    cursor: pointer;
    border: 1px solid transparent;
    transition: background 0.15s ease, border-color 0.15s ease;
  }

  code.cmd:hover, code.cmd-text:hover { background: var(--accent-wash); border-color: var(--accent); }

  code.copied {
    background: var(--good-wash);
    border-color: var(--good);
    color: var(--good);
  }

  code.copied::after { content: " 복사됨"; font-size: 0.85em; font-weight: 600; }

  .callout {
    background: var(--surface);
    border: 1px solid var(--line);
    border-left: 3px solid var(--accent);
    border-radius: 0 12px 12px 0;
    padding: 16px 18px;
    font-size: 13.5px;
    color: var(--ink-soft);
    margin-top: 22px;
  }

  .callout strong { color: var(--ink); }
  .callout a { color: var(--accent); }

  /* ── 실습 STEP 페이지 ── */

  .page-head { margin-bottom: 18px; }

  .page-eyebrow {
    display: block;
    font-size: 11.5px;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
  }

  .page-title-row {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 8px;
  }


  .page-title-row h2 { flex: 1; min-width: 160px; }

  .step-time {
    font-size: 12px;
    color: var(--muted);
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    flex-shrink: 0;
  }

  .step-desc { font-size: 14px; color: var(--ink-soft); margin: 0; }

  .cmd-box {
    display: flex;
    align-items: center;
    gap: 10px;
    background: var(--surface-2);
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 14px;
    font-size: 12.5px;
    flex-wrap: wrap;
  }

  .cmd-label { color: var(--muted); flex-shrink: 0; }
  .cmd-text { font-family: "IBM Plex Mono", ui-monospace, monospace; color: var(--ink); flex: 1; min-width: 140px; }

  .prompt-box { border: 1px solid var(--accent); border-radius: 10px; overflow: hidden; margin-bottom: 16px; }
  .prompt-box > summary { cursor: pointer; list-style: none; }
  .prompt-box > summary::-webkit-details-marker { display: none; }
  /* 접혀 있으면 눈에 띄어야 한다 — 이걸 못 찾으면 실습이 시작되지 않는다 */
  .prompt-box > summary { background: var(--accent-wash); color: var(--accent); }
  .prompt-box > summary:hover { filter: brightness(0.97); }
  .prompt-box > summary .prompt-label { color: var(--accent); font-size: 13.5px; }
  .prompt-box > summary .prompt-label::before {
    content: "▸"; display: inline-block; margin-right: 6px;
  }
  .prompt-box[open] > summary .prompt-label::before { content: "▾"; }
  .prompt-hint {
    margin-right: auto; padding: 2px 8px; border-radius: 999px;
    background: var(--accent); color: var(--accent-ink);
    font-size: 11px; font-weight: 700; letter-spacing: 0.02em;
    animation: hintPulse 1.8s ease-in-out infinite;
  }
  .prompt-box[open] .prompt-hint { display: none; }
  @keyframes hintPulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.45; } }
  @media (prefers-reduced-motion: reduce) { .prompt-hint { animation: none; } }

  .prompt-box-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    background: var(--surface-2);
    padding: 9px 14px;
    font-size: 12px;
    font-weight: 600;
    color: var(--ink-soft);
  }

  .prompt-text {
    margin: 0;
    padding: 16px;
    /* 본문과 같은 글꼴 — 고정폭·손글씨보다 읽기 쉽다 */
    font-family: "IBM Plex Sans KR", sans-serif;
    font-size: 14px;
    line-height: 1.75;
    white-space: pre-wrap;
    word-break: break-word;
    color: var(--ink);
  }

  .copy-btn {
    font-size: 11.5px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 6px;
    border: 1px solid var(--line-strong);
    background: var(--surface);
    color: var(--ink-soft);
    cursor: pointer;
    flex-shrink: 0;
  }

  .copy-btn:hover { color: var(--ink); }
  .copy-btn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .copy-btn.copied { color: var(--good); border-color: var(--good); }

  .workflow-note {
    background: var(--accent-wash);
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 18px;
  }

  .workflow-note-title {
    font-size: 13.5px;
    font-weight: 700;
    color: var(--ink);
    margin: 0 0 8px;
  }

  .workflow-note ol {
    margin: 0;
    padding-left: 20px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .workflow-note li { font-size: 13px; color: var(--ink-soft); }
  .workflow-note strong { color: var(--ink); }
  .workflow-note code { background: var(--surface); }

  /* ── STEP 2 두 가지 방법 ── */
  .ways { margin: 14px 0 6px; padding: 14px; border-radius: 10px; background: var(--paper); border: 1px solid var(--line); }
  .ways-title { margin: 0 0 10px; font-size: 14px; font-weight: 700; color: var(--ink); }
  .cert-lane.alt { border-color: var(--accent); background: var(--accent-wash); }
  .cert-lane.alt .cert-end { border-color: var(--accent); color: var(--accent); font-weight: 700; }
  .ways .cert-end small { font-family: inherit; }
  .ways-tag { display: inline-block; margin-left: 4px; padding: 1px 7px; border-radius: 999px; font-size: 10.5px;
              font-weight: 700; background: var(--good); color: var(--surface); vertical-align: 1px; }
  .ways-tag.alt { background: var(--accent); color: var(--accent-ink); }
  .ways-pros { list-style: none; margin: 10px 0 0; padding: 0; display: flex; flex-direction: column; gap: 3px; text-align: left; }
  .ways-pros li { font-size: 12px; color: var(--ink-soft); padding-left: 16px; position: relative; }
  .ways-pros li.up::before { content: "✓"; position: absolute; left: 0; color: var(--good); font-weight: 700; }
  .ways-pros li.down::before { content: "✕"; position: absolute; left: 0; color: var(--bad); font-weight: 700; }
  .ways-note { margin: 10px 0 0 !important; }
  a.cert-box.corp-card { display: block; margin: 0; text-align: center; text-decoration: none; cursor: pointer; border: 1.5px dashed var(--accent);
                         transition: background 0.15s ease; }
  a.cert-box.corp-card:hover { background: var(--accent-wash); border-style: solid; }
  .corp-dl-icon { display: inline-grid; place-items: center; width: 18px; height: 18px; margin-left: 3px; border-radius: 50%;
                  background: var(--accent); color: var(--accent-ink); font-size: 11px; vertical-align: 1px; }
  .cert-box small.corp-dl-hint { margin-top: 2px; font-size: 10.5px; }

  /* ── STEP 1 인증서 오류 그림 ── */
  .cert { margin: 4px 0 12px; padding: 14px; border-radius: 10px; background: var(--paper); border: 1px solid var(--line); }
  .cert-path { display: flex; align-items: center; gap: 4px; margin-bottom: 14px; }
  .cert-path .pv-line { margin-top: 12px; }
  .cert-lanes { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .cert-lane { display: flex; flex-direction: column; align-items: stretch; gap: 0; padding: 10px; border-radius: 10px; border: 1.5px solid; }
  .cert-lane.bad { border-color: var(--bad); background: var(--bad-wash); }
  .cert-lane.good { border-color: var(--good); background: var(--good-wash); }
  .cert-lane p { margin: 0; text-align: center; }
  .cert-who { font-size: 13px; font-weight: 700; margin-bottom: 8px !important; color: var(--ink); }
  .cert-who small { font-weight: 500; color: var(--muted); font-size: 11px; }
  .cert-box { font-size: 12.5px; color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-radius: 7px; padding: 7px 8px; }
  .cert-box small { display: block; font-size: 11px; color: var(--muted); }
  .cert-box + .cert-box { position: relative; margin-top: 16px; }
  .cert-box + .cert-box::before { content: "↓"; position: absolute; top: -16px; left: 0; right: 0; font-size: 12px; line-height: 16px; color: var(--muted); }
  .cert-lane.bad .cert-end { border-color: var(--bad); color: var(--bad); font-weight: 700; }
  .cert-lane.good .cert-end { border-color: var(--good); color: var(--good); font-weight: 700; }
  .cert-end small { font-weight: 500; font-family: "IBM Plex Mono", ui-monospace, monospace; }
  .chip.hl { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); font-weight: 700; }
  .cert-when { margin-top: 14px; }
  .cert-note { margin: 10px 0 0; }
  @media (max-width: 560px) {
    .cert-lanes { grid-template-columns: 1fr; }
    .cert-path .pv-node { min-width: 0; padding: 6px; font-size: 11px; }
  }

  /* ── 사전 준비 D — RSS 란 / API 란 그림 ── */
  .rv { display: grid; grid-template-columns: 1.4fr 1fr; gap: 12px; margin: 10px 0 4px; padding: 14px;
        border-radius: 10px; background: var(--paper); border: 1px solid var(--line); }
  .rv-sheet { background: var(--surface); border: 1px solid var(--line-strong); border-radius: 8px; overflow: hidden; }
  .rv-sheet-cap { font-size: 11px; color: var(--muted); padding: 6px 10px; background: var(--surface-2); border-bottom: 1px solid var(--line); }
  .rv-sheet table { width: 100%; border-collapse: collapse; font-size: 11.5px; }
  .rv-sheet th { background: var(--good-wash); color: var(--good); font-weight: 700; text-align: left; padding: 5px 8px;
                 border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); }
  .rv-sheet td { padding: 5px 8px; color: var(--ink-soft); border-right: 1px solid var(--line); border-bottom: 1px solid var(--line);
                 white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 150px; }
  .rv-sheet tr > :last-child { border-right: 0; }
  .rv-sheet tr:last-child td { border-bottom: 0; }
  .rv-side { display: flex; flex-direction: column; gap: 8px; }
  .rv-badge { flex: 1; padding: 10px 12px; border-radius: 8px; background: var(--surface); border: 1px solid var(--line); }
  .rv-badge b { display: block; font-size: 13px; color: var(--ink); }
  .rv-badge small { display: block; margin-top: 2px; font-size: 11.5px; color: var(--muted); line-height: 1.5; }
  .rv-badge.free { border-color: var(--good); background: var(--good-wash); }
  .rv-badge.free b { color: var(--good); }

  .rv.rv-api { grid-template-columns: 1fr auto auto auto 1fr; align-items: center; gap: 8px; }
  .rv-form, .rv-answer { background: var(--surface); border: 1px solid var(--line-strong); border-radius: 8px; padding: 8px 10px; }
  .rv-form-cap { font-size: 11px; font-weight: 700; color: var(--muted); margin-bottom: 4px; }
  .rv-form p, .rv-answer p { margin: 0; font-size: 12px; color: var(--ink); line-height: 1.7; white-space: nowrap; }
  .rv-form p span { display: inline-block; width: 42px; color: var(--muted); font-size: 11px; }
  .rv-form p.key { color: var(--accent); font-weight: 700; }
  .rv-answer p { overflow: hidden; text-overflow: ellipsis; }
  .rv-arrow { position: relative; font-size: 11px; color: var(--ink-soft); text-align: center; padding-bottom: 8px; min-width: 34px; }
  .rv-arrow i { position: absolute; left: 0; right: 6px; bottom: 0; height: 2px; background: var(--line-strong); }
  .rv-arrow i::after { content: ""; position: absolute; right: -6px; top: -4px; border: 5px solid transparent; border-left-color: var(--line-strong); }
  .rv-window { text-align: center; padding: 10px 12px; border-radius: 10px; background: var(--accent-wash); border: 1.5px solid var(--accent); }
  .rv-window b { display: block; font-size: 14px; color: var(--ink); }
  .rv-window small { display: block; font-size: 11px; color: var(--muted); }
  .rv-window em { display: inline-block; margin-top: 4px; font-style: normal; font-size: 10.5px; font-weight: 700;
                  padding: 2px 6px; border-radius: 999px; background: var(--accent); color: var(--accent-ink); }
  .rv-note { margin-top: 8px !important; }
  @media (max-width: 560px) {
    .rv, .rv.rv-api { grid-template-columns: 1fr; }
    .rv-arrow { padding: 0; min-width: 0; }
    .rv-arrow i { display: none; }
    .rv-arrow::after { content: " ↓"; }
  }

  /* ── 사전 준비 — 그림 ── */
  .pv-map { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 4px 0 22px; }
  .pv-map-item { display: flex; flex-direction: column; align-items: center; gap: 3px; text-align: center;
                 background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 14px 8px; }
  .pv-map-num { width: 30px; height: 30px; border-radius: 50%; display: grid; place-items: center; margin-bottom: 4px;
                background: var(--accent-wash); color: var(--accent); font-weight: 700; font-size: 13px; }
  .pv-map-item strong { font-size: 14px; color: var(--ink); }
  .pv-map-item small { font-size: 12px; color: var(--muted); }
  .pv-map-note { margin: 0 0 22px; font-size: 12.5px; color: var(--muted); text-align: right; }

  .pv-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 10px 0 8px; }
  .pv-steps.four { grid-template-columns: repeat(4, 1fr); }
  .pv-step p { margin: 6px 0 0; font-size: 12.5px; color: var(--ink-soft); text-align: center; line-height: 1.5; }
  .pv-step p b { display: inline-grid; place-items: center; width: 18px; height: 18px; margin-right: 5px; border-radius: 50%;
                 background: var(--accent); color: var(--accent-ink); font-size: 11px; vertical-align: 1px; }
  .pv-step p code { font-size: 11.5px; }
  .pv-step p small { display: block; font-size: 11px; color: var(--muted); }
  .pv-pic { position: relative; height: 84px; border-radius: 8px; background: var(--paper); border: 1px solid var(--line);
            display: grid; place-items: center; overflow: hidden; }

  a.pv-pic.pv-dl { text-decoration: none; cursor: pointer; border: 1.5px dashed var(--accent);
                   transition: background 0.15s ease; }
  a.pv-pic.pv-dl:hover { background: var(--accent-wash); border-style: solid; }
  .pv-dl-hint { position: absolute; right: 8px; bottom: 6px; font-size: 10.5px; font-weight: 700; color: var(--accent); }
  .pv-folder { position: relative; width: 58px; height: 40px; margin-top: 6px; border-radius: 3px 7px 7px 7px;
               background: var(--accent-wash); border: 1.5px solid var(--accent); color: var(--accent);
               display: grid; place-items: center; font-size: 11px; font-weight: 700; }
  .pv-folder::before { content: ""; position: absolute; left: -1.5px; top: -9px; width: 24px; height: 8px;
                       border: 1.5px solid var(--accent); border-bottom: 0; border-radius: 4px 4px 0 0; background: var(--accent-wash); }
  .pv-file { width: 40px; height: 50px; border-radius: 3px 12px 3px 3px; background: var(--surface);
             border: 1.5px solid var(--line-strong); display: grid; place-items: end center; padding-bottom: 6px;
             font-size: 10px; font-weight: 700; color: var(--muted); box-sizing: border-box; }
  .pv-dbl { position: absolute; right: 10px; bottom: 10px; font-size: 10.5px; font-weight: 700; padding: 3px 7px;
            border-radius: 999px; background: var(--accent); color: var(--accent-ink); }
  .pv-term { width: 82%; display: flex; flex-direction: column; gap: 3px; padding: 8px 10px; box-sizing: border-box;
             background: #1c2321; border-radius: 6px; font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 10px; }
  .pv-term i { font-style: normal; color: #aab4ae; }
  .pv-term i.ok { color: #7ec293; font-weight: 700; }

  .pv-browser { width: 86%; height: 62px; display: flex; flex-direction: column; overflow: hidden;
                background: var(--surface); border: 1px solid var(--line-strong); border-radius: 6px; }
  .pv-browser .bar { height: 9px; flex: none; background: var(--surface-2); border-bottom: 1px solid var(--line); }
  .pv-browser .logo { flex: 1; display: grid; place-items: center; font-size: 12px; font-weight: 800; color: #1b6fd0; letter-spacing: 0.02em; }
  .pv-browser .cards { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 3px; padding: 5px; }
  .pv-browser .cards i { border-radius: 3px; background: var(--surface-2); }
  .pv-browser .cards i.hl { background: var(--accent); color: var(--accent-ink); font-style: normal; font-size: 9px;
                            font-weight: 700; display: grid; place-items: center; }
  .pv-browser .form { flex: 1; display: flex; flex-direction: column; gap: 4px; padding: 6px 8px; }
  .pv-browser .form i { height: 5px; border-radius: 3px; background: var(--surface-2); }
  .pv-browser .form em { align-self: flex-end; font-style: normal; font-size: 9px; font-weight: 700; padding: 2px 8px;
                         border-radius: 4px; background: var(--accent); color: var(--accent-ink); }
  .pv-key { display: flex; align-items: center; gap: 6px; }
  .pv-key span { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 11px; padding: 5px 7px; border-radius: 5px;
                 background: var(--surface); border: 1px solid var(--line-strong); color: var(--ink-soft); }
  .pv-key em { font-style: normal; font-size: 10.5px; font-weight: 700; padding: 4px 8px; border-radius: 5px;
               background: var(--accent); color: var(--accent-ink); }

  .pv-flow { display: flex; flex-direction: column; gap: 14px; margin: 8px 0 14px; padding: 14px; border-radius: 10px;
             background: var(--paper); border: 1px solid var(--line); }
  .pv-row { display: flex; align-items: center; gap: 8px; }
  .pv-tag { width: 38px; flex: none; font-size: 11px; font-weight: 800; color: var(--good); }
  .pv-tag.api { color: var(--accent); }
  .pv-node { flex: none; min-width: 74px; padding: 8px 10px; border-radius: 8px; text-align: center; font-size: 12.5px;
             font-weight: 700; color: var(--ink); background: var(--surface); border: 1.5px solid var(--line-strong); }
  .pv-node small { display: block; font-size: 10.5px; font-weight: 500; color: var(--muted); }
  .pv-node.src { border-color: var(--good); background: var(--good-wash); }
  .pv-node.src.api { border-color: var(--accent); background: var(--accent-wash); }
  .pv-lines { flex: 1; display: flex; flex-direction: column; gap: 16px; }
  .pv-line { position: relative; flex: 1; height: 2px; margin: 12px 4px 0; background: var(--line-strong); }
  .pv-lines .pv-line { flex: none; margin-top: 12px; }
  .pv-line em { position: absolute; left: 50%; bottom: 4px; transform: translateX(-50%); white-space: nowrap;
                font-style: normal; font-size: 11px; color: var(--ink-soft); }
  .pv-line.left::before, .pv-line.right::after { content: ""; position: absolute; top: -4px; border: 5px solid transparent; }
  .pv-line.left::before { left: -6px; border-right-color: var(--line-strong); }
  .pv-line.right::after { right: -6px; border-left-color: var(--line-strong); }

  .pv-parcels { display: flex; flex-direction: column; gap: 12px; margin: 10px 0; padding: 14px; border-radius: 10px;
                background: var(--paper); border: 1px solid var(--line); }
  .pv-parcel-row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
  .pv-parcel { position: relative; width: 84px; padding: 16px 8px 7px; border-radius: 6px; text-align: center;
               background: #e9c79a; border: 1.5px solid #b9864a; display: flex; flex-direction: column; gap: 3px; }
  .pv-parcel::before { content: ""; position: absolute; top: 0; left: 50%; width: 12px; height: 100%;
                       transform: translateX(-50%); background: rgba(255, 255, 255, 0.35); }
  .pv-parcel b { position: relative; font-size: 11.5px; color: #4a2f10; }
  .pv-fill { position: relative; display: block; height: 12px; margin: 3px 0; border-radius: 3px;
             background: rgba(255, 255, 255, 0.7); border: 1px solid rgba(0, 0, 0, 0.2); overflow: hidden; }
  .pv-fill em { position: absolute; left: 0; top: 0; bottom: 0; }
  .pv-fill em.p10 { width: 10%; background: #8a5a22; }
  .pv-fill em.p100 { width: 100%; background: #3f63a3; }
  .pv-parcel small.cap { font-size: 10px; opacity: 0.75; }
  .pv-parcel small { position: relative; font-size: 10.5px; color: #4a2f10; }
  .pv-parcel.dart { background: #cfdcf1; border-color: #6d8fc4; }
  .pv-parcel.dart b, .pv-parcel.dart small { color: #1f3a66; }
  .pv-more { font-size: 16px; color: var(--muted); letter-spacing: 2px; }
  .pv-sum { margin-left: 6px; font-size: 13px; color: var(--ink-soft); line-height: 1.4; }
  .pv-sum strong { color: var(--accent); font-size: 14px; }
  .pv-sum small { display: block; font-size: 11.5px; color: var(--muted); }

  @media (max-width: 560px) {
    .pv-map, .pv-steps.four { grid-template-columns: repeat(2, 1fr); }
    .pv-steps { grid-template-columns: 1fr; }
    .pv-node { min-width: 0; padding: 6px; font-size: 11.5px; }
    .pv-tag { width: 28px; }
  }

  /* ── 실전 사례 도식 (SVG) ── */
  /* 도식이 있는 알파 실습 페이지만 본문을 넓힌다 — 960 폭 도식이 글자 크기 그대로 들어가게 */
  .wrap:has(.page.active[data-page="case"]), .wrap:has(.page.active[data-page="s6"]),
  .wrap:has(.page.active[data-page="s7"]), .wrap:has(.page.active[data-page="s8"]) { max-width: 1060px; }
  .dg { margin: 6px 0 4px; }
  .dg-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .dg svg { display: block; width: 100%; min-width: 760px; height: auto; }
  .dg figcaption { margin-top: 6px; font-size: 12px; color: var(--muted); line-height: 1.55; }
  .dg .bx { fill: var(--surface); stroke: var(--line-strong); stroke-width: 1; }
  .dg .bx.k { fill: var(--accent-wash); stroke: var(--accent); stroke-width: 1.6; }
  .dg .bx.out { fill: var(--good-wash); stroke: var(--good); stroke-width: 1.2; }
  .dg .bx.drop { fill: var(--bad-wash); stroke: var(--bad); stroke-dasharray: 4 3; }
  .dg text { fill: var(--ink); font-family: inherit; font-size: 12px; }
  .dg text.h { font-weight: 700; font-size: 12.5px; }
  .dg text.s { fill: var(--muted); font-size: 10.5px; }
  .dg text.col { fill: var(--muted); font-size: 11px; font-weight: 700; letter-spacing: 0.04em; }
  .dg text.al { fill: var(--ink-soft); font-size: 10.5px; }
  .dg text.al.k { fill: var(--accent); }
  .dg text.note { fill: var(--ink-soft); font-size: 11.5px; font-weight: 600; }
  .dg text.lane-t { fill: var(--muted); font-size: 11.5px; font-weight: 700; }
  .dg .lane { fill: none; stroke: var(--line-strong); stroke-dasharray: 3 4; }
  .dg .ln { fill: none; stroke: var(--muted); stroke-width: 1.4; }
  .dg .ln.k { stroke: var(--accent); stroke-width: 1.6; }
  .dg .ln.drop { stroke: var(--bad); stroke-dasharray: 4 3; }
  .dg .mk { fill: var(--muted); } .dg .mk.k { fill: var(--accent); } .dg .mk.drop { fill: var(--bad); }

  /* ── 알파 실습 — 실전 사례 과정·기술 그림 ── */
  .xf { margin: 14px 0 6px; padding: 16px; border-radius: 12px; background: var(--paper); border: 1px solid var(--line); }
  .xf-title { margin: 0 0 12px; font-size: 15px; font-weight: 700; color: var(--ink); }
  .download-stage-btn .dl-name { margin-left: 6px; font-size: 11.5px; font-weight: 500; opacity: 0.85; }
  .xf-badge { display: inline-block; margin-right: 8px; padding: 2px 9px; border-radius: 999px; font-size: 11px;
              background: var(--accent); color: var(--accent-ink); vertical-align: 2px; }
  .xf-cmp { display: grid; grid-template-columns: 1fr auto 1fr; gap: 8px; align-items: stretch; }
  .xf-side { padding: 10px 12px; border-radius: 9px; background: var(--surface); border: 1px solid var(--line);
             font-size: 13px; color: var(--ink-soft); line-height: 1.55; }
  .xf-side span { display: block; font-size: 11px; font-weight: 700; color: var(--muted); margin-bottom: 3px; }
  .xf-side.real { border: 1.5px solid var(--accent); background: var(--accent-wash); color: var(--ink); }
  .xf-side.real span { color: var(--accent); }
  .xf-arrow { align-self: center; font-size: 20px; color: var(--accent); font-weight: 700; }
  .xf-h { margin: 16px 0 8px; font-size: 12.5px; font-weight: 700; color: var(--ink); }
  .xf-flow { list-style: none; counter-reset: xf; margin: 0; padding: 0; display: grid;
             grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .xf-flow li { counter-increment: xf; position: relative; padding: 10px 10px 10px 36px; border-radius: 9px;
                background: var(--surface); border: 1px solid var(--line); font-size: 12.5px; color: var(--ink); line-height: 1.5; }
  .xf-flow li::before { content: counter(xf); position: absolute; left: 10px; top: 10px; width: 18px; height: 18px;
                        border-radius: 50%; display: grid; place-items: center; font-size: 11px; font-weight: 700;
                        background: var(--accent); color: var(--accent-ink); }
  .xf-chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .xf-chip { font-size: 12px; padding: 4px 10px; border-radius: 999px; background: var(--surface);
             border: 1px solid var(--line-strong); color: var(--ink); }
  .xf-api { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
  .xf-api li { padding: 9px 12px; border-radius: 9px; background: var(--surface); border: 1px solid var(--line);
               border-left: 3px solid var(--accent); }
  .xf-api a { font-size: 13px; font-weight: 700; color: var(--ink); text-decoration: none; }
  .xf-api a:hover { color: var(--accent); text-decoration: underline; }
  .xf-api small { display: block; margin-top: 2px; font-size: 12px; color: var(--muted); }
  .xf-none { margin: 6px 0 0; font-size: 12.5px; color: var(--ink-soft); }
  .xf-nums { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 14px; }
  .xf-num { padding: 10px; border-radius: 9px; background: var(--surface); border: 1px solid var(--line); text-align: center; }
  .xf-num b { display: block; font-size: 18px; color: var(--accent); }
  .xf-num small { display: block; font-size: 11px; color: var(--muted); line-height: 1.4; }
  .xf-bar { display: flex; gap: 3px; height: 54px; }
  .xf-bar span { display: flex; flex-direction: column; justify-content: center; padding: 0 8px; border-radius: 6px;
                 font-size: 12px; font-weight: 700; color: #fff; overflow: hidden; white-space: nowrap; }
  .xf-bar span small { font-size: 10.5px; font-weight: 500; opacity: 0.9; overflow: hidden; text-overflow: ellipsis; }
  .xf-bar span:nth-child(1) { background: #c96a1a; }
  .xf-bar span:nth-child(2) { background: #d98a45; }
  .xf-bar span:nth-child(3) { background: #3f7a52; }
  .xf-bar span:nth-child(4) { background: #6b7570; }
  .xf-grades { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin-top: 8px; }
  .xf-grades span { padding: 7px; border-radius: 7px; text-align: center; font-size: 12.5px; font-weight: 700; }
  .xf-grades small { display: block; font-size: 10.5px; font-weight: 500; }
  .g-s { background: #b3452f; color: #fff; } .g-a { background: #c96a1a; color: #fff; }
  .g-b { background: var(--surface-2); color: var(--ink); } .g-c { background: var(--surface); color: var(--muted); border: 1px solid var(--line); }
  .xf-pipe { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
  .xf-pipe div { position: relative; padding: 12px; border-radius: 10px; background: var(--surface); border: 1px solid var(--line);
                 border-top: 3px solid var(--accent); }
  .xf-pipe div.auto { border-top-color: var(--good); }
  .xf-pipe b { display: block; font-size: 14px; color: var(--ink); }
  .xf-pipe small { display: block; font-size: 12px; color: var(--muted); }
  .xf-pipe em { display: inline-block; margin-top: 6px; font-style: normal; font-size: 10.5px; font-weight: 700;
                padding: 1px 7px; border-radius: 999px; background: var(--accent-wash); color: var(--accent); }
  .xf-pipe div.auto em { background: var(--good-wash); color: var(--good); }
  .xf-dev { margin-top: 14px; }
  @media (max-width: 560px) {
    .xf-cmp { grid-template-columns: 1fr; } .xf-arrow { transform: rotate(90deg); justify-self: center; }
    .xf-flow, .xf-nums, .xf-grades, .xf-pipe { grid-template-columns: 1fr 1fr; }
    .xf-bar span small { display: none; }
  }

  /* ── 알파 실습 · 실전 사례 ── */
  .case-go { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin: 4px 0 6px;
             padding: 16px 20px; border-radius: 12px; background: var(--accent); color: var(--accent-ink);
             text-decoration: none; box-shadow: var(--shadow); }
  .case-go b { display: block; font-size: 16px; }
  .case-go small { display: block; font-size: 12px; opacity: 0.85; word-break: break-all; }
  .case-go-arrow { font-size: 24px; font-weight: 700; }
  .case-go:hover { filter: brightness(1.06); }
  .case-map { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
  .case-card { display: flex; flex-direction: column; gap: 4px; padding: 14px; border-radius: 10px;
               background: var(--surface); border: 1px solid var(--line); border-top: 3px solid var(--accent); }
  .case-step { font-size: 11px; font-weight: 700; color: var(--accent); letter-spacing: 0.02em; }
  .case-card strong { font-size: 14px; color: var(--ink); }
  .case-card small { font-size: 12px; color: var(--muted); line-height: 1.55; }
  @media (max-width: 560px) { .case-map { grid-template-columns: 1fr; } }

  /* ── The APPS ── */
  .apps-flow { gap: 6px; }
  .apps-flow .vnode { padding: 12px 6px; }
  .apps-flow .vnode strong { font-size: 13px; }
  .apps-flow .vnode small { font-size: 11px; }
  .apps-flow .varrow { font-size: 16px; }
  .vnode.done { border-color: var(--good); background: var(--good-wash); }
  .vnode.done .vrole { background: var(--good); color: var(--surface); }
  .apps-go { display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap;
             margin-top: 22px; padding: 16px 18px; border-radius: 12px; background: var(--surface); border: 1px solid var(--line); }
  .apps-go-title { margin: 0 0 4px; font-size: 15px; font-weight: 700; color: var(--ink); }
  .apps-go-sub { margin: 0; font-size: 12.5px; color: var(--muted); line-height: 1.6; }

  /* ── 서론 — 글 대신 그림으로 ── */
  .v-title { font-size: 15px; font-weight: 700; color: var(--ink); margin: 28px 0 12px; }

  .v-block { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 20px; }
  .vflow { display: flex; align-items: stretch; justify-content: center; gap: 10px; }
  .vnode { flex: 1; max-width: 170px; display: flex; flex-direction: column; align-items: center; gap: 4px;
           padding: 14px 10px; border: 1.5px solid var(--line-strong); border-radius: 12px; text-align: center; }
  .vnode.ai { border-color: var(--accent); background: var(--accent-wash); }
  .vrole { width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center;
           background: var(--ink); color: var(--surface); font-weight: 700; font-size: 13px; margin-bottom: 4px; }
  .vnode.ai .vrole { background: var(--accent); color: var(--accent-ink); }
  .vnode strong { font-size: 14px; color: var(--ink); }
  .vnode small { font-size: 12px; color: var(--muted); }
  .varrow { align-self: center; font-size: 20px; color: var(--muted); }
  .vloop { margin: 14px auto 0; width: fit-content; max-width: 100%; padding: 6px 14px; border-radius: 999px;
           border: 1.5px dashed var(--accent); color: var(--accent); font-size: 12.5px; font-weight: 600; text-align: center; }

  .build-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 0; }
  .build { margin: 0; }
  .build figcaption { margin-top: 6px; font-size: 12.5px; color: var(--ink-soft); text-align: center; }
  .build figcaption span { display: block; font-size: 11px; font-weight: 700; color: var(--accent); letter-spacing: 0.03em; }
  .mw { background: var(--surface); border: 1px solid var(--line-strong); border-radius: 8px; padding: 0 8px 8px;
        display: flex; flex-direction: column; gap: 6px; box-shadow: var(--shadow); }
  .mw-bar { display: flex; gap: 3px; padding: 6px 0 2px; border-bottom: 1px solid var(--line); margin: 0 -8px; padding-left: 8px; }
  .mw-bar span { width: 6px; height: 6px; border-radius: 50%; background: var(--line-strong); }
  .mw-in, .mw-out { display: flex; flex-direction: column; gap: 3px; }
  .mw-in i { height: 5px; border-radius: 3px; background: var(--surface-2); }
  .mw-in i:nth-child(2) { width: 80%; }
  .mw-in i:nth-child(3) { width: 60%; }
  .mw-out { flex-direction: row; gap: 4px; }
  .mw-out i { flex: 1; height: 22px; border-radius: 4px; border: 1px dashed var(--line-strong); }
  .mw-out i.on { border-style: solid; border-color: var(--good); background: var(--good-wash); }
  .mw-btns { display: flex; flex-wrap: wrap; gap: 3px; }
  .mw-btns b { font-size: 10px; font-weight: 600; line-height: 1; padding: 4px 5px; border-radius: 4px;
               border: 1px dashed var(--line-strong); color: var(--muted); }
  .mw-btns b.on { border-style: solid; border-color: var(--accent); color: var(--accent); }
  .mw-btns b.new { border-style: solid; border-color: var(--accent); background: var(--accent); color: var(--accent-ink);
                   box-shadow: 0 0 0 2px var(--accent-wash); }

  .cycle { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 6px; margin-top: 16px; }
  .cycle-label { font-size: 12.5px; font-weight: 700; color: var(--ink-soft); margin-right: 4px; }
  .chip { font-size: 12.5px; padding: 5px 12px; border-radius: 999px; background: var(--surface); border: 1px solid var(--line-strong); color: var(--ink); }
  .chip.next { background: var(--good-wash); border-color: var(--good); color: var(--good); font-weight: 600; }
  .carrow { color: var(--muted); font-size: 14px; }

  .vs { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .vs-card { border-radius: 12px; padding: 16px; border: 1.5px solid; }
  .vs-card.bad { border-color: var(--bad); background: var(--bad-wash); }
  .vs-card.good { border-color: var(--good); background: var(--good-wash); }
  .vs-head { margin: 0 0 12px; font-size: 14px; font-weight: 700; }
  .vs-card.bad .vs-head { color: var(--bad); }
  .vs-card.good .vs-head { color: var(--good); }
  .vs-pic { min-height: 140px; display: grid; place-items: center; margin-bottom: 12px; }
  .blob { position: relative; width: 150px; height: 96px; border-radius: 40% 55% 45% 60%; background: var(--surface);
          border: 1.5px solid var(--bad); display: grid; place-items: center; font-size: 12.5px; font-weight: 600; color: var(--ink-soft); }
  .blob em { position: absolute; font-style: normal; font-weight: 800; color: var(--bad); font-size: 18px; }
  .blob em:nth-of-type(1) { top: -6px; left: 14px; }
  .blob em:nth-of-type(2) { top: 30px; right: -8px; }
  .blob em:nth-of-type(3) { bottom: -8px; left: 60px; }
  .stack { display: flex; flex-direction: column; gap: 3px; width: 130px; }
  .stack span { font-size: 11.5px; font-weight: 600; text-align: center; padding: 3px 0; border-radius: 4px;
                background: var(--surface); border: 1px solid var(--good); color: var(--good); }
  .stack span.base { background: var(--good); color: var(--surface); border-color: var(--good); }
  .vs-card ul { margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 4px; }
  .vs-card li { font-size: 13px; color: var(--ink-soft); }

  .tips { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .tip { display: flex; flex-direction: column; gap: 3px; background: var(--surface); border: 1px solid var(--line);
         border-left: 3px solid var(--accent); border-radius: 10px; padding: 12px 14px; }
  .tip:last-child:nth-child(odd) { grid-column: 1 / -1; }
  .tip strong { font-size: 13.5px; color: var(--ink); }
  .tip small { font-size: 12px; color: var(--muted); }

  @media (max-width: 560px) {
    .vflow { flex-direction: column; align-items: center; }
    .vnode { width: 100%; max-width: none; }
    .varrow { transform: rotate(90deg); }
    .build-grid { grid-template-columns: repeat(2, 1fr); }
    .vs, .tips { grid-template-columns: 1fr; }
  }

  .criteria-box { background: var(--good-wash); border-radius: 10px; padding: 14px 16px; margin-bottom: 4px; }

  .criteria-label {
    font-size: 12px;
    font-weight: 700;
    color: var(--good);
    margin: 0 0 8px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .criteria-box ul { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 6px; }

  .criteria-box li { font-size: 13.5px; color: var(--ink-soft); padding-left: 22px; position: relative; }

  .criteria-box li::before {
    content: "✓";
    position: absolute;
    left: 0;
    color: var(--good);
    font-weight: 700;
  }

  .answer-details { margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--line); }
  .answer-details summary { cursor: pointer; font-size: 13.5px; font-weight: 600; color: var(--ink-soft); }
  .answer-details summary:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .answer-details[open] summary { color: var(--ink); margin-bottom: 12px; }

  .code-box { position: relative; }
  .code-box .copy-btn { position: absolute; top: 8px; right: 8px; }

  .code-block {
    margin: 0;
    background: var(--surface-2);
    border-radius: 10px;
    padding: 16px;
    overflow-x: auto;
    font-family: "IBM Plex Mono", ui-monospace, monospace;
    font-size: 12.5px;
    line-height: 1.6;
    color: var(--ink);
    white-space: pre;
  }

  /* ── 페이지 이동 바 ── */

  .page-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-top: 34px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
  }

  .page-nav-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 13.5px;
    font-weight: 600;
    padding: 9px 16px;
    border-radius: 9px;
    border: 1px solid var(--line-strong);
    background: var(--surface);
    color: var(--ink);
    cursor: pointer;
  }

  .page-nav-btn:hover { background: var(--surface-2); }
  .page-nav-btn:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
  .page-nav-btn:disabled { opacity: 0.35; cursor: default; }
  .page-nav-btn:disabled:hover { background: var(--surface); }
  .page-nav-btn.next { background: var(--accent); border-color: var(--accent); color: var(--accent-ink); }
  .page-nav-btn.next:hover { filter: brightness(1.05); }

  .page-nav-pos {
    font-size: 12px;
    color: var(--muted);
    font-family: "IBM Plex Mono", ui-monospace, monospace;
  }

  footer {
    margin-top: 44px;
    padding-top: 18px;
    border-top: 1px solid var(--line);
    font-size: 12px;
    color: var(--muted);
  }
</style>'''

TOC_HTML = f'''<button class="toc-toggle" id="tocToggle" aria-label="목차 열기" aria-expanded="false">☰</button>
<div class="toc-backdrop" id="tocBackdrop"></div>
<nav class="toc" id="toc" aria-label="실습 목차">
  <button class="toc-close" id="tocClose" aria-label="목차 닫기">✕</button>
  <div class="toc-brand">DART·뉴스 정보 크롤링 및 메일발송 프로그램 만들기</div>

  <a class="toc-link" data-page="intro" href="#intro"><span class="toc-badge">i</span>서론 · 바이브코딩이란</a>
  <a class="toc-link" data-page="prep" href="#prep"><span class="toc-badge">0</span>사전 준비</a>

  <div class="toc-group-label">실습 1 · 수집</div>
{toc_part1}

  <div class="toc-group-label">실습 2 · 보고서</div>
{toc_part2}

  <div class="toc-group-label">실습 3 · 메일 발송</div>
{toc_part3}

  <div class="toc-group-label">알파 실습 · 고도화</div>
      <a class="toc-link" data-page="case" href="#case"><span class="toc-badge">★</span>실전 사례</a>
{toc_part4}

  <div class="toc-group-label">참고</div>
      <a class="toc-link" data-page="apis" href="#apis"><span class="toc-badge">?</span>API 모음</a>
      <a class="toc-link" data-page="apps" href="#apps"><span class="toc-badge">+</span>The APPS</a>
</nav>'''



# ── API 안내 페이지 ───────────────────────────────────────
# 수치(한도·가격)는 2026-09-21 확인값이다. 자주 바뀌므로 발급처 화면을 우선한다.
APIS_PAGE = '''
  <section class="page" data-page="apis" id="apis">
    <div class="page-head">
      <span class="page-eyebrow">참고</span>
      <div class="page-title-row">
        <h2>유용한 API 모음</h2>
      </div>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">무료 · 부분 무료 — 인증키만 받으면 쓸 수 있다</p>
      <p class="tiny" style="margin:0 0 4px;">이름을 누르면 그 API 신청 페이지가 바로 열린다.</p>
      <div class="apitable-wrap">
      <table class="apitable compact">
        <thead><tr><th>API</th><th>무엇에 쓰나</th><th>요금</th><th>한도</th></tr></thead>
        <tbody>
          <tr class="api-cat"><td colspan="4">입찰 · 계약</td></tr>
          <tr><td class="api-name api-pick" title="조달청"><a href="https://www.data.go.kr/data/15129394/openapi.do" target="_blank" rel="noopener">나라장터 입찰공고</a></td><td class="api-use">공사·물품 입찰공고 매일 받기</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1,000건</td></tr>
          <tr><td class="api-name" title="조달청"><a href="https://www.data.go.kr/data/15129415/openapi.do" target="_blank" rel="noopener">나라장터 가격정보</a></td><td class="api-use">조달 자재 단가</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1,000건</td></tr>
          <tr><td class="api-name" title="국토교통부"><a href="https://www.data.go.kr/data/15061362/openapi.do" target="_blank" rel="noopener">키스콘 건설업체정보</a></td><td class="api-use">협력·경쟁 업체 면허·실적</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1만 건</td></tr>
          <tr class="api-cat"><td colspan="4">현장 · 안전</td></tr>
          <tr><td class="api-name api-pick" title="기상청"><a href="https://www.data.go.kr/data/15084084/openapi.do" target="_blank" rel="noopener">기상청 단기예보</a></td><td class="api-use">3일 강우·강풍 · 작업중지 판단</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1만 건</td></tr>
          <tr><td class="api-name" title="기상청"><a href="https://www.data.go.kr/data/15059468/openapi.do" target="_blank" rel="noopener">기상청 중기예보</a></td><td class="api-use">10일 날씨 · 공정 계획</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1만 건</td></tr>
          <tr><td class="api-name" title="기상청"><a href="https://www.data.go.kr/data/15000415/openapi.do" target="_blank" rel="noopener">기상특보</a></td><td class="api-use">호우·강풍·한파 특보</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1만 건</td></tr>
          <tr><td class="api-name" title="기상청"><a href="https://www.data.go.kr/data/15000420/openapi.do" target="_blank" rel="noopener">지진정보</a></td><td class="api-use">지진 발생 시 현장 점검</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1만 건</td></tr>
          <tr><td class="api-name" title="한국환경공단"><a href="https://www.data.go.kr/data/15073861/openapi.do" target="_blank" rel="noopener">에어코리아 대기질</a></td><td class="api-use">미세먼지 · 옥외작업 관리</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 500건</td></tr>
          <tr><td class="api-name" title="산업안전보건공단"><a href="https://www.data.go.kr/data/15121001/openapi.do" target="_blank" rel="noopener">국내 재해사례</a></td><td class="api-use">사고 사례로 안전교육</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1,000건</td></tr>
          <tr><td class="api-name api-pick" title="한국천문연구원"><a href="https://www.data.go.kr/data/15012690/openapi.do" target="_blank" rel="noopener">공휴일 정보</a></td><td class="api-use">공정표 작업일수 계산</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1만 건</td></tr>
          <tr class="api-cat"><td colspan="4">부동산 · 인허가</td></tr>
          <tr><td class="api-name" title="국토교통부"><a href="https://www.data.go.kr/data/15136267/openapi.do" target="_blank" rel="noopener">건축인허가정보</a></td><td class="api-use">허가·착공 동향 · 영업</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1만 건</td></tr>
          <tr><td class="api-name" title="국토교통부"><a href="https://www.data.go.kr/data/15134735/openapi.do" target="_blank" rel="noopener">건축물대장</a></td><td class="api-use">부지·건물 제원</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1만 건</td></tr>
          <tr><td class="api-name" title="국토교통부"><a href="https://www.data.go.kr/data/15058410/openapi.do" target="_blank" rel="noopener">토지이용규제정보</a></td><td class="api-use">용도지역·규제 확인</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 1,000건</td></tr>
          <tr><td class="api-name" title="한국부동산원"><a href="https://www.data.go.kr/data/15098547/openapi.do" target="_blank" rel="noopener">청약홈 분양정보</a></td><td class="api-use">분양 일정 · 경쟁 단지</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 4만 건</td></tr>
          <tr class="api-cat"><td colspan="4">경제 · 통계</td></tr>
          <tr><td class="api-name" title="한국은행"><a href="https://ecos.bok.or.kr/api/" target="_blank" rel="noopener">경제통계 ECOS</a></td><td class="api-use">금리·환율</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">한도 공지 없음</td></tr>
          <tr><td class="api-name" title="국가데이터처"><a href="https://kosis.kr/openapi/" target="_blank" rel="noopener">국가통계 KOSIS</a></td><td class="api-use">건설수주액 · 물가지수</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">분당 200건</td></tr>
          <tr class="api-cat"><td colspan="4">공시 · 뉴스 · 위치</td></tr>
          <tr><td class="api-name" title="금융감독원 · 오늘 쓴 것"><a href="https://opendart.fss.or.kr/uss/umt/EgovMberInsertView.do" target="_blank" rel="noopener">DART 전자공시</a></td><td class="api-use">상장사 공시</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 4만 건</td></tr>
          <tr><td class="api-name" title="오늘 쓴 것 · 인증키 없음">구글 뉴스</td><td class="api-use">키워드 뉴스</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">인증키 없음</td></tr>
          <tr><td class="api-name" title="NAVER API HUB"><a href="https://www.ncloud.com/product/applicationService/naverApiHub" target="_blank" rel="noopener">네이버 검색</a></td><td class="api-use">뉴스·블로그 검색</td><td class="api-fee"><span class="tag free">무료</span></td><td class="api-quota">하루 2만 5천 건</td></tr>
          <tr><td class="api-name" title="카카오"><a href="https://developers.kakao.com/docs/ko/kakaomap/common" target="_blank" rel="noopener">카카오 로컬</a></td><td class="api-use">주소 → 좌표 · 현장 지도</td><td class="api-fee"><span class="tag partial">부분 무료</span></td><td class="api-quota">하루 10만 건 · 넘으면 유료</td></tr>
        </tbody>
      </table>
      </div>
      <p class="tiny" style="margin-top:8px;">주황색이 우리 업무에 가장 가깝다. 공공데이터포털 한도는
        개발계정 기준이고 활용사례를 등록하면 늘릴 수 있다. <strong>부분 무료</strong>(카카오)는
        무료 한도를 넘으면 건당 0.5~2원 — 결제 수단(비즈월렛)을 연결하고 유료 사용을 켜야만
        넘어가므로 모르는 사이에 과금되지는 않는다.</p>
    </div>

    <div class="criteria-box">
      <p class="criteria-label">AI API — 웍스 AI API 를 쓴다</p>
      <ul>
        <li><strong>쓰는 곳</strong> — 모아온 기사를 요약·분류하고 중요도를 매기기. 오늘 만든 보고서에 붙이면
          「읽을 것만 골라주는」 리포트가 된다.</li>
        <li><strong>외부 유료 AI API</strong> (Claude · GPT · Gemini 등) 도 있지만, 사내 자료가 회사 밖으로
          나가는 <strong>보안 문제</strong>가 있다.</li>
        <li>그래서 회사는 <strong>웍스 AI API</strong> 사용을 권한다. 사용을 원하면 <strong>DX팀에 문의</strong>.</li>
      </ul>
    </div>
  </section>'''

# ── 마지막 안내 페이지 ────────────────────────────────────
# 실습이 끝난 사람에게 "만든 걸 어디에 올리는지" 를 알려주는 자리.
# 매뉴얼 파일은 여기에 넣지 않는다 (사내 배포 문서라 별도로 전달한다).
APPS_PAGE = '''
  <section class="page" data-page="apps" id="apps">
    <div class="page-head">
      <span class="page-eyebrow">참고</span>
      <div class="page-title-row">
        <h2>만든 걸 사내에 등록하기 — The APPS</h2>
      </div>
      <p class="step-desc">오늘 만든 프로그램은 내 PC 에만 있다. 팀에서 같이 쓰려면
        사내 앱 스토어 <strong>The APPS</strong> 에 등록한다.</p>
    </div>

    <div class="v-block">
      <div class="vflow apps-flow">
        <div class="vnode"><span class="vrole">1</span><strong>내 PC</strong><small>오늘 만든 프로그램</small></div>
        <span class="varrow" aria-hidden="true">→</span>
        <div class="vnode"><span class="vrole">2</span><strong>등록 신청</strong><small>누구나 · 파일도 웹앱도</small></div>
        <span class="varrow" aria-hidden="true">→</span>
        <div class="vnode"><span class="vrole">3</span><strong>운영 심사</strong><small>쓸 만한 도구인지</small></div>
        <span class="varrow" aria-hidden="true">→</span>
        <div class="vnode ai"><span class="vrole">4</span><strong>보안 심사</strong><small>인증키·비밀번호 검사</small></div>
        <span class="varrow" aria-hidden="true">→</span>
        <div class="vnode done"><span class="vrole">✓</span><strong>게시</strong><small>팀원이 검색·설치</small></div>
      </div>
      <div class="vloop"><strong>API 키는 절대 노출되면 안 된다</strong> · 보안 심사에서 파일 안에 인증키가 있으면 걸린다</div>
    </div>

    <p class="v-title">The APPS 에서 할 수 있는 것</p>
    <div class="tips">
      <div class="tip"><strong>Xi C&amp;A 앱스토어</strong><small>임직원이 직접 만든 앱 · 웹을 한곳에 모아서 볼 수 있다</small></div>
      <div class="tip"><strong>웹/앱 올리기</strong><small>누구나 신청 · 파일로 쓰는 도구도, 주소로 접속하는 웹앱도 된다</small></div>
      <div class="tip"><strong>심사 / 지원</strong><small>운영 · 보안을 심사하고, AI API 와 배포 · DB 를 지원한다</small></div>
      <div class="tip"><strong>기록 — 설치 수 · 별점</strong><small>누가 실제로 쓰는지 숫자로 남는다</small></div>
    </div>

    <div class="apps-go">
      <div>
        <p class="apps-go-title">The APPS <span class="tag partial">오픈 전</span></p>
        <p class="apps-go-sub"><strong>사내망에서만</strong> 접속 가능<br>
          계정·권한·등록 절차 매뉴얼은 따로 전달한다</p>
      </div>
      <a class="btn primary" href="https://vibe-registry.xicna.app/" target="_blank" rel="noopener">vibe-registry.xicna.app</a>
    </div>
  </section>'''

# ── 서론 ────────────────────────────────────────────────
# 바이브코딩이 무엇이고, 왜 「틀 먼저, 부품은 하나씩」 인지. 실습 전에 먼저 보는 페이지.
INTRO_PAGE = '''
  <section class="page" data-page="intro" id="intro">
    <div class="page-head">
      <span class="page-eyebrow">서론</span>
      <div class="page-title-row">
        <h2>바이브코딩이란</h2>
      </div>
      <p class="step-desc"><strong>말로 시키고, 눈으로 확인한다.</strong> 코드는 AI 가 쓴다.</p>
    </div>

    <div class="v-block">
      <div class="vflow">
        <div class="vnode">
          <span class="vrole">나</span>
          <strong>말로 설명</strong>
          <small>무엇을 만들지</small>
        </div>
        <span class="varrow" aria-hidden="true">→</span>
        <div class="vnode ai">
          <span class="vrole">AI</span>
          <strong>코드 작성</strong>
          <small>어떻게 만들지</small>
        </div>
        <span class="varrow" aria-hidden="true">→</span>
        <div class="vnode">
          <span class="vrole">▶</span>
          <strong>실행 · 확인</strong>
          <small>눈으로 본다</small>
        </div>
      </div>
      <div class="vloop">↺ 틀리면 다시 말한다 · 에러 문장은 그대로 붙여넣기</div>
    </div>

    <p class="v-title">순서 — 틀 먼저, 부품은 하나씩</p>
    <div class="build-grid">
      <figure class="build">
        <div class="mw">
          <div class="mw-bar"><span></span><span></span><span></span></div>
          <div class="mw-in"><i></i><i></i><i></i></div>
          <div class="mw-btns"><b>뉴스</b><b>DART</b><b>보고서</b><b>메일</b><b>전체</b></div>
          <div class="mw-out"><i></i><i></i><i></i></div>
        </div>
        <figcaption><span>STEP 0</span>틀 — 화면만</figcaption>
      </figure>
      <figure class="build">
        <div class="mw">
          <div class="mw-bar"><span></span><span></span><span></span></div>
          <div class="mw-in"><i></i><i></i><i></i></div>
          <div class="mw-btns"><b class="new">뉴스</b><b>DART</b><b>보고서</b><b>메일</b><b>전체</b></div>
          <div class="mw-out"><i class="on"></i><i></i><i></i></div>
        </div>
        <figcaption><span>STEP 1</span>+ 뉴스</figcaption>
      </figure>
      <figure class="build">
        <div class="mw">
          <div class="mw-bar"><span></span><span></span><span></span></div>
          <div class="mw-in"><i></i><i></i><i></i></div>
          <div class="mw-btns"><b class="on">뉴스</b><b class="new">DART</b><b>보고서</b><b>메일</b><b>전체</b></div>
          <div class="mw-out"><i class="on"></i><i class="on"></i><i></i></div>
        </div>
        <figcaption><span>STEP 2</span>+ DART</figcaption>
      </figure>
      <figure class="build">
        <div class="mw">
          <div class="mw-bar"><span></span><span></span><span></span></div>
          <div class="mw-in"><i></i><i></i><i></i></div>
          <div class="mw-btns"><b class="on">뉴스</b><b class="on">DART</b><b class="new">보고서</b><b>메일</b><b>전체</b></div>
          <div class="mw-out"><i class="on"></i><i class="on"></i><i class="on"></i></div>
        </div>
        <figcaption><span>STEP 3</span>+ 보고서</figcaption>
      </figure>
      <figure class="build">
        <div class="mw">
          <div class="mw-bar"><span></span><span></span><span></span></div>
          <div class="mw-in"><i></i><i></i><i></i></div>
          <div class="mw-btns"><b class="on">뉴스</b><b class="on">DART</b><b class="on">보고서</b><b class="new">메일</b><b>전체</b></div>
          <div class="mw-out"><i class="on"></i><i class="on"></i><i class="on"></i></div>
        </div>
        <figcaption><span>STEP 4</span>+ 메일</figcaption>
      </figure>
      <figure class="build">
        <div class="mw">
          <div class="mw-bar"><span></span><span></span><span></span></div>
          <div class="mw-in"><i></i><i></i><i></i></div>
          <div class="mw-btns"><b class="on">뉴스</b><b class="on">DART</b><b class="on">보고서</b><b class="on">메일</b><b class="new">전체</b></div>
          <div class="mw-out"><i class="on"></i><i class="on"></i><i class="on"></i></div>
        </div>
        <figcaption><span>STEP 5</span>통합 실행</figcaption>
      </figure>
    </div>

    <div class="cycle">
      <span class="cycle-label">부품마다</span>
      <span class="chip">시키기</span><span class="carrow">→</span>
      <span class="chip">실행</span><span class="carrow">→</span>
      <span class="chip">확인</span><span class="carrow">→</span>
      <span class="chip next">다음 부품</span>
    </div>

    <p class="v-title">왜 틀부터?</p>
    <div class="vs">
      <div class="vs-card bad">
        <p class="vs-head">✕ 한 번에 다</p>
        <div class="vs-pic">
          <div class="blob">전부 한꺼번에<em>?</em><em>?</em><em>?</em></div>
        </div>
        <ul>
          <li>빠진 요구는 나중에 발견</li>
          <li>에러가 어디서 났는지 모름</li>
          <li>하나 고치면 다른 게 깨짐</li>
        </ul>
      </div>
      <div class="vs-card good">
        <p class="vs-head">✓ 틀 먼저, 하나씩</p>
        <div class="vs-pic">
          <div class="stack">
            <span>메일 ✓</span><span>보고서 ✓</span><span>DART ✓</span><span>뉴스 ✓</span>
            <span class="base">틀</span>
          </div>
        </div>
        <ul>
          <li>화면을 보며 요구가 정리됨</li>
          <li>에러는 방금 채운 곳</li>
          <li>그 부품만 고치면 끝</li>
        </ul>
      </div>
    </div>

    <p class="v-title">말로 시킬 때 요령</p>
    <div class="tips">
      <div class="tip"><strong>틀부터 만들기</strong><small>화면을 먼저 그려보면 무엇을 입력받고 무엇을 보여줄지, 요구사항이 분명해진다</small></div>
      <div class="tip"><strong>한 번에 하나씩</strong><small>기능 하나 시키고, 되면 다음</small></div>
      <div class="tip"><strong>에러는 화면에 보이게</strong><small>프로그램 안에서 난 에러 · 오류 코드는 항상 사용자가 볼 수 있게 띄우라고 시킨다</small></div>
      <div class="tip"><strong>안 될 때도 알리게</strong><small>0건이면 왜 0건인지 — 조용한 실패가 제일 무섭다</small></div>
      <div class="tip"><strong>되는 버전은 남겨두기</strong><small>다음 기능을 붙이기 전에 파일을 복사해둔다</small></div>
    </div>
  </section>'''

PREP_PAGE = f'''
  <section class="page" data-page="prep" id="prep">
    <div class="page-inner">
      <h1>DART·뉴스 정보 크롤링 및 메일발송 프로그램 만들기</h1>

      <div class="group-head" style="margin-top: 26px;">
        <span class="num">0</span>
        <h2>사전 준비</h2>
      </div>

      <div class="pv-map">
        <div class="pv-map-item"><span class="pv-map-num">A</span><strong>설치</strong><small>더블클릭 한 번</small></div>
        <div class="pv-map-item"><span class="pv-map-num">B</span><strong>DART 인증키</strong><small>무료 발급 · 메모장에</small></div>
        <div class="pv-map-item"><span class="pv-map-num">C</span><strong>뉴스</strong><small>발급할 것 없음</small></div>
        <div class="pv-map-item"><span class="pv-map-num">E</span><strong>아웃룩</strong><small>로그인만 확인</small></div>
      </div>

{sections_prep}
    </div>
  </section>'''


FOOTER = '''
  <footer>
    입력한 인증키는 <code>settings.json</code> 에 저장됩니다 — 이 파일은 공유하지 마세요.
  </footer>'''

SCRIPT = '''<script>
(function () {
  var PAGE_IDS = ''' + repr(ALL_PAGE_IDS).replace("'", '"') + ''';
  var STORAGE_KEY = "issuebot-checklist";
  var STATE_KEY = "issuebot-current-page";

  var boxes = Array.prototype.slice.call(document.querySelectorAll(".check"));
  var pages = Array.prototype.slice.call(document.querySelectorAll(".page"));
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll(".toc-link"));
  var itemCountWordEl = document.getElementById("itemCountWord");
  var navPrevBtn = document.getElementById("pageNavPrev");
  var navNextBtn = document.getElementById("pageNavNext");
  var navPosEl = document.getElementById("pageNavPos");

  var toc = document.getElementById("toc");
  var tocToggle = document.getElementById("tocToggle");
  var tocClose = document.getElementById("tocClose");
  var tocBackdrop = document.getElementById("tocBackdrop");

  function loadState() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); }
    catch (e) { return {}; }
  }

  function saveState(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
    catch (e) { /* 저장 안 되면 세션 동안만 유지 */ }
  }

  function render() {
    // 진행률 표시는 두지 않는다. 체크박스는 스스로 확인하는 용도로만 쓰고,
    // 다 체크한 단계는 목차에서 색으로만 표시한다.
    if (itemCountWordEl) itemCountWordEl.textContent = "6가지";

    tocLinks.forEach(function (link) {
      var pageId = link.dataset.page;
      var pageEl = document.getElementById(pageId);
      if (!pageEl) return;
      var pageBoxes = pageEl.querySelectorAll(".check");
      var allDone = pageBoxes.length > 0 &&
        Array.prototype.every.call(pageBoxes, function (b) { return b.checked; });
      link.classList.toggle("done", allDone);
    });
  }

  var state = loadState();
  boxes.forEach(function (box) {
    var id = box.dataset.id;
    if (state[id]) box.checked = true;
    box.addEventListener("change", function () {
      state[id] = box.checked;
      saveState(state);
      render();
    });
    box.addEventListener("click", function (e) { e.stopPropagation(); });
  });

  /* ── 페이지 전환 ── */

  function currentIndex() {
    var active = document.querySelector(".page.active");
    if (!active) return 0;
    var idx = PAGE_IDS.indexOf(active.dataset.page);
    return idx === -1 ? 0 : idx;
  }

  function goTo(pageId, opts) {
    opts = opts || {};
    if (PAGE_IDS.indexOf(pageId) === -1) pageId = PAGE_IDS[0];

    pages.forEach(function (p) { p.classList.toggle("active", p.dataset.page === pageId); });
    tocLinks.forEach(function (l) { l.classList.toggle("current", l.dataset.page === pageId); });

    var idx = PAGE_IDS.indexOf(pageId);
    navPrevBtn.disabled = idx <= 0;
    navNextBtn.disabled = idx >= PAGE_IDS.length - 1;
    navNextBtn.textContent = idx >= PAGE_IDS.length - 1 ? "완료" : "다음 →";
    navPosEl.textContent = (idx + 1) + " / " + PAGE_IDS.length;

    if (!opts.skipHash) {
      if (history.replaceState) history.replaceState(null, "", "#" + pageId);
      else location.hash = pageId;
    }
    try { sessionStorage.setItem(STATE_KEY, pageId); } catch (e) {}

    if (!opts.skipScroll) window.scrollTo(0, 0);
    closeToc();
  }

  tocLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      goTo(link.dataset.page);
    });
  });

  navPrevBtn.addEventListener("click", function () {
    var idx = currentIndex();
    if (idx > 0) goTo(PAGE_IDS[idx - 1]);
  });

  navNextBtn.addEventListener("click", function () {
    var idx = currentIndex();
    if (idx < PAGE_IDS.length - 1) goTo(PAGE_IDS[idx + 1]);
  });

  window.addEventListener("hashchange", function () {
    var id = location.hash.replace("#", "");
    if (id) goTo(id, { skipHash: true });
  });

  /* ── 목차 열기/닫기 (좁은 화면) ── */

  function openToc() {
    toc.classList.add("open");
    tocBackdrop.classList.add("show");
    tocToggle.setAttribute("aria-expanded", "true");
  }
  function closeToc() {
    toc.classList.remove("open");
    tocBackdrop.classList.remove("show");
    tocToggle.setAttribute("aria-expanded", "false");
  }
  tocToggle.addEventListener("click", function () {
    toc.classList.contains("open") ? closeToc() : openToc();
  });
  tocClose.addEventListener("click", closeToc);
  tocBackdrop.addEventListener("click", closeToc);

  /* ── 초기 페이지 결정: URL 해시 > 이전 세션 > 첫 페이지 ── */

  var initial = location.hash.replace("#", "");
  if (!initial) {
    try { initial = sessionStorage.getItem(STATE_KEY) || ""; } catch (e) { initial = ""; }
  }
  render();
  goTo(initial || PAGE_IDS[0], { skipHash: !initial, skipScroll: true });

  /* ── 복사 버튼 ── */

  function copyText(text, btn) {
    var settled = false;
    var done = function () {
      if (settled) return;
      settled = true;
      var original = btn.textContent;
      btn.textContent = "복사됨!";
      btn.classList.add("copied");
      setTimeout(function () {
        btn.textContent = original;
        btn.classList.remove("copied");
      }, 1500);
    };

    /* 클립보드 API가 권한 프롬프트 등으로 응답 없이 멈추는 경우를 대비해
       일정 시간 안에 안 끝나면 execCommand 방식으로 바로 넘어간다. */
    var timeoutId = setTimeout(function () { fallbackCopy(text, done); }, 600);

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () { clearTimeout(timeoutId); done(); },
        function () { clearTimeout(timeoutId); fallbackCopy(text, done); }
      );
    } else {
      clearTimeout(timeoutId);
      fallbackCopy(text, done);
    }
  }

  function fallbackCopy(text, done) {
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      done();
    } catch (e) { /* 복사 실패 시 그냥 무시 */ }
  }

  /* 명령어 조각을 클릭하면 그 내용이 복사된다. 라벨(체크박스)이나 summary 안에 있는 경우가
     있어서 기본 동작을 막지 않으면 체크가 켜지거나 블록이 펼쳐진다. */
  Array.prototype.slice.call(document.querySelectorAll("code.cmd, code.cmd-text")).forEach(function (el) {
    el.title = "클릭하면 복사";
    el.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      var text = el.textContent;
      copyText(text, {
        get textContent() { return text; },
        set textContent(v) { /* 조각 안의 글자는 그대로 둔다 */ },
        classList: el.classList
      });
    });
  });

  Array.prototype.slice.call(document.querySelectorAll(".copy-btn")).forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      // summary 안에 있는 버튼이라, 막지 않으면 복사하면서 블록이 같이 펼쳐진다.
      e.preventDefault();
      e.stopPropagation();
      var target = document.getElementById(btn.dataset.copy);
      if (!target) return;
      copyText(target.textContent, btn);
    });
  });

  /* ── "정답 코드 파일 받기" — main.py 를 base64 로 박아뒀다가 Blob 으로 내려받는다 ── */
  var STAGE_B64 = __STAGE_B64__;
  Array.prototype.slice.call(document.querySelectorAll(".download-stage-btn")).forEach(function (btn) {
    btn.addEventListener("click", function () {
      try {
        var stage = btn.dataset.stage;
        var binary = atob(STAGE_B64[stage]);
        var bytes = new Uint8Array(binary.length);
        for (var i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
        var blob = new Blob([bytes], { type: "text/x-python" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = btn.dataset.file || ("STEP" + stage + ".py");   // 이름만 보고 몇 단계까지 된 파일인지 알게
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 2000);
      } catch (e) {
        alert("다운로드에 실패했습니다. 페이지를 새로고침한 뒤 다시 눌러주세요.");
      }
    });
  });
})();
</script>'''
SCRIPT = SCRIPT.replace("__STAGE_B64__", STAGE_B64_JS)

body = f'''{TOC_HTML}

<div class="content-outer">
  <div class="wrap">

{INTRO_PAGE}
{PREP_PAGE}
{step_pages_html}
{CASE_PAGE}
{APIS_PAGE}
{APPS_PAGE}

    <div class="page-nav">
      <button class="page-nav-btn" id="pageNavPrev">← 이전</button>
      <span class="page-nav-pos" id="pageNavPos">1 / {len(ALL_PAGE_IDS)}</span>
      <button class="page-nav-btn next" id="pageNavNext">다음 →</button>
    </div>

{FOOTER}
  </div>
</div>'''

doc = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DART·뉴스 정보 크롤링 및 메일발송 프로그램 만들기</title>
{FAVICON}
{fonts_head}
{STYLE}
</head>
<body>
{body}

{SCRIPT}
</body>
</html>
'''

out_path = f"{REPO}/DART 뉴스 크롤링 및 메일발송 프로그램 만들기.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(doc)

# GitHub Pages 로 공유할 때 주소가 짧아지도록 같은 내용을 index.html 로도 쓴다.
# (한글·공백이 든 파일명은 주소에서 DART%20뉴스%20... 로 길게 늘어난다)
# 사람이 더블클릭해서 여는 것은 위의 한글 파일명 쪽을 그대로 쓴다.
index_path = f"{REPO}/index.html"
with open(index_path, "w", encoding="utf-8") as f:
    f.write(doc)

print("written:", out_path, len(doc), "chars,", len(ALL_PAGE_IDS), "pages")
print("written:", index_path, "(Pages 용 같은 사본)")
