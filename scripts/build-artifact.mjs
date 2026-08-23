/**
 * 교육 프로그램 전체를 파일 하나(HTML)로 묶는다.
 *
 * 목적: Node.js 설치나 소스 다운로드 없이 링크만 열어서 쓰게 하는 것.
 * 결과물은 CSS·JS가 모두 인라인된 자립형 HTML 이라 사내 위키에 첨부하거나
 * 파일 서버에 올려도 그대로 열린다.
 *
 * 주의: 아티팩트로 게시할 때 호스트가 <!doctype html><head>…</head><body> 를
 * 감싸주므로, 이 스크립트는 그 안에 들어갈 "본문"만 출력한다.
 */
import { execFileSync } from 'node:child_process'
import { mkdirSync, readFileSync, readdirSync, writeFileSync, rmSync } from 'node:fs'
import { join } from 'node:path'

const OUT_DIR = 'artifact'
const OUT_FILE = join(OUT_DIR, 'vibe-coding-education.html')
const BUILD_DIR = 'dist-artifact'
const TITLE = '바이브 코딩 교육 프로그램'

rmSync(BUILD_DIR, { recursive: true, force: true })

console.log('· 빌드 (해시 라우터 모드)')
execFileSync('npx', ['vite', 'build', '--outDir', BUILD_DIR], {
  stdio: 'inherit',
  env: { ...process.env, VITE_HASH_ROUTER: '1' },
})

const assetDir = join(BUILD_DIR, 'assets')
const files = readdirSync(assetDir)
const jsFile = files.find((f) => f.endsWith('.js'))
const cssFile = files.find((f) => f.endsWith('.css'))
if (!jsFile || !cssFile) throw new Error('빌드 결과에서 js/css 파일을 찾지 못했습니다')

const css = readFileSync(join(assetDir, cssFile), 'utf8')
const js = readFileSync(join(assetDir, jsFile), 'utf8')

// 스크립트 문자열 안에 </script> 가 있으면 인라인할 때 태그가 조기 종료된다.
const safeJs = js.replaceAll('</script>', '<\\/script>')

const html = `<title>${TITLE}</title>
<meta name="description" content="프롬프트를 복사해 AI에게 붙여넣으면서 업무 캘린더·주간보고·인수인계 웹앱을 15단계로 만드는 사내 교육 프로그램" />
<style>
${css}
</style>
<div id="root"></div>
<script type="module">
${safeJs}
</script>
`

mkdirSync(OUT_DIR, { recursive: true })
writeFileSync(OUT_FILE, html)
rmSync(BUILD_DIR, { recursive: true, force: true })

const kb = (n) => (n / 1024).toFixed(0) + ' kB'
console.log(`\n✓ ${OUT_FILE}  (${kb(Buffer.byteLength(html))})`)
console.log(`  CSS ${kb(css.length)} + JS ${kb(js.length)} 인라인`)
