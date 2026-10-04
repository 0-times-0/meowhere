// src/pages/AddReport.tsx
import { useState, FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import type { CreateReportInput } from '../types'
import { ClickMap } from '../components/Map'

export function AddReport() {
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [formData, setFormData] = useState<CreateReportInput>({
    title: '',
    description: '',
    coat_color: '',
    breed: '',
    sex: 'samica',
    species: 'cat',
    status: 'lost',
    photo_url: '',
    contact_phone: '',
    latitude: 50.0614,  // Domyślny środek Krakowa
    longitude: 19.9366,
  })

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/reports/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        throw new Error('Failed to create report')
      }

      // Return to homepage after successful post
      navigate('/')
    } catch (err) {
      console.error(err)
      setError('Coś poszło nie tak podczas dodawania zgłoszenia.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <Link to="/" className="back-link">← Powrót do listy</Link>

      <div className="form-card">
        <h2>Dodaj nowe zgłoszenie</h2>

        {error && <p className="error-message">{error}</p>}

        <form onSubmit={handleSubmit} className="report-form">
          <div className="form-group">
            <label htmlFor="title">Tytuł *</label>
            <input
              type="text"
              id="title"
              name="title"
              required
              placeholder="np. Zaginął kot"
              value={formData.title}
              onChange={handleChange}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="species">Gatunek</label>
              <select id="species" name="species" value={formData.species} onChange={handleChange}>
                <option value="cat">Kot</option>
                <option value="dog">Pies</option>
                <option value="other">Inne</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="status">Status</label>
              <select id="status" name="status" value={formData.status} onChange={handleChange}>
                <option value="lost">Zaginiony</option>
                <option value="found_patrol">Zabezpieczony (Straż)</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="breed">Rasa</label>
              <input
                type="text"
                id="breed"
                name="breed"
                placeholder="np. dachowiec / kundelek"
                value={formData.breed}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="coat_color">Umaszczenie</label>
              <input
                type="text"
                id="coat_color"
                name="coat_color"
                placeholder="np. biało-czarny"
                value={formData.coat_color}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="sex">Płeć</label>
              <select id="sex" name="sex" value={formData.sex} onChange={handleChange}>
                <option value="samica">Samica</option>
                <option value="samiec">Samiec</option>
                <option value="nieznana">Nieznana</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Opis *</label>
            <textarea
              id="description"
              name="description"
              rows={3}
              required
              placeholder="np. Białe łapki, reaguje na imię..."
              value={formData.description}
              onChange={handleChange}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="photo_url">URL zdjęcia</label>
              <input
                type="url"
                id="photo_url"
                name="photo_url"
                placeholder="https://..."
                value={formData.photo_url}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="contact_phone">Telefon kontaktowy *</label>
              <input
                type="tel"
                id="contact_phone"
                name="contact_phone"
                required
                placeholder="+48123456789"
                value={formData.contact_phone}
                onChange={handleChange}
              />
            </div>
          </div>

          {/* Sekcja Mapy do wyboru lokalizacji */}
          <div className="form-group" style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
            <label>Zaznacz lokalizację na mapie (kliknij w miejsce) *</label>
            <div style={{ borderRadius: 'var(--radius-sm)', overflow: 'hidden', border: '1px solid var(--border-color)' }}>
              <ClickMap 
                onLocationSelect={(lat, lng) => 
                  setFormData(prev => ({ ...prev, latitude: lat, longitude: lng }))
                } 
              />
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--accent)', marginTop: '0.5rem' }}>
              Wybrane współrzędne: {formData.latitude.toFixed(6)}, {formData.longitude.toFixed(6)}
            </p>
          </div>

          <button type="submit" disabled={submitting} className="btn-submit">
            {submitting ? 'Zapisywanie...' : 'Dodaj zgłoszenie'}
          </button>
        </form>
      </div>
    </div>
  )
}