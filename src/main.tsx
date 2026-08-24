import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, HashRouter } from 'react-router-dom'
import App from './App'
import { initTheme } from './lib/theme'
import './index.css'

initTheme()

// 단일 HTML 파일로 배포할 때(아티팩트 등)는 서버 라우팅 폴백이 없으므로 해시 라우터를 쓴다.
// 일반 배포(Coolify + nginx)에서는 주소가 깔끔한 BrowserRouter 를 그대로 쓴다.
const hashMode = import.meta.env.VITE_HASH_ROUTER === '1'

// 하위 경로에 배포된 경우(GitHub Pages 등) 라우터도 그 경로를 알아야 한다.
// BASE_URL 은 빌드 시 vite 가 넣어준다. '/vibe-coding-education/' → '/vibe-coding-education'
const basename = import.meta.env.BASE_URL.replace(/\/$/, '')

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {hashMode ? (
      <HashRouter>
        <App />
      </HashRouter>
    ) : (
      <BrowserRouter basename={basename}>
        <App />
      </BrowserRouter>
    )}
  </StrictMode>,
)
