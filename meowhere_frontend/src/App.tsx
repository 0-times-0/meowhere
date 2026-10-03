// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Home } from './pages/Home'
import { ReportDetail } from './components/ReportDetail'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Main page list */}
        <Route path="/" element={<Home />} />

        {/* Detailed page for a single pet report */}
        <Route path="/reports/:id" element={<ReportDetail />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App