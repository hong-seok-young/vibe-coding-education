import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// GitHub Pages 는 https://<계정>.github.io/<저장소>/ 하위 경로로 서빙되므로
// 빌드할 때 VITE_BASE 로 그 경로를 알려준다. 로컬·Coolify 배포는 루트('/')를 쓴다.
const base = process.env.VITE_BASE ?? '/'

export default defineConfig({
  base,
  plugins: [react(), tailwindcss()],
  // 교육 콘텐츠(프롬프트·샘플 코드)가 문자열로 들어 있어 번들이 큰 편이다.
  // 정적 파일 하나를 사내망에서 받는 구조라 코드 분할 없이 그대로 둔다.
  build: { chunkSizeWarningLimit: 900 },
  server: { host: '0.0.0.0', port: 5173 },
  preview: { host: '0.0.0.0', port: 4173 },
})
