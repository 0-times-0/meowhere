import { Link } from 'react-router-dom'

interface TileProps {
  id: number
  title: string
  image: string
  description: string
  contact?: string
}

export function Tile({ id, title, image, description, contact }: TileProps) {
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
        </div>
      </div>
    </Link>
  )
}