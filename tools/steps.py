"""실습 페이지의 단계별 내용 — 이 파일이 원본이다.

프롬프트·성공 기준을 여기서 고치고 build_page.py 를 실행하면 저장소 루트의 실습
HTML 이 다시 만들어진다. HTML 을 직접 고치면 다음 실행에 덮어써진다.

이 파일은 2026-09-08 에 전면 재작성됐다. 아주 단순한 일반인 말투 프롬프트에서
시작해 7라운드에 걸쳐 실제로 프로그램을 만들고 사내 PC 에서 돌려보며, 막힐 때마다
그 원인을 프롬프트에 반영하는 식으로 만들었다. 뉴스 수집 → DART 공시 수집 →
아웃룩 자동 발송까지 실제로 도달한 것을 확인했다. 근거와 측정값은 저장소 루트의
강사가-알려줄것.md 에 있다.

이 과정의 범위는 "기능이 되는가" 다 — 뉴스가 모이는가, 공시가 모이는가, 메일이
가는가. 기사 품질(중복 기사, 블로그 섞임, 언론사명 정리)은 의도적으로 다루지 않는다.

각 항목의 뜻
  part          1=수집 실습, 2=보고서 실습, 3=메일 발송 실습
  num / id      화면에 보이는 번호 / 내부 식별자(URL 해시)
  time          배정 시간 (README 진행표의 합계와 맞춰야 한다)
  lib           그 단계에서 pip 로 받아야 하는 것 (없으면 None)
  desc          수강생에게 이 단계가 무엇인지 설명하는 문단
  todo          (선택) 이 단계에서 만들 것을 명사형으로 끊어 쓴 목록. 있으면 desc 대신
                번호 목록으로 나온다 — 줄글보다 눈에 빨리 들어온다
  prompt        AI 에게 그대로 붙여넣는 본문. 파일 요청 문구는 build_page.py 가
                뒤에 자동으로 붙이므로 여기 쓰지 않는다
  need_install  프롬프트 위에 띄우는 설치 안내
  trouble       (선택) 막혔을 때 이어서 넣을 프롬프트 dict(summary, body, prompt,
                items=왜 그런지 목록, flow=순서 그림)
  criteria      성공 기준 체크리스트 — 눈으로 확인할 수 있는 것만 쓴다

프롬프트를 쓸 때 지키는 것 (라운드를 돌면서 얻은 것들이다)
  · 코딩을 모르는 사람이 실제로 쓸 만한 말투. 기술 용어를 나열하지 않는다
  · 애매하게 쓰면 AI 는 에러 없이 조용히 틀린다. 꼭 정확해야 하는 기술 사항은
    번호를 매겨 구체적으로 적는다
  · 어느 라이브러리를 쓸지는 AI 가 고르게 둔다. requests 를 고르면 사내망에서 첫 접속부터
    죽는데, STEP 1 은 일부러 그 에러를 겪고 「인증서 오류가 뜨면?」 칸에서 설명 듣고 고친다
  · "에러를 화면에 사람 말로" 와 "0건일 때 왜 0건인지" 를 매 단계에 넣는다.
    이 실습의 최대 적은 에러가 아니라 조용한 실패다
  · 수집량·출력량 상한을 빼지 않는다. 없으면 결과 칸이 수천 줄이 되어 창이 멈춘다
  · 문장 끝이 따옴표로 끝나면 안 된다 (파이썬 삼중 따옴표 문자열이 깨진다)
  · 프롬프트에 역슬래시를 넣지 않는다 (check_page.py 가 검사한다)
"""

STEPS = [
    dict(
        part=1, num="0", id="s0", time="10분",
        title="프로그램 창 만들기",
        lib=None,
        desc="",
        todo=[
            "터미널 대신 더블클릭으로 뜨는 프로그램 창 띄우기",
            "입력 칸 세 개 만들기 — 검색어(회사명) · 메일 받을 사람 · DART 인증키",
            "버튼 다섯 개 만들기 — 뉴스 수집 · DART 수집 · 보고서 만들기 · 메일 보내기 · 전체 실행",
            "결과 칸 세 개 만들기 — 뉴스 · DART · 진행 상황",
            "입력값 저장하기 — 창을 닫았다 열어도 그대로 남게",
            "에러가 보이는 화면 만들기 — 오류를 봐야 고칠 수 있다",
        ],
        prompt="""파이썬으로 뉴스와 DART 공시를 모아 메일로 보내는 프로그램을 만들 거야. 나는 코딩을 전혀
모르고, 윈도우 PC 에 아웃룩으로 회사 메일을 로그인해둔 상태야.

터미널이 아니라 더블클릭하면 창이 뜨는 프로그램으로 만들어줘. 아래를 순서대로.

1. 입력 칸 세 개 — 검색어(회사명, 쉼표로 여러 개), 메일 받을 사람, DART 인증키
2. 입력값 저장 — 창을 닫았다 다시 열어도 그대로
3. 버튼 다섯 개 — "뉴스 수집하기", "DART 수집하기", "보고서 만들기", "메일 보내기", "전체 실행"
4. 결과 칸 세 개 — "뉴스 수집 결과", "DART 수집 결과", 그리고 진행 상황과 에러가 들어갈 작은
   "진행 상황" 칸. 수집 버튼은 각자 자기 칸에만 쓰고, 세 칸 다 스크롤되고 글자는 고칠 수 없게
5. 제목 클릭으로 원문 열기 — 파란색 밑줄, 마우스 올리면 손가락 모양
6. 기사·공시 한 건을 담을 형태 — 출처, 제목, 원문 링크, 날짜와 시각, 짧은 메모.
   날짜는 한국 시간 "09/08 14:30" 형식, 시각을 모르면 날짜만
7. 창이 열리면 진행 상황 칸 첫 줄에 파이썬 버전 한 줄

검색어 칸 하나로 뉴스 검색과 DART 회사 찾기를 같이 쓴다. 둘 다 회사명이라 칸을 나눌 이유가 없어.

앞으로 모든 단계에서 지킬 규칙 넷. 이걸 안 지키면 나는 뭐가 잘못됐는지 알 수가 없어.

1. 조용히 실패 금지 — 프로그램이 아는 모든 실패를 "진행 상황" 칸에 코딩 모르는 사람이 읽을
   수 있는 말로. 터미널에만 찍히면 나는 볼 수가 없어
2. 0건이면 이유 구분 — 그냥 "0건" 은 쓸모가 없어
3. 창 안 멈추게 — 버튼 작업은 뒤에서 돌리고, 작업 중에는 버튼이 안 눌리다가 끝나면 다시 눌리게
4. 수집량·출력량 상한 — 상한이 없으면 결과 칸이 수천 줄이 되어 창이 멈춰. 화면에는 방금
   가져온 것만 앞에서 열 건, 나머지는 "이 밖에 몇 건 더" 한 줄

지금은 버튼을 눌러도 진행 상황 칸에 안내만 나오면 돼.""",
        need_install=None,
        criteria=[
            "받은 파일을 AI가 알려준 대로 저장하고 실행하면, 검은 터미널 창이 아니라 진짜 프로그램 창이 뜬다",
            "결과 보는 곳이 \"뉴스 수집 결과\" / \"DART 수집 결과\" / \"진행 상황\" 세 칸으로 나뉘어 있다",
        ],
    ),

    dict(
        part=1, num="1", id="s1", time="15분",
        title="뉴스 수집 버튼 연결하기",
        lib="feedparser",
        desc="",
        todo=[
            "구글 뉴스에서 기사 가져오기 — 인증키 없이",
            "검색어는 쉼표(,)로만 구분 — 앞뒤 띄어쓰기는 상관없음",
            "검색어 하나당 최신 10건까지만",
            "날짜를 한국 시간으로 바꾸기",
            "제목 눌러 원문 열기",
            "못 가져온 경우와 기사가 없는 경우 구분해서 알리기",
        ],
        prompt=""""뉴스 수집하기" 버튼이 구글 뉴스에서 기사를 가져오게 해줘. 인증키 없이 검색 결과를 받아올 수
있어.

1. 검색어 칸은 쉼표(,)로만 나누고 앞뒤 띄어쓰기는 지우기 — 이름 안의 띄어쓰기는 그대로 둬
   (예: "삼성전자, SK 하이닉스" 는 검색어 2개)
2. 나눈 검색어마다 한국 기준으로 검색, 검색어당 최신 10건까지만
3. 출처는 "뉴스", 날짜는 한국 시간으로 변환 — 받아온 시간이 세계 표준시라 그대로 쓰면 아홉
   시간 어긋나
4. 뉴스 칸에 방금 가져온 것만 최신순, 제목 클릭하면 원문 열림
5. 검색어마다 "몇 건 가져왔고 검색 결과 전체는 몇 건" 을 진행 상황 칸에
6. 검색어 칸이 비어있으면 "검색어가 없어 건너뜀" 만 알리고 끝
7. 못 가져올 때는 두 경우 구분해서 알리고 다음 검색어로 계속 — 회사 네트워크가 막아서 아예 못
   받은 경우, 받아왔는데 걸리는 기사가 없는 경우
8. 버튼 누른 동안 창 안 멈추게""",
        need_install="pip install feedparser",
        trouble=dict(
            summary="인증서 오류 (CERTIFICATE_VERIFY_FAILED) 가 뜨면?",
            # 왜 막히는지 그림 — 페이지에 그대로 들어가는 HTML
            visual="""<div class="cert">
        <div class="cert-path">
          <span class="pv-node">파이썬 프로그램</span>
          <span class="pv-line right"><em>접속</em></span>
          <span class="pv-node src api">회사 보안장비<small>회사 도장을 찍어 넘김</small></span>
          <span class="pv-line right"><em>&nbsp;</em></span>
          <span class="pv-node">news.google.com</span>
        </div>
        <div class="cert-lanes">
          <div class="cert-lane bad">
            <p class="cert-who"><code>requests</code></p>
            <p class="cert-box">자기 목록을 본다<small>설치할 때 딸려온 목록</small></p>
            <p class="cert-box">회사 도장이 없다</p>
            <p class="cert-box cert-end">✕ 연결 끊음<small>CERTIFICATE_VERIFY_FAILED</small></p>
          </div>
          <div class="cert-lane good">
            <p class="cert-who"><code>feedparser</code> <small>안에서 urllib</small></p>
            <p class="cert-box">윈도우 목록을 본다<small>회사가 PC 줄 때 회사 도장을 넣어둠</small></p>
            <p class="cert-box">회사 도장이 있다</p>
            <p class="cert-box cert-end">✓ 통과<small>RSS 목록을 받는다</small></p>
          </div>
        </div>
        <div class="cycle cert-when">
          <span class="cycle-label">순서</span>
          <span class="chip">접속 요청</span><span class="carrow">→</span>
          <span class="chip hl">도장 확인</span><span class="carrow">→</span>
          <span class="chip">통로 열림</span><span class="carrow">→</span>
          <span class="chip next">데이터 받음</span>
        </div>
        <p class="tiny cert-note">인증서는 <strong>도장 확인</strong>에서 한 번만 본다 — 여기서 막히면 데이터는 한 줄도 안 온다.
          윈도우 목록 직접 보기: 윈도우 + R → <code class="cmd">certmgr.msc</code> → 신뢰할 수 있는 루트 인증 기관</p>
      </div>""",
            body="이 에러가 떴다면 AI 가 <code>requests</code> 를 쓴 것이다. 회사망에서는 자주 일어난다 — "
                 "같은 프롬프트를 줘도 AI 가 어느 부품을 고르느냐에 따라 성패가 갈린다.",
            prompt="""CERTIFICATE_VERIFY_FAILED 에러가 나. 지금 코드가 인터넷에서 자료를 받아올 때 requests 를
쓰고 있는지 봐줘. 쓰고 있으면 feedparser 로 바꿔줘. feedparser 는 파이썬에 원래 들어있는
urllib 을 쓰기 때문에 윈도우 인증서 저장소를 보고, 그래서 우리 회사 환경에서 그냥 돼.
인증서 검증을 끄는 방법은 쓰지 말아줘.""",
        ),
        criteria=[
            "키워드를 하나 넣고 버튼을 누르면 뉴스 칸에 기사 제목이 나온다",
            "제목을 누르면 브라우저에서 그 기사가 열린다",
            "진행 상황 칸에 \"몇 건 가져왔고 검색 결과는 몇 건\" 이 찍힌다",
        ],
    ),

    dict(
        part=1, num="2", id="s2", time="20분",
        title="DART 수집 버튼 연결하기",
        # 할 일 목록 아래에 넣는 그림 — 페이지에 그대로 들어가는 HTML
        visual="""<div class="ways">
      <p class="ways-title">DART 에서 회사 공시를 고르는 두 가지 방법</p>
      <div class="cert-lanes">
        <div class="cert-lane good">
          <p class="cert-who">A · 전부 받고 내가 거르기 <span class="ways-tag">실습에서 쓰는 방법</span></p>
          <p class="cert-box">기간만 넣어 요청<small>회사 이름은 넣어도 무시된다</small></p>
          <p class="cert-box">그 주 모든 회사 공시가 온다<small>약 2,500건 · 요청 25회</small></p>
          <p class="cert-box cert-end">프로그램이 회사 이름으로 거르기<small>→ 현대건설 3건</small></p>
          <ul class="ways-pros">
            <li class="up">단계가 적어 AI 가 덜 틀린다</li>
            <li class="up">「삼성전자」 로 계열사까지 걸린다</li>
            <li class="down">한 번에 3개월까지만</li>
            <li class="down">요청 횟수가 많다</li>
          </ul>
        </div>
        <div class="cert-lane alt">
          <p class="cert-who">B · 회사코드로 바로 찾기 <span class="ways-tag alt">이렇게도 된다</span></p>
          <a class="cert-box corp-card" href="downloads/dart-corpcode-20260930.csv" download="DART_회사고유번호.csv">회사 목록 받기 <span class="corp-dl-icon">⬇</span><small>누르면 CSV — 회사명 · 고유번호 · 약 12만 개</small><small class="corp-dl-hint">2026-09-30 기준</small></a>
          <p class="cert-box">이름으로 고유번호 찾기<small>현대건설 → 00164478</small></p>
          <p class="cert-box cert-end">고유번호로 요청<small>→ 그 회사 공시만 · 3개월치 53건 · 요청 1회</small></p>
          <ul class="ways-pros">
            <li class="up">요청이 적다</li>
            <li class="up">기간을 길게 (1999년부터)</li>
            <li class="down">이름이 정확히 같아야 한다</li>
            <li class="down">같은 이름 회사가 여럿일 수 있다</li>
          </ul>
        </div>
      </div>
      <p class="tiny ways-note">B 로 하고 싶으면 프롬프트에 「회사 이름으로 DART 고유번호 목록 파일에서 번호를 찾아서,
        그 번호(corp_code)로 공시를 조회해줘」 를 넣는다.</p>
    </div>
""",
        lib=None,
        desc="",
        todo=[
            "전자공시에서 최근 일주일 공시 가져오기",
            "마지막 페이지까지 넘겨가며 다 받기 — 100건씩 약 30페이지",
            "회사 걸러내기 — DART 에 맡기지 말고, 받은 뒤 프로그램이 직접",
            "원문 주소 정확히 만들기 — 틀리면 「거부」 페이지가 열린다",
            "0건인 이유 구분해서 알리기 — 공시 없음 · 그 회사 없음 · 인증키 문제",
            "회사별 건수 한 줄로 요약하기",
        ],
        prompt=""""DART 수집하기" 버튼이 전자공시시스템(DART)에서 최근 일주일 공시를 가져오게 해줘.

1. 회사 찾기는 뉴스와 같은 검색어 칸 사용 (쉼표로 나누는 방식도 같게) — 적은 이름이 들어간
   공시만 남기고, 정확히 같지 않아도 그 글자가 들어가면 걸리게. 띄어쓰기는 양쪽 다 빼고 비교
   ("SK 하이닉스" 와 "SK하이닉스" 가 같게)
2. 검색어 칸이 비어있으면 최신 50건만 담고 "전체 몇 건 중 50건만 담았다" 고 알리기
3. 담는 형태 — 제목은 "[회사명] 보고서 이름", 링크는 아래 형식의 원문 주소, 날짜는 접수일,
   메모는 제출인, 출처는 "DART"
4. 0건이면 이유 구분 — 그 기간에 공시가 아예 없었는지, 공시는 있었는데 그 회사 것이
   없었는지, 인증키 문제인지. 회사 것이 없던 경우는 "공시 몇 건을 살펴봤는데 그중 그 회사
   건은 없었다" 처럼 살펴본 전체 건수도 함께
5. 회사를 여러 개 적었으면 "GS건설 1건 / 삼성물산 1건" 처럼 회사별 건수 한 줄 요약
6. DART 칸에 방금 가져온 것만 최신순, 제목 클릭하면 원문 열림
7. 인증키가 없으면 "DART 인증키가 없어 건너뜀" 만 알리고 넘어가기
8. 버튼 누른 동안 창 안 멈추게

DART 는 함정이 넷 있어. 놓치면 결과가 조용히 틀리니 그대로 지켜줘.

1. 회사 이름으로 찾아달라고 요청하는 기능이 없다 — 회사 이름을 같이 보내도 에러가 나지 않고
   정상 이라고 응답이 오는데, 실제로는 그 값을 무시하고 전체를 준다. 있지도 않은 회사 이름을
   보내도 정상 이라고 온다. 그러니 요청으로 거르려 하지 말고, 그 기간 공시를 끝까지 받은 다음
   프로그램에서 직접 골라내
2. 한 번에 받을 수 있는 최대 건수는 100건 — 그보다 크게 요청해도 에러 없이 100건만 온다.
   응답에 들어있는 전체 페이지 수를 보고 마지막 페이지까지 넘겨가며 다 받아. 최근 일주일이면
   보통 2,700건 전후에 28페이지이고 15초쯤 걸려. 지금 몇 페이지째인지 진행 상황 칸에 적어줘.
   중간에서 끊으면 뒷페이지에 있던 그 회사 공시를 놓치고 없다고 하게 돼
3. 목록 받는 곳과 문서 여는 곳이 다르다 — 목록은 opendart.fss.or.kr, 문서는
   dart.fss.or.kr 이다. 원문 주소는 dart.fss.or.kr/dsaf001/main.do?rcpNo=접수번호 형식이고,
   받은 자료에서 접수번호 항목의 이름은 rcept_no 지만 주소에 쓸 이름은 rcpNo 다. 틀리면
   「거부」 라고만 뜨는 페이지가 열려
4. 응답의 상태 값으로 이유를 구분 — 000 은 정상, 013 은 그 기간에 공시가 아예 없음(주말이나
   공휴일이면 정상), 010 과 011 은 인증키 문제, 020 은 요청 한도 초과""",
        need_install=None,
        criteria=[
            "검색어 칸에 회사명을 적었으면 DART 칸에 그 회사 공시만 나온다",
            "제목을 누르면 브라우저에 공시 원문이 열린다 (「거부」 라고만 뜨면 주소 형식이 틀린 것이다)",
        ],
    ),

    dict(
        part=2, num="3", id="s3", time="15분",
        title="HTML 보고서 만들기",
        lib=None,
        desc="",
        todo=[
            "뉴스 수집 · DART 수집 결과를 HTML 보고서로 작성",
            "「보고서 만들기」 누르면 프로그램이 있는 폴더에 HTML 파일 생성",
            "만든 보고서를 브라우저에 바로 띄우기",
        ],
        prompt="""앞에서 만들어둔 "보고서 만들기" 버튼이 동작하게 해줘. 모은 것을 보고서 한 장으로 만들어
파일로 저장하고 브라우저로 열어주는 버튼이야.

먼저 합칠 때 정리.

1. 제목이 비어있는 항목 빼기
2. 제목이 같으면 링크가 달라도 같은 소식으로 보고 하나만 남기기
3. 최신순 정렬, 날짜 없는 것은 맨 뒤로
4. 시각을 모르는 항목은 날짜만 — 0시로 채우면 같은 날 뉴스보다 늘 아래로 밀린다
5. 수집 버튼 둘 다 이 정리를 거치게 (각자 자기 칸에 보여주는 건 그대로)

보고서 내용.

1. 맨 위에 "오늘의 이슈 리포트", 오늘 날짜(한국어, 예: 2026년 09월 22일), 총 건수,
   "뉴스 몇 건 · DART 몇 건" 요약 한 줄
2. 본문은 출처별로 나누기 — 뉴스끼리 공시끼리 묶고 소제목 옆에 건수, 그 안에서 최신순
3. 항목마다 제목(누르면 원문으로 가는 링크)과 날짜
4. 전체 40건까지, 더 있으면 "이 밖에 몇 건이 더 있습니다"
5. 디자인은 별도 파일 없이 본문 안에 직접 — 다음 단계에서 이 보고서를 메일 본문으로 그대로
   쓸 건데 메일은 디자인 파일을 불러올 수 없어

파일 저장과 열기.

1. 프로그램이 있는 폴더에 저장
2. 이름에 날짜와 시각을 넣어 여러 번 눌러도 덮어쓰지 않게
3. 저장 후 브라우저로 바로 열기
4. 진행 상황 칸에 파일 이름과 담은 건수 알리기
5. 모은 항목이 없으면 "보고서로 만들 항목이 없습니다. 먼저 수집하세요" 만 알리고 끝

브라우저로 여는 부분만 조심해줘. 파일 경로를 주소로 바꿀 때 문자열을 이어붙이지 마. 폴더
이름에 샵 기호나 공백이 들어있으면 주소 문법으로 해석돼 엉뚱한 곳이 열려 — 실제로 폴더
이름에 샵이 있어서 보고서 대신 D 드라이브 폴더 목록이 열린 적이 있어. pathlib 의 Path 로
경로를 감싸고 as_uri() 로 주소를 만들어줘. 그러면 특수문자가 알아서 바뀐다.""",
        need_install=None,
        criteria=[
            "\"보고서 만들기\" 를 누르면 브라우저에 보고서가 열린다 (폴더 목록이 열리면 주소 만드는 방식이 틀린 것이다)",
            "프로그램이 있는 폴더에 날짜가 들어간 HTML 파일이 생긴다",
        ],
    ),

    dict(
        part=3, num="4", id="s4", time="20분",
        title="메일 보내기 — 아웃룩 메일 자동 작성 · 전송",
        lib="pywin32 (윈도우 전용)",
        desc="",
        todo=[
            "「메일 보내기」 를 누르면 아웃룩 메일을 자동으로 작성해서 전송까지 — 로그인된 아웃룩이라 비밀번호 없이",
            "메일 본문은 앞에서 만든 보고서로",
            "메일 속 제목을 누르면 원문이 열리게 — 글자가 아니라 링크로",
            "보낼 수 없는 경우 안내하기 — 항목 없음 · 받는 사람 없음 · 설치 안 됨",
            "전송이 막히면 작성된 메일 창을 열어주기 — 「보내기」 만 누르면 되게",
        ],
        prompt=""""메일 보내기" 버튼이 앞 단계에서 만든 그 보고서를 본문으로 그대로 써서 실제 발송하게 해줘.
보고서를 다시 만들지 말고 같은 걸 쓰면 돼.

1. 받는 사람이 여러 명이면 전부
2. 제목은 "[이슈 리포트] 오늘 날짜 · N건" 형식
3. 알리고 끝내는 경우 넷 — 모은 항목이 없을 때("보낼 항목이 없습니다. 먼저 수집하세요"),
   받는 사람이 비었을 때, 윈도우가 아닌 컴퓨터일 때, 아웃룩 조작에 필요한 게 설치 안 됐을
   때(설치 방법도 함께)
4. 자동 발송이 안 될 때 대안 — 회사에서 "새 아웃룩" 을 쓰면 이 방식 자체가 지원되지 않아.
   그때는 제목·받는 사람·본문이 채워진 메일 창을 열어줘서 내가 보내기만 누르면 되게
5. 자동 발송 성공하면 "자동 발송 완료", 안 되면 그 사실을 알린 뒤 메일 창을 열고
   "보내기만 누르면 된다" 고 알리기
6. 버튼 누른 동안 창 안 멈추게

보내는 방식은 다섯 가지를 지켜줘. 하나라도 빠지면 실제로 막혀.

1. SMTP 로 보내지 마 — 회사 보안장비가 암호화 통신으로 올라가는 단계에서 연결을 끊어버려서,
   포트는 열려 있는데 응답이 오지 않고 몇십 초 매달린 뒤 죽어. 에러 메시지도 제대로 안 나와.
   게다가 SMTP 는 계정 비밀번호를 프로그램에 적어야 해
2. 윈도우에 이미 로그인되어 있는 데스크톱 아웃룩을 조작 — pywin32 의 win32com.client 로
   Outlook.Application 을 붙잡고, CreateItem(0) 으로 새 메일을 만들어 받는 사람과 제목과
   본문을 채운 뒤 Send() 로 보내면 돼. 이미 로그인된 아웃룩을 쓰니 비밀번호가 필요 없어
3. 본문은 반드시 HTMLBody 에 — Body 에 넣으면 링크가 「제목 다음에 주소가 따라오는」 글자로
   깨져서 눌러도 열리지 않아
4. 버튼 작업을 뒤에서 돌리니, 그 작업 안에서 아웃룩을 붙잡기 전에 pythoncom 의 CoInitialize
   를 먼저 불러줘. 빠뜨리면 자동 발송이 com_error 「CoInitialize 가 호출되지 않았습니다」 로
   실패해. 일이 끝나면 CoUninitialize 로 정리
5. Send 를 부른 뒤에는 그 메일 객체를 다시 건드리지 마 — 보낸 편지함으로 옮겨져서 받는 사람
   주소를 읽기만 해도 「항목이 삭제되었거나 옮겨졌습니다」 오류가 나. 그러면 실제로는
   보내놓고도 실패로 처리돼 메일 창이 한 번 더 떠. 로그에 쓸 값은 Send 전에 미리 변수에 담아둬""",
        need_install="pip install pywin32",
        criteria=[
            "아웃룩으로 메일이 도착했는지 확인",
            "메일 내용에 뉴스와 DART 정보가 있는지 확인",
        ],
    ),

    dict(
        part=3, num="5", id="s5", time="10분",
        title="통합 실행",
        lib=None,
        desc="",
        todo=[
            "한 번에 실행하기 — 뉴스, DART, 보고서, 메일 순서로",
            "수집된 게 없으면 보고서와 메일 건너뛰기",
            "예상 못 한 문제도 화면에 알리기",
        ],
        prompt=""""전체 실행" 버튼을 완성해줘.

1. 누르면 뉴스 수집, DART 수집, 보고서 만들기, 메일 보내기를 순서대로 한 번에
2. 수집된 게 없으면 보고서와 메일은 건너뛰고 진행 상황 칸에 알리기
3. 어떤 작업이 진행 중이면 다른 버튼도 잠시 안 눌리다가 끝나면 다시 눌리게
4. 진행 중에 또 누르면 "아직 앞의 작업이 끝나지 않았습니다" 알리기
5. 어디서든 예상 못 한 문제가 생겨도 프로그램이 죽지 않고 진행 상황 칸에 무슨 문제인지 적기

여기까지 되면 완성이야.""",
        need_install=None,
        criteria=[
            "\"전체 실행\" 을 누르면 뉴스 → DART → 보고서 → 메일까지 한 번에 진행된다",
            "진행 중에는 다른 버튼이 눌리지 않고, 끝나면 다시 눌린다",
            "메일이 도착하고 그 안에 뉴스와 공시가 모두 들어있다",
        ],
    ),

    # ── 알파 실습 · 고도화 — 사례(수주레이더) 설명 + 프롬프트만, 실습은 자율 ──
    dict(
        part=4, num="6", id="s6", time="20분",
        title="목적에 맞는 수집",
        # 실전 사례(수주레이더)는 이 단계를 어떻게 했나 — 페이지에 그대로 들어가는 HTML
        visual="""<div class="xf"><p class="xf-title"><span class="xf-badge">실전 사례에서는</span>영업에 쓸 신호만, 출처를 넓혀서 모은다</p><div class="xf-cmp"><div class="xf-side"><span>기본 실습 · 우리가 만든 것</span>구글 뉴스 RSS 하나 + DART 목록에서 회사 이름으로 거르기</div><div class="xf-arrow">→</div><div class="xf-side real"><span>실전 사례 · 수주레이더</span>매체 RSS 44개 직접 + DART 시설투자 공시 원문 + 나라장터 시설공사 + 식약처 GMP</div></div><p class="xf-h">과정 — 실제 코드 흐름</p><figure class="dg"><div class="dg-scroll"><svg viewBox="0 0 960 520" role="img" aria-label="출처 네 곳이 각자 받기와 거르기를 거쳐 파일로 쌓이는 수집 흐름"><defs><marker id="mk-c" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk " d="M0,0 L10,5 L0,10 z"/></marker><marker id="mk-c-k" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk k" d="M0,0 L10,5 L0,10 z"/></marker><marker id="mk-c-drop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk drop" d="M0,0 L10,5 L0,10 z"/></marker></defs><text class="col" x="120" y="18" text-anchor="middle">어디서</text><text class="col" x="360" y="18" text-anchor="middle">받아오기</text><text class="col" x="615" y="18" text-anchor="middle">거르기</text><text class="col" x="850" y="18" text-anchor="middle">모아두는 곳</text><rect class="lane" x="8" y="30" width="944" height="92" rx="10"/><text class="lane-t" x="20" y="48">매일 06:00</text><rect class="bx " x="20" y="52" width="200" height="58" rx="7"/><text class="h " x="120" y="77.5" text-anchor="middle">언론사 44곳 새 기사</text><text class="s" x="120" y="92.5" text-anchor="middle">종합·경제·산업 전문지</text><rect class="bx " x="250" y="52" width="220" height="58" rx="7"/><text class="h " x="360" y="77.5" text-anchor="middle">제목·요약 받기</text><text class="s" x="360" y="92.5" text-anchor="middle">빠지지 않게 이틀치씩 겹쳐서</text><rect class="bx " x="500" y="52" width="230" height="58" rx="7"/><text class="h " x="615" y="70.0" text-anchor="middle">1차 거르기</text><text class="s" x="615" y="85.0" text-anchor="middle">「착공+공장」 처럼 짝이 맞아야 통과</text><text class="s" x="615" y="100.0" text-anchor="middle">주택·관급 같은 말이 있으면 탈락</text><rect class="bx out" x="760" y="52" width="180" height="58" rx="7"/><text class="h " x="850" y="70.0" text-anchor="middle">뉴스 보관함</text><text class="s" x="850" y="85.0" text-anchor="middle">같은 기사는 한 번만</text><text class="s" x="850" y="100.0" text-anchor="middle">10일치 보관</text><polyline class="ln " points="220,81 246,81" marker-end="url(#mk-c)"/><polyline class="ln " points="470,81 496,81" marker-end="url(#mk-c)"/><polyline class="ln " points="730,81 756,81" marker-end="url(#mk-c)"/><rect class="lane" x="8" y="132" width="944" height="380" rx="10"/><text class="lane-t" x="20" y="150">금요일 06:40 — 한 주치를 한 번에</text><polyline class="ln " points="850,110 850,148" marker-end="url(#mk-c)"/><text class="al " x="876" y="140" text-anchor="middle">7일치</text><rect class="bx out" x="760" y="152" width="180" height="58" rx="7"/><text class="h " x="850" y="177.5" text-anchor="middle">한 주치 뉴스 묶음</text><text class="s" x="850" y="192.5" text-anchor="middle">며칠에 걸쳐 겹친 기사 정리</text><rect class="bx k" x="20" y="232" width="200" height="58" rx="7"/><text class="h " x="120" y="257.5" text-anchor="middle">DART 공시</text><text class="s" x="120" y="272.5" text-anchor="middle">회사가 수시로 내는 공시</text><rect class="bx " x="250" y="232" width="220" height="58" rx="7"/><text class="h " x="360" y="250.0" text-anchor="middle">공시 제목으로 고르기</text><text class="s" x="360" y="265.0" text-anchor="middle">시설투자 · 공장 신축 · 공급계약</text><text class="s" x="360" y="280.0" text-anchor="middle">합병 · 주식 매입은 뺌</text><rect class="bx k" x="500" y="232" width="230" height="58" rx="7"/><text class="h " x="615" y="250.0" text-anchor="middle">공시 본문까지 읽기</text><text class="s" x="615" y="265.0" text-anchor="middle">앞부분 3,000자를 받아서</text><text class="s" x="615" y="280.0" text-anchor="middle">장비만 사는 건 · 기존 건물 매입은 뺌</text><rect class="bx out" x="760" y="232" width="180" height="58" rx="7"/><text class="h " x="850" y="250.0" text-anchor="middle">공시 목록</text><text class="s" x="850" y="265.0" text-anchor="middle">투자금액·목적·기간은</text><text class="s" x="850" y="280.0" text-anchor="middle">보고서 만들 때 읽어냄</text><polyline class="ln " points="220,261 246,261" marker-end="url(#mk-c)"/><polyline class="ln " points="470,261 496,261" marker-end="url(#mk-c)"/><polyline class="ln " points="730,261 756,261" marker-end="url(#mk-c)"/><rect class="bx k" x="20" y="322" width="200" height="58" rx="7"/><text class="h " x="120" y="347.5" text-anchor="middle">나라장터</text><text class="s" x="120" y="362.5" text-anchor="middle">공공기관 시설공사 입찰공고</text><rect class="bx " x="250" y="322" width="220" height="58" rx="7"/><text class="h " x="360" y="347.5" text-anchor="middle">공고 받기</text><text class="s" x="360" y="362.5" text-anchor="middle">한 주치를 한 번에</text><rect class="bx " x="500" y="322" width="230" height="58" rx="7"/><text class="h " x="615" y="340.0" text-anchor="middle">공고명으로 고르기</text><text class="s" x="615" y="355.0" text-anchor="middle">「반도체」 「GMP」 같은 말이 있거나</text><text class="s" x="615" y="370.0" text-anchor="middle">「공장」+산업 이름이 함께 있으면</text><rect class="bx out" x="760" y="322" width="180" height="58" rx="7"/><text class="h " x="850" y="355.0" text-anchor="middle">입찰공고 목록</text><polyline class="ln " points="220,351 246,351" marker-end="url(#mk-c)"/><polyline class="ln " points="470,351 496,351" marker-end="url(#mk-c)"/><polyline class="ln " points="730,351 756,351" marker-end="url(#mk-c)"/><rect class="bx k" x="20" y="412" width="200" height="58" rx="7"/><text class="h " x="120" y="437.5" text-anchor="middle">식약처 GMP</text><text class="s" x="120" y="452.5" text-anchor="middle">의약품 제조 허가 공장 명단</text><rect class="bx " x="250" y="412" width="220" height="58" rx="7"/><text class="h " x="360" y="437.5" text-anchor="middle">이번 주 명단 받기</text><text class="s" x="360" y="452.5" text-anchor="middle">지난주 명단은 따로 보관</text><rect class="bx " x="500" y="412" width="230" height="58" rx="7"/><text class="h " x="615" y="437.5" text-anchor="middle">지난주와 비교</text><text class="s" x="615" y="452.5" text-anchor="middle">업체·주소·제품이 같은지</text><rect class="bx out" x="760" y="412" width="180" height="58" rx="7"/><text class="h " x="850" y="437.5" text-anchor="middle">GMP 공장 목록</text><text class="s" x="850" y="452.5" text-anchor="middle">새로 생긴 곳 표시</text><polyline class="ln " points="220,441 246,441" marker-end="url(#mk-c)"/><polyline class="ln " points="470,441 496,441" marker-end="url(#mk-c)"/><polyline class="ln " points="730,441 756,441" marker-end="url(#mk-c)"/><text class="note" x="500" y="500" text-anchor="start">네 목록 → 점수 매기기 · 보고서 만들기로 (STEP 7 · 8)</text></svg></div><figcaption>뉴스는 매일 조금씩 쌓아두고, 날짜로 조회되는 DART·나라장터·식약처는 금요일에 7일치를 한 번에 받는다. 주황 테두리는 기본 실습에 없던 출처다.</figcaption></figure><div class="xf-nums"><div class="xf-num"><b>44개</b><small>매체 RSS</small></div><div class="xf-num"><b>4종</b><small>출처 — 뉴스 · DART · 식약처 · 나라장터</small></div><div class="xf-num"><b>7일</b><small>한 번에 보는 기간</small></div><div class="xf-num"><b>1,524건</b><small>9/18~25 한 주 수집</small></div></div></div>""",
        lib=None,
        desc="수주레이더는 출처를 넷으로 넓히고, 매일 조금씩 · 금요일에 한 주치를 모았다.",
        todo=[],
        prompt="""지금 만든 뉴스 · DART 프로그램을 영업팀용 「수주 레이더」 로 키울 거야. 이번엔 모으는 범위부터 넓혀줘.

1. 뉴스는 구글 뉴스 대신 언론사 RSS 를 직접 받기 — 종합 · 경제지와 산업 전문지(반도체 · 전자, 제약 · 바이오,
   식품 · 화장품, 건설 · 에너지). 주소 목록은 설정 파일(rss_feeds.yaml)로 빼서 늘리고 줄이기 쉽게
2. 기사는 제목과 요약만 쓰고, 빠지는 기사가 없게 매일 이틀치씩 겹쳐 받기. 같은 주소의 기사는 한 번만
3. 1차 거르기 — 「행동(착공 · 신축 · 증설 …) + 대상(공장 · 클린룸 · 데이터센터 …)」, 「대상 + 금액」,
   「대상 + 면적」 중 하나가 맞아야 통과. 주택 · 관급 · 인프라 같은 제외어가 제목이나 본문 앞 200자에 있으면
   탈락. 키워드는 전부 설정 파일(filter_rules.yaml)로
4. 통과한 뉴스는 날짜별 파일로 쌓고 10일 지난 것은 지우기. 금요일에는 7일치를 합치고 겹친 기사 정리
5. DART 는 수시공시를 기간으로 받고, 보고서 이름으로 신규시설투자 · 유형자산 양수 · 취득 · 공장 신축 · 증설 ·
   공급계약만 고르기. 합병 · 주식 양수 · 계약 해지는 빼기
6. 고른 공시는 「공시서류원본파일」 API 로 본문 앞 3,000자를 받아 파일로 저장해두고(다음엔 다시 안 받게),
   장비만 사는 것 · 기존 건물 매입 · 원자재 취득은 빼기
7. 나라장터 시설공사 입찰공고(공공데이터포털)도 받기 — 공고명에 제외어가 있으면 빼고, 반도체 · GMP ·
   데이터센터 같은 말이 있거나 「공장 · 센터 · 시설」 과 산업 이름이 함께 있으면 남기기
8. 식약처 「의약품 GMP 적합판정서 발급현황」 도 받기 — 발급일 항목이 없으니 매주 전체 명단을 저장하고
   지난주 명단과 비교해서 새로 생긴 곳만 표시
9. 인증키(DART, 공공데이터포털)는 코드에 쓰지 말고 환경변수에서 읽기 (자동화할 때 GitHub Secrets 로 넘긴다)
10. 출처 하나가 실패해도 나머지는 계속 받고, 무엇이 실패했는지 남기기

참고로 이렇게 만든 실제 사례: https://github.com/hong-seok-young/xicna-sujoo-radar""",
        need_install=None,
        criteria=[],
    ),

    dict(
        part=4, num="7", id="s7", time="20분",
        title="스코어링 — 쓸모 있는 것만 남기기",
        # 실전 사례(수주레이더)는 이 단계를 어떻게 했나 — 페이지에 그대로 들어가는 HTML
        visual="""<div class="xf"><p class="xf-title"><span class="xf-badge">실전 사례에서는</span>규칙으로 점수를 매기고 등급으로 나눈다</p><div class="xf-cmp"><div class="xf-side"><span>기본 실습 · 우리가 만든 것</span>점수 없음 — 회사 이름으로만 거르고 최신순으로 보여주기</div><div class="xf-arrow">→</div><div class="xf-side real"><span>실전 사례 · 수주레이더</span>노이즈부터 잘라내고 100점 만점 · S/A/B/C 등급 · 같은 사안은 1건으로</div></div><p class="xf-h">과정 — 실제 코드 흐름</p><figure class="dg"><div class="dg-scroll"><svg viewBox="0 0 960 330" role="img" aria-label="뉴스와 공시 한 건이 필터, 분류, 점수, 묶기를 거쳐 TOP 10 이 되는 흐름"><defs><marker id="mk-s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk " d="M0,0 L10,5 L0,10 z"/></marker><marker id="mk-s-k" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk k" d="M0,0 L10,5 L0,10 z"/></marker><marker id="mk-s-drop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk drop" d="M0,0 L10,5 L0,10 z"/></marker></defs><text class="al" x="19" y="50" text-anchor="start">뉴스 · 공시</text><polyline class="ln " points="19,56 79,56 79,66" marker-end="url(#mk-s)"/><rect class="bx " x="19" y="70" width="118" height="78" rx="7"/><text class="h " x="78" y="98.0" text-anchor="middle">1차 거르기</text><text class="s" x="78" y="113.0" text-anchor="middle">「착공+공장」 처럼</text><text class="s" x="78" y="128.0" text-anchor="middle">짝이 맞아야 통과</text><rect class="bx " x="153" y="70" width="118" height="78" rx="7"/><text class="h " x="212" y="98.0" text-anchor="middle">중요도 3단계</text><text class="s" x="212" y="113.0" text-anchor="middle">착공·증설 + 공장·클린룸</text><text class="s" x="212" y="128.0" text-anchor="middle">+ 금액 → HIGH</text><polyline class="ln " points="137,109 149,109" marker-end="url(#mk-s)"/><rect class="bx " x="287" y="70" width="118" height="78" rx="7"/><text class="h " x="346" y="98.0" text-anchor="middle">우리 일 아닌 것</text><text class="s" x="346" y="113.0" text-anchor="middle">경쟁사 수주 · 조선</text><text class="s" x="346" y="128.0" text-anchor="middle">부품 납품 · 10조↑</text><polyline class="ln " points="271,109 283,109" marker-end="url(#mk-s)"/><rect class="bx " x="421" y="70" width="118" height="78" rx="7"/><text class="h " x="480" y="98.0" text-anchor="middle">시설 종류 붙이기</text><text class="s" x="480" y="113.0" text-anchor="middle">클린룸 · 데이터센터</text><text class="s" x="480" y="128.0" text-anchor="middle">제약 · 이차전지 …</text><polyline class="ln " points="405,109 417,109" marker-end="url(#mk-s)"/><rect class="bx k" x="555" y="70" width="118" height="78" rx="7"/><text class="h " x="614" y="98.0" text-anchor="middle">점수 100</text><text class="s" x="614" y="113.0" text-anchor="middle">출처 + 규모</text><text class="s" x="614" y="128.0" text-anchor="middle">+ 시설 + 실현</text><polyline class="ln " points="539,109 551,109" marker-end="url(#mk-s)"/><rect class="bx " x="689" y="70" width="118" height="78" rx="7"/><text class="h " x="748" y="98.0" text-anchor="middle">같은 사안 묶기</text><text class="s" x="748" y="113.0" text-anchor="middle">제목 단어 60%↑</text><text class="s" x="748" y="128.0" text-anchor="middle">또는 같은 기업</text><polyline class="ln " points="673,109 685,109" marker-end="url(#mk-s)"/><rect class="bx out" x="823" y="70" width="118" height="78" rx="7"/><text class="h " x="882" y="98.0" text-anchor="middle">TOP 10</text><text class="s" x="882" y="113.0" text-anchor="middle">C 등급 빼고</text><text class="s" x="882" y="128.0" text-anchor="middle">점수순 10건</text><polyline class="ln " points="807,109 819,109" marker-end="url(#mk-s)"/><polyline class="ln drop" points="78,148 78,196" marker-end="url(#mk-s-drop)"/><rect class="bx drop" x="19" y="200" width="118" height="58" rx="7"/><text class="h " x="78" y="218.0" text-anchor="middle">탈락</text><text class="s" x="78" y="233.0" text-anchor="middle">주택 · 관급 · 인프라 같은</text><text class="s" x="78" y="248.0" text-anchor="middle">말이 앞부분에 있으면</text><polyline class="ln drop" points="212,148 212,196" marker-end="url(#mk-s-drop)"/><rect class="bx drop" x="153" y="200" width="118" height="58" rx="7"/><text class="h " x="212" y="225.5" text-anchor="middle">MID · LOW</text><text class="s" x="212" y="240.5" text-anchor="middle">참고용 칸 · 접어둠</text><polyline class="ln drop" points="346,148 346,196" marker-end="url(#mk-s-drop)"/><rect class="bx drop" x="287" y="200" width="118" height="58" rx="7"/><text class="h " x="346" y="225.5" text-anchor="middle">HIGH → MID 로</text><text class="s" x="346" y="240.5" text-anchor="middle">한 단계 내림</text><polyline class="ln drop" points="748,148 748,196" marker-end="url(#mk-s-drop)"/><rect class="bx drop" x="689" y="200" width="118" height="58" rx="7"/><text class="h " x="748" y="225.5" text-anchor="middle">대표 기사 밑에</text><text class="s" x="748" y="240.5" text-anchor="middle">같은 기사 보관</text><polyline class="ln k" points="614,148 614,196" marker-end="url(#mk-s-k)"/><rect class="bx k" x="555" y="200" width="118" height="58" rx="7"/><text class="h " x="614" y="218.0" text-anchor="middle">등급</text><text class="s" x="614" y="233.0" text-anchor="middle">S 80+ · A 60+</text><text class="s" x="614" y="248.0" text-anchor="middle">B 40+ · C</text><text class="note" x="480" y="300" text-anchor="middle">DART 1차 · 뉴스 HIGH · DART 2차 에서만 TOP 10 을 뽑는다 (식약처 제외)</text></svg></div><figcaption>점선 화살표가 떨어져 나가는 길이다. 점수는 AI 없이 규칙으로 매기고, 같은 사안을 여러 매체가 쓴 기사는 점수가 가장 높은 1건만 남긴다.</figcaption></figure><p class="xf-h">점수 100점 = 네 가지를 더한다</p><div class="xf-bar"><span style="flex:40">출처 40<small>DART 1차 38 · 뉴스 HIGH 34 …</small></span><span style="flex:30">시설 적합성 30<small>CR · 제약 · 이차전지 30</small></span><span style="flex:20">투자 규모 20<small>5,000억 이상 20</small></span><span style="flex:10">실현 10</span></div><div class="xf-grades"><span class="g-s">S · 80점+<small>즉시 영업</small></span><span class="g-a">A · 60~79<small>선제 접촉</small></span><span class="g-b">B · 40~59</span><span class="g-c">C · 40 미만<small>TOP 10 에서 뺌</small></span></div></div>""",
        lib=None,
        desc="수주레이더는 AI 없이 규칙으로 100점 만점 점수를 매기고, 등급으로 영업 우선순위를 정했다.",
        todo=[],
        prompt="""모은 뉴스 · 공시 · 입찰공고 · GMP 명단에 점수를 매겨서 영업에 쓸 것만 위로 올려줘. AI 는 쓰지 말고
규칙으로만.

1. 뉴스 중요도 3단계 — 강한 행동(착공 · 신축 · 증설 · 수주) + 강한 대상(공장 · 플랜트 · 클린룸) + 금액이나
   1,000㎡ 이상 면적이 있으면 HIGH. 준공 · 가동만 있으면 LOW. 나머지는 MID
2. HIGH 라도 우리 일이 아니면 MID 로 내리기 — 경쟁 건설사 수주, 조선 · 해양, 부품 공급사 홍보, 10조 이상 거시
   금액, 시공 얘기가 없는 기사
3. 시설 종류 붙이기 — CR, 데이터센터, 일반생산, 제약/바이오, 식품/음료, R&D, 이차전지. 제목에 있으면 +2,
   본문에 있으면 +1, 1점 이상이면 모두 붙이고 없으면 기타
4. 글에서 금액(억 · 조)과 면적을 숫자로 뽑기 — 「4만1764㎡」 는 41,764㎡. 매출 · 수주잔고 금액은 빼기
5. 점수 100점 = 출처 + 규모 + 시설 + 실현
   - 출처: DART 1차 38 · 뉴스 HIGH 34 · 식약처 26 · DART 2차(공급계약) 24 · 뉴스 MID 16 · 뉴스 LOW 8
   - 규모: 미공시 9 · 450억 미만 7 · 700억 미만 11 · 1천억 미만 14 · 2천억 미만 16 · 5천억 미만 18 · 그 이상 20
   - 시설: CR · 제약/바이오 · 이차전지 30 · 데이터센터 27 · 일반생산 18 · 식품 · R&D · 화장품 12 · 기타 0
     (여러 개면 가장 높은 것)
   - 실현(최대 10): 신규 4 · 정정 1, 자기자본 대비 30% 이상 +3 · 10% 이상 +2 · 그 외 +1, 부지 있으면 +3
   - 준공이면 총점 30 이하
6. 등급 — S 80 이상 · A 60 이상 · B 40 이상 · C 나머지. 뉴스 칸은 등급으로 다시 나누기 (S · A = HIGH,
   B = MID, C = LOW)
7. 같은 사안 묶기 — 점수순으로 세운 뒤, 제목 단어가 60% 이상 겹치거나 같은 대기업 · 같은 지역 얘기면 한 건으로.
   점수가 가장 높은 기사를 대표로 두고 나머지는 대표 밑에 보관
8. DART 공급계약은 500억 이상만, 나라장터는 1억 미만 공고 빼기
9. TOP 10 — DART 1차 · 뉴스 HIGH · DART 2차 에서 C 등급을 빼고 점수순 10건
10. 점수 숫자와 키워드는 설정 파일로 빼서, 숫자만 바꿔 다시 돌려볼 수 있게""",
        need_install=None,
        criteria=[],
    ),

    dict(
        part=4, num="8", id="s8", time="30분",
        title="HTML 보고서 고도화",
        # 실전 사례(수주레이더)는 이 단계를 어떻게 했나 — 페이지에 그대로 들어가는 HTML
        visual="""<div class="xf"><p class="xf-title"><span class="xf-badge">실전 사례에서는</span>영업팀이 바로 쓰는 한 장으로</p><div class="xf-cmp"><div class="xf-side"><span>기본 실습 · 우리가 만든 것</span>뉴스 · 공시 두 칸으로 나눈 목록 한 장 · 제목 누르면 원문</div><div class="xf-arrow">→</div><div class="xf-side real"><span>실전 사례 · 수주레이더</span>우선순위 순서 · KPI 카드 · 카테고리 칩 · 테마 · 글씨 크기 · 접기 · 주간 아카이브</div></div><p class="xf-h">과정 — 실제 코드 흐름</p><figure class="dg"><div class="dg-scroll"><svg viewBox="0 0 960 420" role="img" aria-label="네 파일을 한 장의 HTML 로 조립하고, 화면 설정은 브라우저에 저장하는 보고서 구조"><defs><marker id="mk-r" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk " d="M0,0 L10,5 L0,10 z"/></marker><marker id="mk-r-k" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk k" d="M0,0 L10,5 L0,10 z"/></marker><marker id="mk-r-drop" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk drop" d="M0,0 L10,5 L0,10 z"/></marker></defs><rect class="bx " x="20" y="92" width="130" height="40" rx="7"/><text class="h " x="85" y="116.0" text-anchor="middle">한 주치 뉴스</text><polyline class="ln " points="150,112 180,112 180,210 196,210" marker-end="url(#mk-r)"/><rect class="bx " x="20" y="144" width="130" height="40" rx="7"/><text class="h " x="85" y="168.0" text-anchor="middle">공시 목록</text><polyline class="ln " points="150,164 180,164 180,210 196,210" marker-end="url(#mk-r)"/><rect class="bx " x="20" y="196" width="130" height="40" rx="7"/><text class="h " x="85" y="220.0" text-anchor="middle">입찰공고 목록</text><polyline class="ln " points="150,216 180,216 180,210 196,210" marker-end="url(#mk-r)"/><rect class="bx " x="20" y="248" width="130" height="40" rx="7"/><text class="h " x="85" y="272.0" text-anchor="middle">GMP 공장 목록</text><polyline class="ln " points="150,268 180,268 180,210 196,210" marker-end="url(#mk-r)"/><rect class="bx k" x="200" y="170" width="150" height="80" rx="7"/><text class="h " x="275" y="199.0" text-anchor="middle">보고서 만들기</text><text class="s" x="275" y="214.0" text-anchor="middle">웹 페이지 파일 하나로</text><text class="s" x="275" y="229.0" text-anchor="middle">모아 붙인다</text><polyline class="ln " points="350,210 386,210" marker-end="url(#mk-r)"/><rect class="bx " x="390" y="20" width="330" height="28" rx="7"/><text class="h " x="555" y="38.0" text-anchor="middle">제목 · 테마 · 글씨 크기</text><rect class="bx k" x="390" y="54" width="330" height="28" rx="7"/><text class="h " x="555" y="72.0" text-anchor="middle">고정 바 — 섹션 메뉴 · 카테고리 칩 · 검색</text><rect class="bx out" x="390" y="88" width="330" height="40" rx="7"/><text class="h " x="555" y="112.0" text-anchor="middle">KPI 4카드 + TOP 10</text><rect class="bx " x="390" y="134" width="330" height="28" rx="7"/><text class="h " x="555" y="152.0" text-anchor="middle">⭐ 중요정보 (즐겨찾기)</text><rect class="bx " x="390" y="168" width="330" height="28" rx="7"/><text class="h " x="555" y="186.0" text-anchor="middle">1 DART 1차 — 신규 · 정정 · 유형자산</text><rect class="bx " x="390" y="202" width="330" height="28" rx="7"/><text class="h " x="555" y="220.0" text-anchor="middle">2 뉴스 HIGH</text><rect class="bx " x="390" y="236" width="330" height="28" rx="7"/><text class="h " x="555" y="254.0" text-anchor="middle">3 식약처 GMP — 기간 버튼</text><rect class="lane" x="384" y="272" width="342" height="132" rx="10"/><text class="lane-t" x="396" y="290">참조 · 기본 접힘</text><rect class="bx " x="400" y="298" width="310" height="22" rx="7"/><text class="h " x="555" y="313.0" text-anchor="middle">4 DART 2차 (500억↑ 공급계약)</text><rect class="bx " x="400" y="324" width="310" height="22" rx="7"/><text class="h " x="555" y="339.0" text-anchor="middle">5 뉴스 MID</text><rect class="bx " x="400" y="350" width="310" height="22" rx="7"/><text class="h " x="555" y="365.0" text-anchor="middle">6 뉴스 LOW</text><rect class="bx " x="400" y="376" width="310" height="22" rx="7"/><text class="h " x="555" y="391.0" text-anchor="middle">7 나라장터</text><rect class="bx k" x="770" y="60" width="175" height="150" rx="7"/><text class="h " x="857" y="94.0" text-anchor="middle">내 브라우저가 기억</text><text class="s" x="857" y="109.0" text-anchor="middle">다음에 열어도 그대로</text><text class="s" x="857" y="124.0" text-anchor="middle"></text><text class="s" x="857" y="139.0" text-anchor="middle">화면 테마</text><text class="s" x="857" y="154.0" text-anchor="middle">글씨 크기</text><text class="s" x="857" y="169.0" text-anchor="middle">☆ 즐겨찾기</text><text class="s" x="857" y="184.0" text-anchor="middle">접어둔 칸</text><polyline class="ln k" points="720,34 766,90" marker-end="url(#mk-r-k)"/><text class="al k" x="743" y="29" text-anchor="middle">기억</text><polyline class="ln k" points="720,148 766,150" marker-end="url(#mk-r-k)"/><polyline class="ln k" points="726,300 740,300 740,196 766,196" marker-end="url(#mk-r-k)"/><rect class="bx out" x="770" y="300" width="175" height="56" rx="7"/><text class="h " x="857" y="324.5" text-anchor="middle">지난 보고서 모음</text><text class="s" x="857" y="339.5" text-anchor="middle">주마다 한 장씩 쌓임</text><polyline class="ln " points="726,340 766,330" marker-end="url(#mk-r)"/><text class="al " x="746" y="325" text-anchor="middle">올림</text></svg></div><figcaption>보고서는 웹 페이지 파일 한 장이다. 영업 우선순위대로 1~3 을 펼쳐두고 참고용 4~7 은 접어둔다. 테마 · 글씨 · 즐겨찾기 · 접어둔 칸은 보는 사람 브라우저가 기억한다.</figcaption></figure></div>""",
        lib=None,
        desc="수주레이더는 영업팀이 바로 쓰도록 우선순위 순서의 웹 페이지 한 장으로 보여준다.",
        todo=[],
        prompt="""보고서를 영업팀이 바로 쓰는 웹 페이지 한 장으로 바꿔줘.

1. HTML 파일 하나로 — 디자인과 기능을 그 안에 다 넣어서 파일만 열면 되게
2. 맨 위 — KPI 카드 4개(총 분석 건수 · S급 · A급 · S·A 총 투자액)와 TOP 10 표(발주처/프로젝트 · 출처 ·
   시설 유형 · 투자 규모 · 점수와 등급)
3. 칸 순서는 영업 우선순위대로 — ⭐ 중요정보 → 1 DART 1차(신규 · 정정 · 유형자산으로 묶기) → 2 뉴스 HIGH →
   3 식약처 GMP, 그 아래 [참조] 4 DART 2차 · 5 뉴스 MID · 6 뉴스 LOW · 7 나라장터. 참조 4개는 처음에 접어두기
4. 스크롤해도 위에 붙어 있는 바 — 칸 메뉴, 시설 종류 칩(건수 표시), 키워드 검색. 칩과 검색으로 바로 걸러지게
5. 줄마다 ☆ — 누르면 맨 위 중요정보에 모이고, 브라우저에 저장해서 다시 열어도 남게
6. 화면 테마(다크 · 라이트 · 세피아), 글씨 크기 3단계, 접어둔 칸 — 모두 브라우저에 저장
7. 오른쪽에 떠 있는 목차 — 지금 보고 있는 칸 표시, 누르면 그 칸으로 이동하고 접혀 있으면 펼치기
8. 식약처 칸에는 기간 버튼(7 · 30 · 90 · 180 · 365일)
9. 줄을 누르면 원문을 새 창으로
10. 한 줄을 그리다 문제가 생겨도 그 줄만 건너뛰고 나머지는 그리기""",
        need_install=None,
        criteria=[],
    ),
]
