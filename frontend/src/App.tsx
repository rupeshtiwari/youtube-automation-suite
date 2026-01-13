import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Sessions from './pages/Sessions'
import ShortsNew from './pages/ShortsNew'
import ShortsLibrary from './pages/ShortsLibrary'
import Calendar from './pages/Calendar'
import ContentPreview from './pages/ContentPreview'
import Insights from './pages/Insights'
import Activity from './pages/Activity'
import Settings from './pages/Settings'
import AudioGenerator from './pages/AudioGenerator'
import AudioLibrary from './pages/AudioLibrary'
import VideoUpload from './pages/VideoUpload'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/sessions" element={<Sessions />} />
        <Route path="/shorts" element={<ShortsNew />} />
        <Route path="/shorts-library" element={<ShortsLibrary />} />
        <Route path="/calendar" element={<Calendar />} />
        <Route path="/content-preview" element={<ContentPreview />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/activity" element={<Activity />} />
        <Route path="/audio-generator" element={<AudioGenerator />} />
        <Route path="/audio-library" element={<AudioLibrary />} />
        <Route path="/video-upload" element={<VideoUpload />} />
        <Route path="/settings" element={<Settings />} />
        {/* Catch-all for unknown routes */}
        <Route path="*" element={<Dashboard />} />
      </Routes>
    </Layout>
  )
}

export default App
