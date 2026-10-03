// src/pages/Home.tsx
import { useState, useEffect } from 'react'
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
      <h1>Meow</h1>

      <div className="reports-list">
        {reports.map((report) => (
          <Tile
            key={report.id}
            id={report.id}
            title={report.title}
            image={report.photo_url}
            description={report.description}
            contact={report.contact_phone}
          />
        ))}
      </div>

      <img src={creature} alt="Kreatura" />
    </>
  )
}