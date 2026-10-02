"""교안 화면 애니메이션 — 글 · 도식이 차례로 떠오르고, 숫자는 0 부터 올라간다.

build_page.py 가 ANIMATE = True 일 때만 이 파일의 CSS · JS 를 페이지에 붙인다.
문제가 생기면 build_page.py 의 ANIMATE 를 False 로 바꾸고 다시 만들면 예전 화면 그대로다.
(넣기 전 상태는 git 태그 before-animation 으로도 남아 있다.)

동작
  · 페이지가 바뀔 때마다 그 페이지의 글 · 상자 · 표 줄이 화면에 들어오는 순서대로 떠오른다
    (스크롤해서 새로 보이는 것도 그때 떠오른다)
  · SVG 도식은 왼쪽에서 오른쪽으로 상자가 나타나고, 화살표는 선을 그리듯 이어진다
  · 강조된 숫자(굵은 글씨 · 한도 칸 · 도식 속 숫자)는 0 부터 올라간다
    시각(06:00) · 날짜(9/18) · 연도 · 「STEP 3」「DART 30」 같은 이름 속 번호는 건드리지 않는다
  · 움직임 줄이기(윈도우 설정)를 켠 사람과 인쇄할 때는 아무것도 움직이지 않는다
  · 자바스크립트가 안 돌면 원래 화면 그대로 보인다 (숨기는 것도 자바스크립트가 한다)
"""

ANIM_STYLE = '''<style>
  /* ── 화면 애니메이션 (tools/anim.py) ── */
  .an-on .an-wait { opacity: 0; }
  .an-on .an-svg-wait > :not(defs) { opacity: 0; }

  @keyframes an-up   { from { opacity: 0; translate: 0 14px; } to { opacity: 1; translate: 0 0; } }
  @keyframes an-pop  { from { opacity: 0; translate: 0 10px; scale: 0.96; } to { opacity: 1; translate: 0 0; scale: 1; } }
  @keyframes an-fade { from { opacity: 0; } to { opacity: 1; } }
  @keyframes an-grow { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }
  @keyframes an-draw {
    0%   { opacity: 0; stroke-dashoffset: var(--an-len); }
    1%   { opacity: 1; }
    100% { opacity: 1; stroke-dashoffset: 0; }
  }

  .an-up   { animation: an-up 0.6s cubic-bezier(0.2, 0.7, 0.2, 1) both; }
  .an-pop  { animation: an-pop 0.5s cubic-bezier(0.2, 0.8, 0.25, 1) both; }
  .an-fade { animation: an-fade 0.45s ease both; }
  .an-grow { animation: an-grow 0.9s cubic-bezier(0.3, 0.7, 0.2, 1) both; }
  .an-s    { animation: an-pop 0.5s cubic-bezier(0.2, 0.8, 0.25, 1) both;
             transform-box: fill-box; transform-origin: center; }
  .an-draw { animation: an-draw 0.55s ease-out both; }

  .an-num { font-variant-numeric: tabular-nums; }
  span.an-num { display: inline-block; text-align: right; }

  @media print {
    .an-on .an-wait, .an-on .an-svg-wait > * { opacity: 1 !important; }
    .an-up, .an-pop, .an-fade, .an-grow, .an-s, .an-draw { animation: none !important; }
  }
</style>'''

ANIM_SCRIPT = r'''
<script>
/* ── 화면 애니메이션 (tools/anim.py) ── */
(function () {
  if (!("IntersectionObserver" in window) || !window.MutationObserver) return;
  if (window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var root = document.documentElement;
  root.classList.add("an-on");

  // 떠오르는 덩어리 — 페이지 · 묶음의 바로 아래 칸들
  var SEL_UP = [".page > *", ".page-head > *", ".page-inner > *", "section.group > *", ".v-block > *",
                ".xf > *", ".cert > *", ".ways > *", ".criteria-box > *", "details > :not(summary)"].join(",");
  // 하나씩 차례로 튀어나오는 것 — 흐름 · 카드 · 목록의 칸
  var SEL_POP = [".vflow > *", ".build-grid > *", ".vs > *", ".tips > *", ".pv-map > *", ".pv-steps > *",
                 ".install-list > li", ".items > *", ".rv > *", ".step-todo > li", ".cert-lanes > *",
                 ".cert-lane > *", ".ways-pros > li", ".xf-cmp > *", ".xf-nums > *", ".xf-pipe > *",
                 ".pv-parcel-row > *", ".pv-flow > *", ".pv-lines > *", ".cycle > *", ".mw > *",
                 ".apitable tbody > tr"].join(",");
  // 왼쪽부터 차오르는 막대
  var SEL_GROW = ".pv-fill > em, .xf-bar > span";
  var SEL_ALL = SEL_GROW + "," + SEL_POP + "," + SEL_UP;
  var KINDS = ["an-up", "an-pop", "an-fade", "an-grow", "an-s", "an-draw"];

  /* ── 숫자 찾기 — 강조된 곳의 숫자만 an-num 칸으로 감싼다 (처음 한 번) ── */
  var NUM_HOST = "b, strong, .api-quota, .step-time, .cap, .pv-sum, .xf-bar span, .dg text";
  var NUM_RE = /\d{1,3}(?:,\d{3})+|\d+/g;
  var SVG_NS = "http://www.w3.org/2000/svg";

  function wrapNumbers() {
    document.querySelectorAll(".page").forEach(function (page) {
      page.querySelectorAll(NUM_HOST).forEach(function (host) {
        if (host.closest("pre, code, .prompt-box")) return;
        var walker = document.createTreeWalker(host, NodeFilter.SHOW_TEXT), texts = [];
        while (walker.nextNode()) texts.push(walker.currentNode);
        texts.forEach(function (t) {
          var p = t.parentNode;
          if (p.classList && p.classList.contains("an-num")) return;
          var s = t.nodeValue, m, last = 0, parts = [];
          NUM_RE.lastIndex = 0;
          while ((m = NUM_RE.exec(s))) {
            var raw = m[0], before = s.slice(0, m.index), a = s.charAt(m.index - 1), z = s.charAt(m.index + raw.length);
            var to = parseInt(raw.replace(/,/g, ""), 10), comma = raw.indexOf(",") !== -1;
            if (/[:\/~.\-A-Za-z]/.test(a) || /[:\/~.\-A-Za-z0-9]/.test(z)) continue;   // 06:00 · 9/18 · 3.14 · A1
            if (/[A-Za-z]\s*$/.test(before)) continue;                                   // STEP 3 · DART 30 · TOP 10 같은 이름
            if (!comma && raw.length === 4 && to >= 1900 && to <= 2099) continue;         // 연도
            if (to < 2) continue;                                                         // 0 · 1 은 올라갈 게 없다
            if (before.trim() === "" && z === " " && to < 10) continue;                   // 「1 DART …」 같은 순번
            parts.push([m.index, raw, to, comma]);
          }
          if (!parts.length) return;
          var isSvg = p instanceof SVGElement, frag = document.createDocumentFragment();
          parts.forEach(function (q) {
            if (q[0] > last) frag.appendChild(document.createTextNode(s.slice(last, q[0])));
            var n = isSvg ? document.createElementNS(SVG_NS, "tspan") : document.createElement("span");
            n.setAttribute("class", "an-num");
            n.__to = q[2]; n.__comma = q[3];
            n.textContent = q[1];
            frag.appendChild(n);
            last = q[0] + q[1].length;
          });
          if (last < s.length) frag.appendChild(document.createTextNode(s.slice(last)));
          p.replaceChild(frag, t);
        });
      });
    });
  }

  function fmt(n, v) { return n.__comma ? v.toLocaleString("en-US") : String(v); }

  function prepNumber(n) {
    n.__tok = (n.__tok || 0) + 1;
    if (!(n instanceof SVGElement)) {
      n.style.minWidth = "";
      n.textContent = fmt(n, n.__to);
      n.style.minWidth = n.getBoundingClientRect().width + "px";   // 올라가는 동안 옆 글자가 흔들리지 않게
    }
    n.textContent = fmt(n, 0);
  }

  function countUp(n, delay) {
    var tok = n.__tok, to = n.__to, dur = Math.min(1400, 700 + to * 4);
    setTimeout(function () {
      var t0 = null;
      function frame(now) {
        if (n.__tok !== tok) return;
        if (t0 === null) t0 = now;
        var k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
        n.textContent = fmt(n, Math.round(to * e));
        if (k < 1) requestAnimationFrame(frame);
        else n.style.minWidth = "";
      }
      requestAnimationFrame(frame);
    }, delay);
  }

  function finishNumbers() {
    document.querySelectorAll(".an-num").forEach(function (n) {
      n.__tok = (n.__tok || 0) + 1;
      n.textContent = fmt(n, n.__to);
      if (n.style) n.style.minWidth = "";
    });
  }

  /* ── 하나씩 재생 ── */
  function kindOf(el) {
    if (el.matches(SEL_GROW)) return "an-grow";
    if (el.tagName === "TR") return "an-fade";
    if (el.matches(SEL_POP)) return "an-pop";
    return "an-up";
  }

  function play(el, delay) {
    el.style.animationDelay = delay + "ms";
    el.classList.add(el.__anKind);
    el.classList.remove("an-wait");
  }

  // 도식 — 왼쪽 상자부터 오른쪽으로, 화살표는 선을 그리며
  function playSvg(svg, delay) {
    var vb = svg.viewBox && svg.viewBox.baseVal;
    var W = (vb && vb.width) || 960, H = (vb && vb.height) || 400;
    Array.prototype.forEach.call(svg.children, function (c) {
      var tag = c.tagName.toLowerCase();
      if (tag === "defs") return;
      var b; try { b = c.getBBox(); } catch (e) { b = { x: 0, y: 0, width: 0, height: 0 }; }
      var cls = c.getAttribute("class") || "", line = /^(polyline|line|path)$/.test(tag), t;
      if (/(^|\s)(lane|col)(\s|$)/.test(cls)) t = (b.y / H) * 150;                 // 바탕 띠 · 열 제목 먼저
      else t = 120 + ((line ? b.x : b.x + b.width / 2) / W) * 700 + (b.y / H) * 220 + (line ? 140 : 0);
      t = Math.round(delay + t);
      var dashed = line && (getComputedStyle(c).strokeDasharray || "none") !== "none";
      var len = line && !dashed && c.getTotalLength ? c.getTotalLength() : 0;
      if (len > 0) {
        c.style.setProperty("--an-len", len);
        c.style.strokeDasharray = len;
        var mk = c.getAttribute("marker-end");
        if (mk) { c.__mk = mk; c.removeAttribute("marker-end"); }       // 화살촉은 선이 다 그려진 뒤
        c.classList.add("an-draw");
      } else {
        c.classList.add(line ? "an-fade" : "an-s");
      }
      c.style.animationDelay = t + "ms";
      c.querySelectorAll && c.querySelectorAll(".an-num").forEach(function (n) { countUp(n, t + 120); });
    });
    svg.classList.remove("an-svg-wait");
  }

  function restore(el) {
    KINDS.forEach(function (k) { el.classList.remove(k); });
    el.style.animationDelay = "";
    if (el.style.getPropertyValue("--an-len")) {
      el.style.removeProperty("--an-len");
      el.style.strokeDasharray = "";
    }
    if (el.__mk) { el.setAttribute("marker-end", el.__mk); el.__mk = null; }
  }

  // 애니메이션이 끝나면 원래 모습으로 — 이후 마우스 효과 등은 그대로 동작
  document.addEventListener("animationend", function (e) {
    if (/^an-/.test(e.animationName) && e.target.classList) restore(e.target);
  }, true);

  function byDocOrder(a, b) {
    return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
  }

  var io = new IntersectionObserver(function (entries) {
    var hits = entries.filter(function (e) { return e.isIntersecting; }).map(function (e) { return e.target; });
    if (!hits.length) return;
    hits.sort(byDocOrder);
    var step = Math.min(70, 650 / hits.length);
    hits.forEach(function (el, i) {
      io.unobserve(el);
      var d = Math.round(i * step);
      if (el.__anKind === "svg") playSvg(el, d);
      else if (el.__anKind === "num") countUp(el, d + 150);
      else play(el, d);
    });
  }, { rootMargin: "0px 0px -6% 0px", threshold: 0 });

  function reset() {
    io.disconnect();
    document.querySelectorAll(".an-wait").forEach(function (el) { el.classList.remove("an-wait"); });
    document.querySelectorAll(".an-svg-wait").forEach(function (el) { el.classList.remove("an-svg-wait"); });
    document.querySelectorAll("." + KINDS.join(", .")).forEach(restore);
    finishNumbers();
  }

  function activate(page) {
    reset();
    page.querySelectorAll(SEL_ALL).forEach(function (el) {
      if (el.closest("pre")) return;
      el.__anKind = kindOf(el);
      el.classList.add("an-wait");
      io.observe(el);
    });
    page.querySelectorAll(".dg svg").forEach(function (svg) {
      svg.__anKind = "svg";
      svg.classList.add("an-svg-wait");
      io.observe(svg);
    });
    page.querySelectorAll(".an-num").forEach(function (n) {
      prepNumber(n);
      if (!(n instanceof SVGElement)) { n.__anKind = "num"; io.observe(n); }
    });
  }

  wrapNumbers();

  // 페이지가 바뀌는 순간(.page 에 active 가 붙을 때)마다 다시 재생
  var mo = new MutationObserver(function (records) {
    records.forEach(function (r) {
      var was = (r.oldValue || "").split(/\s+/).indexOf("active") !== -1;
      if (!was && r.target.classList.contains("active")) activate(r.target);
    });
  });
  document.querySelectorAll(".page").forEach(function (p) {
    mo.observe(p, { attributes: true, attributeFilter: ["class"], attributeOldValue: true });
  });

  var first = document.querySelector(".page.active");
  if (first) activate(first);
})();
</script>'''
