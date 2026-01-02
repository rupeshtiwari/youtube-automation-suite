import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Shorts from './pages/Shorts'
import Calendar from './pages/Calendar'
import Sessions from './pages/Sessions'
import ContentPreview from './pages/ContentPreview'
import Insights from './pages/Insights'
import Activity from './pages/Activity'
import Settings from './pages/Settings'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/shorts" element={<Shorts />} />
        <Route path="/calendar" element={<Calendar />} />
        <Route path="/sessions" element={<Sessions />} />
        <Route path="/content-preview" element={<ContentPreview />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/activity" element={<Activity />} />
        <Route path="/config" element={<Settings />} />
      </Routes>
    </Layout>
  )
}

export default App
