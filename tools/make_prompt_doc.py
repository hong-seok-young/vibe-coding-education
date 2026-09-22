"""한 번에 붙여넣는 프롬프트 문서를 만든다.

    python tools/make_prompt_doc.py

저장소 루트의 최종프롬프트.md 를 steps.py 에서 생성한다. 손으로 관리하면 실습 페이지와
어긋난다 — 실제로 단계 구성이 바뀐 뒤에도 옛 내용이 남아 있었다.
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from steps import STEPS

OUT = os.path.join(REPO, "최종프롬프트.md")

HEAD = """# 한 번에 붙여넣는 프롬프트

**이 파일은 `tools/make_prompt_doc.py` 가 `tools/steps.py` 에서 만든다. 직접 고치지 말 것.**

실습 페이지는 STEP 을 나눠 진행하지만, 한 번에 다 넣어보고 싶을 때 쓰라고 이어붙인
것이다. 각 문장이 왜 있는지는 [`강사가-알려줄것.md`](강사가-알려줄것.md) 에 측정값과
함께 적어뒀다. **문장을 줄이면 줄인 자리에서 막힌다.**

단계별로 나눠 쓰려면 실습 페이지를 그대로 따라가면 된다.

---
"""

TAIL = """
---

## 확인한 것

동작을 확인한 프로그램은 [`news-report-bot/main.py`](news-report-bot/main.py) 이고,
단계별 스냅샷은 [`news-report-bot/단계별/`](news-report-bot/단계별) 에 있다.

| 항목 | 결과 |
|---|---|
| 창이 뜨고 버튼 5개 동작 | OK |
| 뉴스 수집 | 검색어당 10건 상한 지켜짐, 한국시간 표시 |
| DART 마지막 페이지까지 | 약 2,700~3,000건 / 28~30페이지 / 15초 |
| 회사 필터 | 검색어에 적은 회사만, 회사별 건수 요약 |
| DART 원문 링크 | 실제 공시 문서 열림 |
| 보고서 | 파일 생성 후 브라우저로 열림 |
| 아웃룩 자동 발송 | 보낸 편지함 확인, 메일 창 뜨지 않음 |
| 창 멈춤 | 0.00초 |
"""


def main():
    parts = [HEAD]
    for step in STEPS:
        parts.append("\n## STEP %s · %s\n" % (step["num"], step["title"]))
        if step.get("need_install"):
            parts.append("\n먼저 터미널에 `%s`\n" % step["need_install"])
        parts.append("\n```\n%s\n```\n" % step["prompt"])
    parts.append(TAIL)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write("".join(parts))
    print("written:", OUT, "(%d STEP)" % len(STEPS))


if __name__ == "__main__":
    main()
