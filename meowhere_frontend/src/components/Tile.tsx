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
    <Link to={`/reports/${id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
      <div className="tile">
        <img src={image} alt={title} />
        <h3>{title}</h3>
        <p>{description}</p>
        {contact && <p><strong>Kontakt:</strong> {contact}</p>}
      </div>
    </Link>
  )
}