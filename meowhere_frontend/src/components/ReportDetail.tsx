import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import type { Report } from '../types'
import "leaflet/dist/leaflet.css";
import "./components.css"
import { MaxiMap, MiniMap } from './Map';

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
    <div>
      <Link to="/" className="back-link">← Powrót do listy</Link>

      <div className="report-detail">
        <h1>{report.title}</h1>

        <div className="report-detail-layout">
          {/* Column 1: Image */}
          

          {/* Column 2: Info & Future Map */}
          <div className="report-info-group">
            <div>
            <span><img src={report.photo_url} alt={report.title} className="report-detail-image" /></span>
            </div>
            <div className="report-info-row">
              <span className="report-info-label">Gatunek:</span>
              <span>{report.species}</span>
            </div>
            <div className="report-info-row">
              <span className="report-info-label">Status:</span>
              <span>{report.status}</span>
            </div>
            <div className="report-info-row">
              <span className="report-info-label">Opis:</span>
              <span>{report.description}</span>
            </div>
            <div className="report-info-row">
              <span className="report-info-label">Kontakt:</span>
              <span>{report.contact_phone}</span>
            </div>
            <div className="report-info-row">
              <span className="report-info-label">Lokalizacja:</span>
              <span>{report.latitude}, {report.longitude}</span>
            </div>
            <MaxiMap
              cat={report.species=="cat"?true:false}
              latitude={report.latitude}
              longtitude={report.longitude}
            />

            {/* PLACEHOLDER FOR MAP COMPONENT FUTURE INTEGRATION */}
            
{/* <Map lat={report.latitude} lng={report.longitude} /> */}
{/* <div className="map-container"> </div> */}
          </div>
        </div>
      </div>
    </div>
  )
}