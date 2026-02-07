import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import EngagementWizard from './pages/EngagementWizard'
import DashboardPage from './pages/Dashboard'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/engagement/new" element={<EngagementWizard />} />
        <Route path="/engagement/:id/wizard" element={<EngagementWizard />} />
        <Route path="/engagement/:id/dashboard" element={<DashboardPage />} />
      </Route>
    </Routes>
  )
}
