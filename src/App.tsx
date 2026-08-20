import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { DemoProvider } from './demo/store'
import { DemoPage } from './pages/DemoPage'
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
          <Route path="/prompts" element={<PromptsPage />} />
          <Route path="/demo" element={<Navigate to="/demo/calendar" replace />} />
          <Route path="/demo/:section" element={<DemoPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </DemoProvider>
  )
}
