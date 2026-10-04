// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Home } from './pages/Home'
import { ReportDetail } from './components/ReportDetail'
import { AddReport } from './pages/AddReport'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/reports/new" element={<AddReport />} />
        <Route path="/reports/:id" element={<ReportDetail />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App