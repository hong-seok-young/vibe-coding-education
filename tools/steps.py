"""실습 페이지의 단계별 내용 — 이 파일이 원본이다.

프롬프트·성공 기준·정답 코드를 여기서 고치고 build_page.py 를 실행하면
저장소 루트의 실습 HTML 이 다시 만들어진다. HTML 을 직접 고치면 다음 실행에
덮어써진다.

각 항목의 뜻
  part          1=수집 실습, 2=메일 실습, 3=보너스
  num / id      화면에 보이는 번호 / 내부 식별자(URL 해시)
  time          배정 시간 (README 진행표의 합계와 맞춰야 한다)
  lib           그 단계에서 pip 로 받아야 하는 것 (없으면 None)
  desc          수강생에게 이 단계가 무엇인지 설명하는 문단
  prompt        AI 에게 그대로 붙여넣는 본문. 파일 요청 문구는 build_page.py 가
                뒤에 자동으로 붙이므로 여기 쓰지 않는다
  need_install  프롬프트 위에 띄우는 설치 안내
  trouble       (선택) 막혔을 때 이어서 넣을 프롬프트 dict(summary, body, prompt)
  criteria      성공 기준 체크리스트
  code          참고용 정답 코드 조각. 화면에는 나오지 않는다 — 페이지의
                "정답 코드 파일 받기" 버튼은 news-report-bot/main.py 를 통째로
                내려주므로, 이쪽을 고쳤으면 main.py 도 같이 맞춰야 한다

프롬프트를 쓸 때 지키는 것
  · 코딩을 모르는 사람이 실제로 쓸 만한 말투. 기술 용어를 나열하지 않는다
  · 꼭 정확해야 하는 기술 사항(사내망 SSL 등)은 "강사님이 적어준 것"을 옮겨
    적는 형식으로 「」 안에 넣는다 — 뭉뚱그리면 AI 가 엉뚱한 걸 고른다
  · 문장 끝이 따옴표로 끝나면 안 된다 (파이썬 삼중 따옴표 문자열이 깨진다)
"""

STEPS = [
    dict(
        part=1, num="0", id="s0", time="10분",
        title="프로그램 창 만들기",
        lib=None,
        desc="터미널 대신 더블클릭하면 뜨는 진짜 프로그램 창을 만든다. 여기서부터는 창이 뜨면 다음 "
             "단계로 넘어가도 된다. 결과 칸을 뉴스·DART·진행 상황 셋으로 나누는 건, 한 칸에 다 쌓으면 "
             "두 수집을 번갈아 눌렀을 때 방금 뭘 가져왔는지 알 수 없기 때문이다.",
        prompt="""파이썬으로 뉴스랑 DART 공시를 모아서 메일로 보내는 프로그램을 만들 거야. 터미널이 아니라
더블클릭하면 창이 뜨는 프로그램으로. 나는 코딩을 전혀 몰라.

위쪽에 입력 칸 네 개 — 키워드(여러 개), 지켜볼 회사 이름, 메일 받을 사람, DART 인증키.
입력한 값은 창을 닫았다 다시 열어도 남아있게 저장해줘.

그 아래에 버튼 세 개 — "뉴스 수집하기", "DART 수집하기", "메일 보내기".

그 아래는 결과 보는 곳인데, 하나로 합치지 말고 세 칸으로 나눠줘 — "뉴스 수집 결과",
"DART 수집 결과", 그리고 진행 상황이나 에러가 들어갈 작은 "진행 상황" 칸. 수집 버튼은
각자 자기 칸에만 쓰게 해줘. 세 칸 다 스크롤되고, 안의 글자는 고칠 수 없게.

나중에 항목이 들어오면 그 제목을 눌러서 원문을 브라우저로 열 수 있게 해줘. 제목은 파란색
밑줄로, 마우스를 올리면 손가락 모양으로.

기사·공시 한 건을 담을 형태도 만들어줘 — 출처, 제목, 원문 링크, 올라온 날짜/시간, 짧은
메모. 날짜는 한국 시간 "09/03 14:30" 형식이고, 모르면 "-".

지금은 버튼을 눌러도 진행 상황 칸에 안내만 나오면 돼. 창이 열리면 진행 상황 칸 첫 줄에
파이썬 버전을 한 줄 보여줘.""",
        need_install=None,
        criteria=[
            "받은 파일을 AI가 알려준 대로 저장하고 실행하면, 검은 터미널 창이 아니라 진짜 프로그램 창이 뜬다",
            "결과 보는 곳이 \"뉴스 수집 결과\" / \"DART 수집 결과\" / \"진행 상황\" 세 칸으로 나뉘어 있다",
            "진행 상황 칸 맨 위에 실행 중인 파이썬 버전이 한 줄 표시된다",
            "입력 칸에 아무 값이나 써넣고 창을 닫았다가 다시 열면, 써넣은 값이 그대로 남아있다",
            "버튼 세 개를 눌러보면 에러 없이 진행 상황 칸에 뭔가 나온다",
        ],
        code="""def load_settings() -> dict:
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def save_settings(data: dict) -> None:
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@dataclass
class Item:
    source: str
    title: str
    link: str
    dt: datetime | None = None
    note: str = field(default="")

    @property
    def when(self) -> str:
        return self.dt.astimezone(KST).strftime("%m/%d %H:%M") if self.dt else "-"


def clean_text(raw: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", raw)).strip()


class ResultPane:
    '''제목이 붙은 결과창 하나. 뉴스용·DART용으로 따로 하나씩 쓴다.

    항목의 제목은 누르면 원문이 브라우저에서 열린다. Text 위젯은 구간(tag)마다
    클릭 동작을 따로 걸 수 있으니, 항목마다 고유한 tag 를 붙이고 거기에 링크를
    묶어둔다. 창은 state="disabled" 로 두어 글자를 고칠 수 없게 해도 tag 클릭은
    그대로 동작한다.
    '''

    def __init__(self, parent, title: str, height: int = 9):
        self.frame = ttk.LabelFrame(parent, text=title, padding=6)
        self.box = scrolledtext.ScrolledText(self.frame, height=height, wrap="word", state="disabled")
        self.box.pack(fill="both", expand=True)
        self.box.tag_configure("link", foreground="#0b57d0", underline=True)
        self.box.tag_configure("dim", foreground="#666666")
        self.box.tag_configure("warn", foreground="#b3261e")
        self._link_seq = 0

    def _append(self, text: str, tags=()) -> None:
        self.box.configure(state="normal")
        self.box.insert("end", text, tags)
        self.box.see("end")
        self.box.configure(state="disabled")

    def write(self, message: str, style: str | None = None) -> None:
        self._append(message + "\\n", (style,) if style else ())

    def write_item(self, item: Item) -> None:
        '''한 줄에 '날짜  제목  (메모)'. 제목만 눌러서 원문으로 갈 수 있다.'''
        self._append(f"  {item.when}  ")
        if item.link:
            self._link_seq += 1
            tag = f"link{self._link_seq}"
            self._append(item.title, ("link", tag))
            self.box.tag_bind(tag, "<Button-1>", lambda _e, u=item.link: webbrowser.open(u))
            self.box.tag_bind(tag, "<Enter>", lambda _e: self.box.configure(cursor="hand2"))
            self.box.tag_bind(tag, "<Leave>", lambda _e: self.box.configure(cursor=""))
        else:
            self._append(item.title)
        if item.note:
            self._append(f"   ({item.note})", ("dim",))
        self._append("\\n")


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("DART·뉴스 정보 크롤링 및 메일발송 프로그램")
        root.geometry("880x860")
        self.settings = load_settings()
        self.collected: list[Item] = []

        form = ttk.Frame(root, padding=10)
        form.pack(fill="x")

        self.vars: dict[str, tk.StringVar] = {}
        for key, label in FIELDS:
            row = ttk.Frame(form)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=28).pack(side="left")
            var = tk.StringVar(value=self.settings.get(key, ""))
            var.trace_add("write", lambda *_: self._save_settings())
            ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
            self.vars[key] = var

        btns = ttk.Frame(root, padding=10)
        btns.pack(fill="x")
        self.buttons = [
            ttk.Button(btns, text="뉴스 수집하기", command=lambda: self.log("뉴스 수집하기 — 아직 준비 중")),
            ttk.Button(btns, text="DART 수집하기", command=lambda: self.log("DART 수집하기 — 아직 준비 중")),
            ttk.Button(btns, text="메일 보내기", command=lambda: self.log("메일 보내기 — 아직 준비 중")),
        ]
        for b in self.buttons:
            b.pack(side="left", padx=4)

        # 결과창을 뉴스용·DART용으로 나눈다. 한 칸에 섞어 넣으면 두 수집을 번갈아
        # 눌렀을 때 방금 뭘 가져온 건지 알 수 없다.
        panes = ttk.Frame(root, padding=(10, 0))
        panes.pack(fill="both", expand=True)
        self.news_pane = ResultPane(panes, "뉴스 수집 결과  (제목을 누르면 원문이 열립니다)")
        self.news_pane.frame.pack(fill="both", expand=True, pady=(0, 6))
        self.dart_pane = ResultPane(panes, "DART 수집 결과  (제목을 누르면 원문이 열립니다)")
        self.dart_pane.frame.pack(fill="both", expand=True)

        # 수집 결과가 아닌 것(진행 상황, 에러, 메일 발송)은 여기로 보낸다.
        status = ttk.LabelFrame(root, text="진행 상황", padding=6)
        status.pack(fill="x", padx=10, pady=10)
        self.log_box = scrolledtext.ScrolledText(status, height=6, wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True)

    def _save_settings(self) -> None:
        save_settings({k: v.get() for k, v in self.vars.items()})

    def log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()""",
    ),
    dict(
        part=1, num="2", id="s2", time="10분",
        title="뉴스 수집 버튼 연결하기",
        lib="feedparser",
        desc="'뉴스 수집하기' 버튼을 누르면 실제로 구글 뉴스에서 키워드에 걸리는 기사를 가져오게 "
             "만든다. 인증키가 필요 없고 호출 한도도 없어서, 첫 성공을 가장 빨리 볼 수 있는 방식이다.",
        prompt=""""뉴스 수집하기" 버튼이 실제로 구글 뉴스에서 기사를 가져오게 해줘. 구글 뉴스는 인증키
없이 검색 결과를 받아올 수 있어. 입력한 키워드마다 한국 기준으로 검색해서, 키워드당 최신
10건까지만.

키워드 칸이 비어있으면 뉴스 칸에 "키워드가 없어 건너뜀"만 알려주고 끝내.

못 가져올 때는 "회사 네트워크가 막아서 아예 못 받아온 경우"와 "받아왔는데 그 키워드로
걸리는 기사가 없는 경우"를 구분해서 뉴스 칸에 알려주고, 다음 키워드로 계속 진행해줘.

가져온 건 아까 만든 형태로 담아서(출처는 "뉴스") 지금까지 모은 목록에 합쳐줘. 뉴스 칸에는
방금 가져온 것만 최신순으로 보여주고, 제목을 누르면 원문이 열리게. 누적 전체를 매번 다시
늘어놓으면 수천 줄이 되니까 전체는 숫자로 한 줄만. 진행 상황은 진행 상황 칸에.

버튼을 누른 동안 창이 멈추지 않게 뒤에서 작업해줘.

아, 우리 회사 사정 하나. 보안 장비가 인터넷 통신을 중간에서 열어보는 환경이라, 파이썬으로
뭘 받아오려고 하면 이런 에러가 난다고 해.

CERTIFICATE_VERIFY_FAILED ... Missing Authority Key Identifier

강사님이 이렇게 하면 된다고 적어줬어. 이 부분은 그대로 해줘.

「SSL 설정은 ssl.create_default_context() 로 만들고, 거기서 ctx.verify_flags 의
VERIFY_X509_STRICT 만 빼라. certifi 를 지정하거나 ctx.options 를 건드리는 건 효과가 없고,
verify_mode·check_hostname 을 끄는 건 위험하니 하지 마라.」""",
        need_install="pip install feedparser",
        trouble=dict(
            summary="그래도 뉴스 결과 칸에 CERTIFICATE 어쩌고 하는 에러가 뜨면",
            body="회사 보안 장비 때문에 생기는 문제다. 위 프롬프트에 이미 대응을 요청해뒀지만, "
                 "AI가 빠뜨렸거나 엉뚱한 설정을 건드릴 수 있다. 에러 문장에 "
                 "<code>Missing Authority Key Identifier</code> 가 보이면 최신 파이썬의 엄격 검사에 "
                 "걸린 것이고, <code>unable to get local issuer certificate</code> 가 보이면 회사 "
                 "인증서를 아직 못 믿고 있는 것이다. 아래 프롬프트를 이어서 넣으면 된다 — "
                 "고쳐야 할 곳을 콕 집어 알려주는 내용이라, 애매하게 물어보는 것보다 훨씬 잘 듣는다. "
                 "그래도 안 되면 <strong>에러 문장을 그대로 복사해서</strong> AI에게 붙여넣는 게 가장 빠르다.",
            prompt="""뉴스 수집하기 버튼을 눌렀더니 CERTIFICATE 어쩌고 하는 에러가 떴어.
(에러 문장을 여기에 그대로 붙여넣기)

우리 회사는 보안 장비가 인터넷 통신을 중간에서 열어보는 환경이야. 브라우저에서는 잘 되는데
이 프로그램만 막혀. 강사님이 적어준 대로 고쳐줘.

「SSL 설정은 ssl.create_default_context() 로 만들고, 거기서 ctx.verify_flags 의
VERIFY_X509_STRICT 만 빼라. 둘 중 하나만 하면 다른 에러로 바뀐다. certifi 를 지정하면
unable to get local issuer certificate 로 바뀌고, ctx.options 를 건드리는 건 이 에러와
아무 상관이 없다 — 이미 들어가 있으면 지워라. verify_mode·check_hostname 은 끄지 마라.」

설치해야 할 게 있으면 알려줘.""",
        ),
        criteria=[
            "pip install feedparser 를 실행했다",
            "키워드 칸을 비워두고 버튼을 누르면 에러 없이 \"건너뜀\" 메시지만 뜬다",
            "키워드를 채우고 버튼을 누르면 뉴스 결과 칸에만 한국어 기사 제목들이 나온다 (키워드당 열 건 정도)",
            "기사 제목을 누르면 브라우저에서 그 기사 원문이 열린다",
            "버튼을 누른 동안에도 창이 멈추지 않고 계속 움직인다",
        ],
        code="""# 사내망 대응 — 이 두 가지를 같이 해야 통과한다
def _make_ssl_context() -> ssl.SSLContext:
    # 윈도우 인증서 저장소를 함께 읽는다 (회사 인증서가 거기 있다).
    # certifi 를 지정하면 이 저장소를 덮어써서 오히려 회사 인증서를 못 믿게 된다.
    ctx = ssl.create_default_context()
    # 3.13 부터 기본으로 켜진 엄격 검사만 끈다 (회사 인증서엔 AKI 항목이 없다).
    ctx.verify_flags &= ~getattr(ssl, "VERIFY_X509_STRICT", 0)
    return ctx


class _CorporateTLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = _make_ssl_context()
        return super().init_poolmanager(*args, **kwargs)


SESSION = requests.Session()
SESSION.mount("https://", _CorporateTLSAdapter())


def google_news_rss(keyword: str) -> str:
    return f"https://news.google.com/rss/search?q={quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"


def collect_news(keywords: list[str], limit_per_keyword: int = 10) -> tuple[list[Item], list[str]]:
    items: list[Item] = []
    errors: list[str] = []

    if not keywords:
        return items, ["키워드가 없어 건너뜀"]

    for keyword in keywords:
        # feedparser 에 주소를 그대로 넘기면 위 SESSION 을 못 타므로 직접 받아서 넘긴다
        try:
            resp = SESSION.get(google_news_rss(keyword), timeout=15)
            resp.raise_for_status()
            entries = feedparser.parse(resp.content).entries
        except requests.RequestException as exc:
            errors.append(f"'{keyword}' 검색 실패: {exc}")
            continue

        if not entries:
            errors.append(f"'{keyword}' 검색 결과 0건")
            continue

        for entry in entries[:limit_per_keyword]:
            dt = None
            if getattr(entry, "published_parsed", None):
                dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            items.append(Item(
                source="뉴스",
                title=clean_text(entry.get("title", "")),
                link=entry.get("link", ""),
                dt=dt,
            ))

    return items, errors


# 버튼이 눌렸을 때 실행되는 부분 (App 클래스 안)
def on_collect_news(self) -> None:
    def task():
        self.root.after(0, lambda: self.log("뉴스 수집 중..."))     # 진행 상황 칸
        items, errors = collect_news(self._list_field("keywords"))
        # 왜 0건인지 알아야 하니까, 에러도 뉴스 결과 칸에 그대로 남긴다
        for e in errors:
            self.root.after(0, lambda e=e: self.news_pane.write(f"  ! {e}", "warn"))
        self._merge(items, "뉴스", self.news_pane)
    self._run_in_background(task)""",
    ),
    dict(
        part=1, num="3", id="s3", time="15분",
        title="DART 수집 버튼 연결하기",
        lib="requests",
        desc="'DART 수집하기' 버튼을 누르면 실제로 전자공시시스템에서 공시를 가져오게 만든다. 조건을 "
             "가장 많이 넣어서 요청해야 하는 서비스다. 회사 이름 없이 돌리면 일주일치가 수천 건이라 "
             "50건 상한을 둔다 — 안 그러면 결과 칸이 넘쳐서 창이 멈춘다.",
        prompt=""""DART 수집하기" 버튼이 전자공시시스템(DART)에서 공시 목록을 가져오게 해줘.

인증키가 없으면 DART 칸에 "DART 인증키가 없어 건너뜀"만 알려주고 넘어가.

키가 있으면 최근 일주일치 공시를 가져와줘. 지켜볼 회사를 적어뒀으면 그 회사 것만 남기고 —
이름이 정확히 같지 않아도 그 글자가 들어가면 걸리게("삼성"이면 삼성전자·삼성물산 다).
회사를 안 적었으면 최신 50건만 담고 "전체 몇 건 중 50건만 담았다"고 알려줘.

여기 함정이 하나 있어. DART는 회사 이름으로 찾아달라고 요청할 수가 없어서, 그 기간 공시를
전부 받아온 다음 우리가 직접 골라내야 해. 중간에 끊으면 뒷페이지에 있던 그 회사 공시를
놓치고 "없다"고 하게 되니까, 그 기간 것을 끝까지 받은 다음에 골라줘.

담을 때 제목은 "[회사명] 보고서 이름", 링크는 공시 원문 주소, 날짜는 접수일, 메모는
제출인, 출처는 "DART".

0건일 때는 이유를 구분해서 DART 칸에 알려줘 — ① 그 기간에 공시가 아예 없음(주말·공휴일이면
정상) ② 공시는 있었는데 그 회사 것이 없음 ③ 인증키 문제. ②는 "공시 몇 건을 살펴봤는데
그중 그 회사 건 없었다"처럼 살펴본 전체 건수도 같이 보여줘.

결과는 DART 칸에만, 방금 가져온 것만 최신순으로, 제목을 누르면 원문이 열리게. 전체는
숫자로 한 줄만. 이 버튼도 창이 멈추지 않게 뒤에서 작업해줘.""",
        need_install="pip install requests",
        criteria=[
            "pip install requests 를 실행했다",
            "DART 인증키를 채우고 버튼을 누르면 수집된 공시 제목이 DART 결과 칸에만 뜬다",
            "공시 제목을 누르면 브라우저에서 그 공시 원문이 열린다",
            "0건이 나오면 왜 0건인지(기간에 공시가 없음 / 그 회사 것만 없음) DART 결과 칸에 설명이 뜬다",
            "회사명을 비워두고 눌러도 결과 칸이 수천 줄로 쏟아지지 않고, 프로그램이 계속 잘 움직인다",
            "지켜볼 회사명을 \"삼성\"처럼 짧게 넣으면 삼성전자·삼성물산 같은 것들이 다 걸린다",
        ],
        code="""def collect_dart(watch: list[str], api_key: str, days_back: int = DAYS_BACK, max_pages: int = 30) -> tuple[list[Item], list[str]]:
    '''DART 공시를 가져온다. 회사 이름을 지정했으면 그 회사 것만 남긴다.

    주의할 점이 두 가지 있다.

    · DART 의 목록 조회는 **회사 이름으로 검색할 수 없다.** 기간 안의 공시를 전부
      받아온 뒤 우리가 직접 골라내야 한다. 그래서 기간 안의 페이지를 끝까지 받아야
      한다 — 중간에 끊으면 뒷페이지에 있던 그 회사 공시를 놓쳐서 "0건"이 된다.
    · 하루치만 보면 특정 회사는 공시가 없는 날이 훨씬 많다. 그래서 기본 기간을
      넉넉하게 잡는다(DAYS_BACK).

    0건일 때 왜 0건인지 알 수 있도록, 기간 안의 전체 공시 수와 걸러낸 결과를
    함께 돌려준다.
    '''
    items: list[Item] = []
    errors: list[str] = []

    if not api_key:
        return items, ["DART 인증키가 없어 건너뜀"]

    today = datetime.now(KST).date()
    begin = today - timedelta(days=max(days_back - 1, 0))
    period = f"{begin:%Y-%m-%d}~{today:%Y-%m-%d}"

    total_seen = 0        # 기간 안의 전체 공시 수 (걸러내기 전)
    truncated = False

    page = 1
    while page <= max_pages:
        try:
            resp = SESSION.get(
                "https://opendart.fss.or.kr/api/list.json",
                params={
                    "crtfc_key": api_key,
                    "bgn_de": begin.strftime("%Y%m%d"),
                    "end_de": today.strftime("%Y%m%d"),
                    "page_no": page,
                    "page_count": 100,
                },
                timeout=10,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            errors.append(f"DART 연결 실패: {exc}")
            break

        payload = resp.json()
        status = payload.get("status")

        if status == "013":          # 조회된 데이터 없음 (주말·공휴일이면 정상)
            errors.append(f"DART: {period} 기간에 공시가 없습니다 (주말·공휴일이면 정상)")
            break
        if status != "000":
            errors.append(f"DART 응답 오류 [{status}] {payload.get('message', '')}")
            break

        rows = payload.get("list", [])
        total_seen += len(rows)

        for row in rows:
            corp = row.get("corp_name", "")
            if watch and not any(name in corp for name in watch):
                continue

            dt = None
            try:
                dt = datetime.strptime(row["rcept_dt"], "%Y%m%d").replace(tzinfo=KST)
            except (KeyError, ValueError):
                pass

            items.append(Item(
                source="DART",
                title=f"[{corp}] {row.get('report_nm', '')}".strip(),
                link=f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={row.get('rcept_no', '')}",
                dt=dt,
                note=row.get("flr_nm", ""),
            ))

        total_page = int(payload.get("total_page", 1) or 1)
        if page >= total_page:
            break
        page += 1
    else:
        truncated = True

    # 0건일 때 원인을 알 수 있게 설명을 남긴다.
    if total_seen:
        if watch and not items:
            errors.append(
                f"DART: {period} 공시 {total_seen}건을 살펴봤지만 "
                f"'{', '.join(watch)}' 이(가) 이름에 들어간 회사는 없었습니다. "
                f"회사 이름을 짧게(예: 삼성) 적었는지, 기간을 늘릴지 확인해보세요."
            )
        elif watch:
            errors.append(f"DART: {period} 공시 {total_seen}건 중 {len(items)}건이 '{', '.join(watch)}' 관련")

    if truncated:
        errors.append(
            f"DART: 기간 안의 공시가 너무 많아 앞부분 {total_seen}건까지만 확인했습니다. "
            f"기간을 줄이면 빠짐없이 볼 수 있습니다."
        )

    return items, errors


# 버튼이 눌렸을 때 실행되는 부분 (App 클래스 안)
def on_collect_dart(self) -> None:
    def task():
        self.root.after(0, lambda: self.log("DART 수집 중..."))     # 진행 상황 칸
        items, errors = collect_dart(self._list_field("dart_watch"), self.vars["dart_key"].get())
        for e in errors:
            self.root.after(0, lambda e=e: self.dart_pane.write(f"  ! {e}", "warn"))
        self._merge(items, "DART", self.dart_pane)
    self._run_in_background(task)""",
    ),
    dict(
        part=1, num="4", id="s4", time="5분",
        title="정리 — 중복 제거·최신순·출처별 보기",
        lib=None,
        desc="여러 소스에서 모은 항목을 합칠 때 자동으로 정리되게 만든다. 나중에 RSS 등 소스를 더 "
             "추가해도 이 부분이 그대로 중복을 걸러준다.",
        prompt="""모은 항목들을 합칠 때 자동으로 정리되게 해줘. 제목이 비어있는 건 빼고, 제목이 똑같으면
링크가 달라도 같은 소식으로 봐서 하나만 남기고, 최신 것부터 정렬하되 날짜가 없는 건 맨
뒤로.

수집 버튼 둘 다 새로 가져온 걸 합칠 때 이 정리를 거치게 해줘 (각자 자기 칸에 쓰는 건
그대로).

결과 칸에는 방금 가져온 게 많으면 앞에서 열 개만 보여주고 나머지는 몇 건 더 있다고만
알려줘. 그리고 칸 맨 아래에 "뉴스 몇 건 · DART 몇 건"처럼 지금까지 모은 걸 출처별로 한
줄 요약해줘.

한 가지 더. 공시는 접수 날짜만 알 수 있고 몇 시인지는 몰라. 그런데 지금 00:00으로 채워져서
같은 날 뉴스보다 늘 아래로 밀려. 시각을 모르는 항목은 날짜만 보여줘.""",
        need_install=None,
        criteria=[
            "뉴스 수집하기랑 DART 수집하기를 번갈아 눌러도 같은 제목의 항목이 중복으로 남지 않는다",
            "버튼을 누르면 그 버튼의 결과 칸에, 방금 가져온 것만 최신순으로 나온다",
            "그 아래에 \"뉴스 몇 건 · DART 몇 건\" 처럼 출처별 요약이 한 줄 나온다",
            "공시 항목은 00:00 대신 날짜만 표시된다",
        ],
        code="""def dedupe_and_sort(items: list[Item]) -> list[Item]:
    seen: set[str] = set()
    unique: list[Item] = []

    for item in items:
        if not item.title:
            continue
        key = re.sub(r"[^0-9a-z가-힣]", "", item.title.lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    unique.sort(key=lambda i: i.dt or FAR_PAST, reverse=True)
    return unique


def group_by_source(items: list[Item]) -> list[tuple[str, list[Item]]]:
    '''출처별로 묶어서 (출처, 항목들) 목록으로 돌려준다. 각 묶음은 최신순.

    한 목록에 뉴스와 공시를 시간순으로 섞어두면 읽기가 어렵다. 특히 공시는 시각을
    모르니 같은 날 뉴스보다 늘 아래로 밀려서 뒤죽박죽으로 보인다. 그래서 보여줄 때는
    출처별로 나눈다. (중복 제거와 최신순 정렬은 이미 끝난 상태로 들어온다)
    '''
    groups: dict[str, list[Item]] = {}
    for item in items:
        groups.setdefault(item.source, []).append(item)

    # 뉴스를 먼저, DART를 그다음, 나머지(언론사)는 뒤에
    def order(source: str) -> tuple[int, str]:
        return ({"뉴스": 0, "DART": 1}.get(source, 2), source)

    return sorted(groups.items(), key=lambda kv: order(kv[0]))


# App 클래스 안 — 그 출처의 결과 칸에, 방금 가져온 것만 쓰고 아래에 요약을 붙인다
def _merge(self, new_items: list[Item], label: str, pane: ResultPane) -> None:
    before = len(self.collected)
    self.collected = dedupe_and_sort(self.collected + new_items)
    added = len(self.collected) - before

    def show():
        pane.write(f"{label} {len(new_items)}건 가져옴 (새로 추가 {added}건)")
        for item in dedupe_and_sort(new_items)[:10]:
            pane.write_item(item)          # 제목은 눌러서 원문으로 갈 수 있다
        if len(new_items) > 10:
            pane.write(f"    ... 외 {len(new_items) - 10}건", "dim")
        summary = " · ".join(
            f"{source} {len(group)}건" for source, group in group_by_source(self.collected)
        )
        pane.write(f"  = 지금까지 모은 것: {summary}  (전체 {len(self.collected)}건)", "dim")
        pane.write("")

    self.root.after(0, show)""",
    ),
    dict(
        part=2, num="5", id="s5", time="10분",
        title="메일 조립 — 보기 좋은 이메일 만들기",
        lib=None,
        desc="정리된 항목을 사람이 읽기 좋은 이메일 본문으로 바꾼다.",
        prompt="""모은 항목들을 사람이 보기 좋은 이메일 본문(디자인이 들어간 형태)으로 만드는 부분을
준비해줘. 맨 위에 "오늘의 이슈 리포트", 오늘 날짜(한국어, 예: 2026년 09월 01일), 총 몇
건인지, "뉴스 몇 건 · DART 몇 건" 요약 한 줄.

본문은 출처별로 나눠줘 — 뉴스끼리, 공시끼리 묶어서 각각 소제목을 달고 그 안에서 최신순.
섞어놓으면 읽기 어렵고, 공시는 시각을 몰라서 같은 날 뉴스보다 늘 아래로 밀려. 항목마다
제목(누르면 원문으로 가는 링크)과 발행 시간.

전체 40건까지만 보여주고 더 있으면 "이 밖에 몇 건이 더 있습니다"라고 알려줘. 이메일은
별도 디자인 파일을 못 불러오니까 디자인은 본문 안에 직접 넣어줘.

아직 보내지는 말고 본문 만드는 부분만 — 버튼 연결은 다음 단계에서 할 거야.""",
        need_install=None,
        criteria=[
            "이 부분을 만든 뒤에도 지금까지의 버튼들은 여전히 에러 없이 잘 동작한다",
            "(다음 단계에서 실제 메일을 받아보면) 뉴스와 공시가 각각 따로 묶여서 나온다",
        ],
        code="""def build_html(items: list[Item]) -> str:
    '''메일 본문을 만든다. 출처별로 섹션을 나눠서, 뉴스와 공시가 섞이지 않게 한다.'''
    sections = []
    shown = 0

    for source, group in group_by_source(items):
        if shown >= MAX_ITEMS:
            break

        rows = []
        for item in group[: MAX_ITEMS - shown]:
            rows.append(f'''
        <tr>
          <td style="padding:9px 8px;border-bottom:1px solid #eee;font-size:14px;">
            <a href="{html.escape(item.link)}"
               style="color:#1a1a1a;text-decoration:none;">{html.escape(item.title)}</a>
          </td>
          <td style="padding:9px 8px;border-bottom:1px solid #eee;white-space:nowrap;
                     color:#aaa;font-size:12px;vertical-align:top;">{item.when}</td>
        </tr>''')
        shown += len(rows)

        sections.append(f'''
    <h2 style="font-size:14px;margin:24px 0 6px;padding-bottom:6px;
               border-bottom:2px solid #1a2233;">{html.escape(source)}
      <span style="color:#8993a3;font-weight:normal;font-size:12px;">{len(group)}건</span>
    </h2>
    <table style="width:100%;border-collapse:collapse;">{''.join(rows)}</table>''')

    omitted = len(items) - shown
    more = (f'''
    <p style="color:#aaa;font-size:12px;margin-top:16px;">
      이 밖에 {omitted}건이 더 있습니다.
    </p>''' if omitted > 0 else "")

    summary = " · ".join(f"{source} {len(group)}건" for source, group in group_by_source(items))

    return f'''<!doctype html>
<html><body style="margin:0;padding:24px;background:#f5f6f4;
                   font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;color:#1a2233;">
  <div style="max-width:720px;margin:0 auto;background:#fff;border-radius:12px;padding:28px;">
    <h1 style="font-size:20px;margin:0 0 4px;">오늘의 이슈 리포트</h1>
    <p style="color:#8993a3;font-size:13px;margin:0 0 4px;">
      {datetime.now(KST).strftime('%Y년 %m월 %d일')} · 수집 {len(items)}건
    </p>
    <p style="color:#8993a3;font-size:12px;margin:0;">{html.escape(summary)}</p>
{''.join(sections)}{more}

    <p style="color:#aaa;font-size:11px;margin-top:24px;">
      바이브코딩 실습 · 내 PC에서 실행된 자동 리포트
    </p>
  </div>
</body></html>'''""",
    ),
    dict(
        part=2, num="6", id="s6", time="15분",
        title="메일 보내기 버튼 연결하기 — 아웃룩 자동 발송",
        lib="pywin32 (윈도우 전용)",
        desc="클래식 아웃룩을 원격 조작해서 완전 자동으로 메일을 보낸다. 사내망이 SMTP를 막아둔 상황을 "
             "우회하는 핵심 부분.",
        prompt=""""메일 보내기" 버튼을 눌렀을 때, 모은 항목으로 만든 이메일을 윈도우에 로그인되어 있는
아웃룩(데스크톱 앱)으로 실제 자동 발송하게 해줘.

내가 이미 로그인해둔 아웃룩을 원격으로 조작해서 새 메일을 만들고, 입력해둔 받는 사람(여러
명이면 전부)과 제목("[이슈 리포트] 오늘 날짜 · N건" 형식), 방금 만든 본문을 채운 뒤
전송까지. 모은 항목이 없으면 "보낼 항목이 없습니다. 먼저 수집하세요"만 알려주고 끝내.

여기서 문제가 생기면(예: "새 아웃룩"이라 이 방식이 안 통하는 경우) 일단 그대로 오류가
나게 둬 — 다음 단계에서 다룰 거야. 이 버튼도 창이 멈추지 않게 해줘.""",
        need_install="pip install pywin32   (윈도우에서만)",
        criteria=[
            "윈도우 + 클래식 아웃룩 로그인 상태에서 pip install pywin32 를 실행했다",
            "뉴스나 DART를 한 번 이상 수집한 뒤 메일 보내기를 누르면 본인 메일함으로 실제 메일이 도착한다",
            "아웃룩이 꺼져 있으면 자동으로 켜지면서 발송된다 (로그인 창이 뜬다면 먼저 로그인)",
        ],
        code="""def _send_via_classic_outlook(subject: str, html_body: str, mail_to: list[str]) -> None:
    import win32com.client

    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.Subject = subject
    mail.To = "; ".join(mail_to)
    mail.HTMLBody = html_body
    mail.Send()


def on_send_mail(self) -> None:
    def task():
        if not self.collected:
            self.root.after(0, lambda: self.log("! 보낼 항목이 없습니다. 먼저 수집하세요."))
            return
        subject = f"[이슈 리포트] {datetime.now(KST).strftime('%m/%d')} · {len(self.collected)}건"
        html_body = build_html(self.collected)
        _send_via_classic_outlook(subject, html_body, self._list_field("mail_to"))
        self.root.after(0, lambda: self.log("메일 발송 완료"))
    self._run_in_background(task)""",
    ),
    dict(
        part=2, num="7", id="s7", time="10분",
        title="새 아웃룩 대응 + 메일 보내기 마무리",
        lib=None,
        desc="새 아웃룩(New Outlook)은 방금 만든 방식 자체를 지원하지 않는다. 그 경우를 감지해서 대신 "
             "처리해주는 안전망을 만든다.",
        prompt="""방금 만든 자동 발송은 "새 아웃룩(New Outlook)"에서는 지원이 안 돼서 오류가 나. 안 될 때를
위한 대안을 만들어줘 — 제목·받는 사람·본문이 이미 채워진 새 메일 작성 창을 열어줘서 사람이
[보내기]만 누르면 되게. 본문이 너무 길면 일부만 담고 "내용이 길어 일부만 담았다"고
붙여줘.

그리고 "메일 보내기" 버튼 동작을 마무리해줘. 진행 상황 칸에 알려주고 끝내는 경우가 셋 —
받는 사람이 하나도 없을 때, 윈도우가 아닌 컴퓨터일 때, 아웃룩 조작에 필요한 게 설치 안 됐을
때(설치 안내). 그 외에는 자동 발송을 먼저 시도해서 성공하면 "자동 발송 완료", 새 아웃룩이라
안 되면 그 사실을 알린 뒤 대안으로 넘어가 "메일 창 열기 완료, 보내기만 누르면 된다"고
알려줘.""",
        need_install=None,
        criteria=[
            "클래식 아웃룩 PC에서는 창 없이 바로 자동 발송된다",
            "새 아웃룩만 있는 PC에서는 진행 상황 칸에 안내가 뜨고, 내용이 채워진 메일 창이 자동으로 뜬다",
            "받는 사람을 비워두고 버튼을 누르면 에러 없이 안내 메시지만 뜬다",
        ],
        code="""def _open_draft_mail(subject: str, plain_body: str, mail_to: list[str]) -> None:
    import webbrowser

    body_limit = 1500
    body = plain_body[:body_limit]
    if len(plain_body) > body_limit:
        body += "\\n\\n(내용이 길어 일부만 담았습니다.)"

    mailto = (
        "mailto:" + quote(",".join(mail_to))
        + "?subject=" + quote(subject)
        + "&body=" + quote(body)
    )
    webbrowser.open(mailto)


def send_mail(subject: str, html_body: str, plain_body: str, mail_to: list[str], log) -> None:
    if not mail_to:
        log("! 받는 사람이 없습니다.")
        return

    if sys.platform != "win32":
        log("! 아웃룩 발송은 윈도우에서만 됩니다.")
        return

    try:
        import win32com.client  # noqa: F401
    except ImportError:
        log("! pywin32 가 설치되어 있지 않습니다. `pip install pywin32` 로 설치하세요.")
        return

    try:
        _send_via_classic_outlook(subject, html_body, mail_to)
        log(f"✓ 메일 발송 완료 (자동 발송) → {', '.join(mail_to)}")
        return
    except Exception as exc:
        log(f"! 자동 발송이 안 됩니다: {exc}")
        log("  '새 아웃룩(New Outlook)'만 설치돼 있으면 원래 이렇습니다.")

    log("→ 대신 제목·받는사람·내용을 채운 새 메일 창을 엽니다. 뜨는 창에서 [보내기]만 눌러주세요.")
    try:
        _open_draft_mail(subject, plain_body, mail_to)
        log("✓ 메일 초안 열기 완료 (수동 발송 필요)")
    except Exception as exc:
        log(f"! 메일 초안도 열지 못했습니다: {exc}")


def on_send_mail(self) -> None:
    def task():
        if not self.collected:
            self.root.after(0, lambda: self.log("! 보낼 항목이 없습니다. 먼저 수집하세요."))
            return
        subject = f"[이슈 리포트] {datetime.now(KST).strftime('%m/%d')} · {len(self.collected)}건"
        plain_body = "\\n".join(f"- [{i.source}] {i.title}\\n  {i.link}" for i in self.collected)
        html_body = build_html(self.collected)
        send_mail(subject, html_body, plain_body, self._list_field("mail_to"),
                  lambda m: self.root.after(0, lambda: self.log(m)))
    self._run_in_background(task)""",
    ),
    dict(
        part=2, num="8", id="s8", time="10분",
        title="전체 완성 — 전체 실행 버튼 추가",
        lib=None,
        desc="지금까지 만든 버튼들이 잘 이어지는지 다듬고, 한 번에 다 실행하는 버튼을 추가하면 완성이다.",
        prompt=""""전체 실행" 버튼을 하나 더 추가해줘. 누르면 뉴스 수집 → DART 수집 → 메일 보내기를 순서대로
한 번에 실행해줘 (수집된 게 없으면 메일은 보내지 말고 진행 상황 칸에 알려줘).

그리고 여러 버튼을 동시에 눌러도 꼬이지 않게 해줘 — 어떤 작업이 진행 중이면 다른 버튼도
잠시 안 눌리다가 끝나면 다시 눌리게. 여기까지 되면 완성이야.""",
        need_install=None,
        criteria=[
            "전체 실행 버튼을 누르면 뉴스 수집 → DART 수집 → 메일 보내기가 순서대로 진행되는 게 진행 상황 칸에 보인다",
            "작업이 진행되는 동안 버튼들이 흐리게 바뀌고, 끝나면 다시 눌러쓸 수 있다",
            "여기까지 됐으면 완성이다 — 축하한다",
        ],
        code="""def _set_buttons_enabled(self, enabled: bool) -> None:
    state = "normal" if enabled else "disabled"
    for b in self.buttons:
        b.configure(state=state)


def _run_in_background(self, task) -> None:
    self._set_buttons_enabled(False)

    def wrapper():
        try:
            task()
        finally:
            self.root.after(0, lambda: self._set_buttons_enabled(True))

    threading.Thread(target=wrapper, daemon=True).start()


def on_run_all(self) -> None:
    def task():
        self.root.after(0, lambda: self.log("전체 실행 시작..."))

        news_items, news_errors = collect_newsapi(self._list_field("keywords"), self.vars["newsapi_key"].get())
        for e in news_errors:
            self.root.after(0, lambda e=e: self.log(f"  ! {e}"))
        self._merge(news_items, "뉴스")

        dart_items, dart_errors = collect_dart(self._list_field("dart_watch"), self.vars["dart_key"].get())
        for e in dart_errors:
            self.root.after(0, lambda e=e: self.log(f"  ! {e}"))
        self._merge(dart_items, "DART")

        if not self.collected:
            self.root.after(0, lambda: self.log("! 수집된 항목이 없어 메일은 보내지 않습니다."))
            return

        subject = f"[이슈 리포트] {datetime.now(KST).strftime('%m/%d')} · {len(self.collected)}건"
        plain_body = "\\n".join(f"- [{i.source}] {i.title}\\n  {i.link}" for i in self.collected)
        html_body = build_html(self.collected)
        send_mail(subject, html_body, plain_body, self._list_field("mail_to"),
                  lambda m: self.root.after(0, lambda: self.log(m)))
    self._run_in_background(task)""",
    ),
    dict(
        part=3, num="9", id="s1", time="10분",
        title="언론사 RSS 추가하기 (보너스)",
        lib=None,
        desc="시간이 남으면 해보는 추가 실습. 지금은 키워드에 걸리는 기사만 모으는데, 언론사 자체를 "
             "구독해두면 키워드에 안 걸린 기사까지 훑을 수 있다. 이것도 인증키가 필요 없다.",
        prompt="""뉴스 소스를 하나 더 붙여줘. 지금은 내가 적은 키워드에 걸리는 기사만 모아서, 키워드에 안
걸린 중요한 기사는 놓치게 돼. 그래서 특정 언론사의 최신 기사를 통째로 받아오는 방식도 같이
쓰고 싶어.

연합뉴스·한국경제·매일경제 같은 곳은 최신 기사 목록을 프로그램이 그대로 받아올 수 있게
공개해두고 있어(인증키 필요 없음). 경제 분야 목록 주소를 알아서 골라 세 곳 정도 넣고, 각
언론사에서 최근 10개씩만.

출처는 "연합뉴스"처럼 언론사 이름으로. 어느 한 곳이 안 되면 그 언론사만 건너뛰고 나머지는
계속 진행하고, 어디가 안 됐는지는 뉴스 칸에 알려줘.

"뉴스 수집하기"와 "전체 실행" 둘 다 키워드 검색과 이 언론사 기사가 같이 실행돼서 함께
모이게 해줘. 겹치는 기사는 앞에서 만든 중복 정리가 걸러줄 거야.""",
        need_install=None,
        criteria=[
            "뉴스 수집하기 버튼을 누르면 뉴스 결과 칸에 언론사 이름이 붙은 기사도 함께 나온다",
            "키워드를 아무것도 안 적어도 언론사 기사는 들어온다",
            "어느 언론사가 안 되는 경우, 그 언론사만 건너뛰고 나머지는 정상적으로 들어온다",
        ],
        code="""PRESS_FEEDS = [
    ("연합뉴스 경제", "https://www.yna.co.kr/rss/economy.xml"),
    ("한국경제", "https://rss.hankyung.com/feed/economy.xml"),
    ("매일경제", "https://www.mk.co.kr/rss/30100041/"),
]


def collect_press_rss(feeds=PRESS_FEEDS, limit_per_feed: int = 10) -> tuple[list[Item], list[str]]:
    items: list[Item] = []
    errors: list[str] = []

    for label, url in feeds:
        parsed = feedparser.parse(url)

        if not parsed.entries:
            reason = getattr(parsed, "bozo_exception", None)
            errors.append(f"{label} 가져오기 실패: {reason}" if reason else f"{label} 0건")
            continue

        for entry in parsed.entries[:limit_per_feed]:
            dt = None
            if getattr(entry, "published_parsed", None):
                dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            items.append(Item(
                source=label,
                title=clean_text(entry.get("title", "")),
                link=entry.get("link", ""),
                dt=dt,
            ))

    return items, errors


# on_collect_news / on_run_all 안에서 collect_press_rss() 결과도 함께 _merge 한다""",
    ),
]
