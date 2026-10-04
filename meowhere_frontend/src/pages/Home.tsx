// src/pages/Home.tsx
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import creature from '../assets/creature.webp'
import { Tile } from '../components/Tile'
import type { Report } from '../types'

export function Home() {
  const [reports, setReports] = useState<Report[]>([])

  useEffect(() => {
    fetch('http://localhost:8000/reports')
      .then((res) => res.json())
      .then((data: Report[]) => setReports(data))
      .catch((err) => console.error('Failed to fetch reports:', err))
  }, [])

  return (
    <>
      <div className="header-action-bar">
        <h1 className="page-header">Meow</h1>
        <Link to="/reports/new" className="btn-primary">
          + Dodaj zgłoszenie
        </Link>
      </div>

      <div className="reports-list">
        {reports.map((report) => (
          <Tile
            key={report.id}
            id={report.id}
            title={report.title}
            image={report.photo_url}
            description={report.description}
            contact={report.contact_phone}
            lat={report.latitude}
            lon={report.longitude}
            iscat={report.species=="cat"?true:false}
          />
        ))}
      </div>

      <img src={creature} alt="Kreatura" className="creature-footer" />
    </>
  )
}