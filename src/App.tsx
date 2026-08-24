import { Navigate, Route, Routes, useParams } from 'react-router-dom'
import { Layout } from './components/Layout'
import { stepWithDemo } from './content'
import { DemoProvider } from './demo/store'
import { HomePage } from './pages/HomePage'
import { PromptsPage } from './pages/PromptsPage'
import { StepPage } from './pages/StepPage'

export default function App() {
  return (
    <DemoProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/steps/:slug" element={<StepPage />} />
          <Route path="/steps/:slug/:tab" element={<StepPage />} />
          <Route path="/prompts" element={<PromptsPage />} />
          {/* 데모는 각 단계 안으로 옮겼다. 예전 /demo/* 링크는 해당 단계로 보낸다. */}
          <Route path="/demo" element={<Navigate to="/" replace />} />
          <Route path="/demo/:section" element={<DemoRedirect />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </DemoProvider>
  )
}

function DemoRedirect() {
  const { section = '' } = useParams()
  const step = stepWithDemo(section)
  return <Navigate to={step ? `/steps/${step.slug}/demo` : '/'} replace />
}
