import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // 교육 콘텐츠(프롬프트·샘플 코드)가 문자열로 들어 있어 번들이 큰 편이다.
  // 정적 파일 하나를 사내망에서 받는 구조라 코드 분할 없이 그대로 둔다.
  build: { chunkSizeWarningLimit: 900 },
  server: { host: '0.0.0.0', port: 5173 },
  preview: { host: '0.0.0.0', port: 4173 },
})
