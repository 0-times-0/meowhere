// src/components/ReportDetail.tsx
import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import type { Report } from '../types'

export function ReportDetail() {
  const { id } = useParams<{ id: string }>()
  const [report, setReport] = useState<Report | null>(null)

  useEffect(() => {
    fetch(`http://localhost:8000/reports/${id}`)
      .then((res) => res.json())
      .then((data: Report) => setReport(data))
      .catch((err) => console.error('Failed to fetch report:', err))
  }, [id])

  if (!report) {
    return <p>Ładowanie szczegółów...</p>
  }

  return (
    <div className="report-detail">
      <Link to="/">← Powrót do listy</Link>

      <h1>{report.title}</h1>
      <img src={report.photo_url} alt={report.title} style={{ maxWidth: '400px' }} />

      <p><strong>Gatunek:</strong> {report.species}</p>
      <p><strong>Status:</strong> {report.status}</p>
      <p><strong>Opis:</strong> {report.description}</p>
      <p><strong>Kontakt:</strong> {report.contact_phone}</p>
      <p><strong>Lokalizacja:</strong> {report.latitude}, {report.longitude}</p>
    </div>
  )
}