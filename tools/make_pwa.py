"""실습 페이지를 「설치형 웹 앱(PWA)」 으로 — 크롬 · 엣지 주소창 오른쪽에 설치 아이콘이 뜨게 한다.

    python tools/make_pwa.py && python tools/build_page.py

저장소 맨 위(GitHub Pages 의 맨 위)에 세 가지를 만든다.
  manifest.webmanifest   앱 이름 · 아이콘 · 시작 주소
  sw.js                  서비스 워커 — 한 번 열어둔 교안은 인터넷이 끊겨도 열린다
  icons/*.png            설치 아이콘 (크롬 탭 아이콘과 같은 그림을 크게)
페이지 쪽 연결(<link rel="manifest"> 와 서비스 워커 등록)은 build_page.py 가 넣는다.
파일을 더블클릭해서 여는 경우(file://)에는 설치가 안 된다 — 웹 주소로 열었을 때만.
"""
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ORANGE, LINE = (201, 106, 26), (224, 177, 140)


def icon(size, pad=0.0):
    """크롬 탭 아이콘(64칸 그림)을 size 크기로. pad 는 둥근 마스크용 바깥 여백 비율."""
    big = size * 4                                  # 크게 그린 뒤 줄여서 가장자리를 부드럽게
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if pad:
        d.rectangle([0, 0, big, big], fill=ORANGE)
    else:
        d.rounded_rectangle([0, 0, big - 1, big - 1], radius=big * 14 / 64, fill=ORANGE)
    inner = big * (1 - 2 * pad)
    off = big * pad
    k = inner / 64

    def r(x, y, w, h, fill, rad=0):
        box = [off + x * k, off + y * k, off + (x + w) * k, off + (y + h) * k]
        d.rounded_rectangle(box, radius=rad * k, fill=fill) if rad else d.rectangle(box, fill=fill)

    r(14, 15, 30, 34, "white", 3)
    r(19, 21, 20, 5, ORANGE)
    r(19, 30, 20, 3, LINE)
    r(19, 37, 13, 3, LINE)
    pts = [(46, 31), (51, 31), (54, 34), (54, 45), (51, 48), (31, 48)]
    d.line([(off + x * k, off + y * k) for x, y in pts], fill="white", width=int(4 * k), joint="curve")
    return img.resize((size, size), Image.LANCZOS)


def main():
    os.makedirs(os.path.join(REPO, "icons"), exist_ok=True)
    icon(192).save(os.path.join(REPO, "icons", "icon-192.png"), optimize=True)
    icon(512).save(os.path.join(REPO, "icons", "icon-512.png"), optimize=True)
    icon(512, pad=0.12).save(os.path.join(REPO, "icons", "icon-512-maskable.png"), optimize=True)

    manifest = {
        "name": "DART·뉴스 크롤링 및 메일발송 프로그램 만들기",
        "short_name": "바이브코딩 실습",
        "description": "말로 시켜서 뉴스 · DART 공시를 모으고 메일로 보내는 프로그램 만들기 — 실습 교안",
        "lang": "ko",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": "#eef0ee",
        "theme_color": "#c96a1a",
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "icons/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    with open(os.path.join(REPO, "manifest.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # 서비스 워커 — 늘 인터넷의 최신 교안을 먼저 보고, 끊겼을 때만 저장해 둔 것을 쓴다.
    # 큰 내려받기 파일(downloads/)은 저장하지 않는다.
    sw = """const CACHE = "vibe-edu-v1";
const CORE = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png"];

self.addEventListener("install", (e) => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((keys) =>
    Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  if (url.origin !== location.origin || url.pathname.includes("/downloads/")) return;
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy));
        return res;
      })
      .catch(() => caches.match(e.request).then((hit) => hit || caches.match("index.html")))
  );
});
"""
    with open(os.path.join(REPO, "sw.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write(sw)
    print("manifest.webmanifest · sw.js · icons/ 3개 생성")


if __name__ == "__main__":
    main()
