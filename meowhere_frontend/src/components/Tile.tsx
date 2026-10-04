import { Link } from 'react-router-dom'
import "leaflet/dist/leaflet.css";
import "./components.css"
import { MaxiMap, MiniMap } from './Map';

interface TileProps {
  id: number
  title: string
  image: string
  description: string
  contact?: string
  lat: number
  lon: number
}

export function Tile({ id, title, image, description, contact, lat, lon }: TileProps) {
  return (
    <Link to={`/reports/${id}`} className="tile-link">
      <div className="tile">
        <img src={image} alt={title} className="tile-image" />
        <div className="tile-content">
          <h3 className="tile-title">{title}</h3>
          <p className="tile-description">{description}</p>
          {contact && (
            <p className="tile-contact">
              <strong>Kontakt:</strong> {contact}
            </p>
          )}
          <p>Miejsce zgłoszenia:</p>
          <MiniMap
          latitude={lat}
          longtitude={lon}
          />
        </div>
      </div>
    </Link>
  )
}