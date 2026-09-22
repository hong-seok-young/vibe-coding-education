# tools — 실습 페이지 생성기

저장소 루트의 **`DART 뉴스 크롤링 및 메일발송 프로그램 만들기.html`** 은 손으로 쓴 게
아니라 여기서 만들어진다. **HTML 을 직접 고치지 말 것** — 다음 실행에 덮어써진다.

```
python3 tools/make_stage_files.py   # main.py 에서 단계별 정답 파일 6개를 만든다
python3 tools/check_stage_files.py  # 그 6개가 실제로 열리는지 확인한다
python3 tools/build_page.py         # HTML 을 다시 만든다
python3 tools/check_page.py         # 만들어진 HTML 을 점검한다
python3 tools/capture_window.py     # STEP 0 의 창 그림을 다시 찍는다 (윈도우에서만)
```

**`main.py` 를 고쳤으면 순서대로 다 돌려야 한다.** 단계별 파일이 거기서 만들어지고,
그게 다시 HTML 에 박히기 때문이다.

| 파일 | 무엇 |
|---|---|
| `steps.py` | STEP 0~9 의 프롬프트·성공 기준·정답 코드 조각. **내용을 고치는 곳은 대개 여기다** |
| `prep.html` | 사전 준비 페이지 마크업 (체크리스트, DART 키 발급 안내) |
| `build_page.py` | 위 둘 + 스타일·스크립트·The APPS 안내 페이지를 합쳐 HTML 하나로 |
| `make_stage_files.py` | `main.py` 에서 뒤 단계 기능을 덜어내 `news-report-bot/단계별/STEP0~5.py` 를 만든다. **단계마다 다른 파일을 내려줘야 하는 이유** — 완성본 하나만 내려주면 STEP 0 에서 이미 다 된 프로그램을 받게 되어 실습이 사라진다 |
| `check_stage_files.py` | 그 6개를 실제로 띄워 입력 칸·버튼·결과 칸 수와, 아직 안 붙인 버튼이 안내만 내는지 확인한다 |
| `capture_window.py` | main.py 를 실제로 띄워 창 그림(`program-window.png`)을 찍는다. **화면을 긁지 않고 PrintWindow 로 찍는다** — 사내 PC 는 화면에 이름·소속·IP 워터마크가 깔려 있어 화면 캡처를 쓰면 그게 같이 박힌다 |
| `program-window.png` | STEP 0 페이지에 base64 로 박히는 창 그림. `main.py` 의 창 구성을 바꿨으면 다시 찍을 것 |
| `check_page.py` | 태그 짝, 페이지·체크박스 수, 프롬프트 안의 역슬래시, 낡은 표현, 박혀있는 main.py 일치 |

## 고칠 때

**단계 내용(프롬프트, 성공 기준)** → `steps.py`. 항목별 뜻은 파일 맨 위 설명에 있다.

**사전 준비 페이지** → `prep.html`.

**The APPS 안내 페이지, 스타일, 페이지 이동** → `build_page.py` 안의 `APPS_PAGE`,
`STYLE`, `SCRIPT`.

**정답 코드** → `../news-report-bot/main.py`. 페이지의 "정답 코드 파일 받기" 버튼은 이
파일을 통째로 base64 로 박아서 내려준다. 그래서 **main.py 를 고쳤으면 `build_page.py` 를
다시 실행해야** 페이지에 반영된다 (`check_page.py` 가 이 불일치를 잡는다).

## 프롬프트를 쓸 때 지키는 것

실제 사내 PC 에서 끝까지 돌려보며 부딪힌 것들이다. 되돌리면 같은 곳에서 다시 막힌다.

- **코딩을 모르는 사람이 쓸 만한 말투로.** 기술 용어를 조목조목 나열하면 안 된다.
- **꼭 정확해야 하는 기술 사항은 번호를 매겨 구체적으로.** 사내망 SSL, DART 함정,
  아웃룩 COM 이 그렇다. 뭉뚱그려 쓰면 AI 가 엉뚱한 걸 고르고 **에러 없이 조용히 틀린다** —
  회사명을 DART 요청에 실어 보내고도 「완료」 라고 찍은 적이 있다.
- **프롬프트에 역슬래시를 넣지 않는다.** 사내 AI 툴이 `.py` 파일을 만들 때 역슬래시를
  전부 날려버려 문자열이 찢어지고 프로그램이 아예 안 열린 사례가 있다. 그래서 모든
  프롬프트 끝에 "역슬래시를 쓰지 말고 줄바꿈은 `chr(10)`" 이라는 문구가 붙는다.
  `역슬래시(\)` 처럼 기호를 그대로 쓰는 것도 피한다 — 사내 AI 툴 화면에서 `$` 로 깨진다.
- **수집량·출력량 상한을 빼지 않는다.** 뉴스는 키워드당 10건, DART 는 회사명이 없으면
  50건. 결과 칸에는 방금 가져온 것만 쓴다. 이게 없으면 결과 칸이 수천 줄이 되어 창이 멈춘다.
- **문장이 따옴표로 끝나지 않게.** `steps.py` 의 프롬프트는 삼중 따옴표 문자열이라
  `..."` 로 끝나면 문법이 깨진다. 인용은 `「」` 를 쓴다.

## 확인

`check_page.py` 를 통과시킨 뒤, `<script>` 안의 문법과 실제 동작도 본다.

```
python3 - <<'EOF'
import io, re
s = io.open("DART 뉴스 크롤링 및 메일발송 프로그램 만들기.html", encoding="utf-8").read()
io.open("/tmp/page.js", "w", encoding="utf-8").write(
    "\n".join(re.findall(r"<script>(.*?)</script>", s, re.S)))
EOF
node --check /tmp/page.js
```

그다음 브라우저로 열어 페이지 이동(`#s0`, `#s2`, `#apps`)과 체크박스 저장을 눌러본다.
