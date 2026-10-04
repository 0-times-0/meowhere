import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createReport, getStoredSession, uploadPhoto } from '../api';
import MapView from '../components/MapView';
import { AnimalSex, Species } from '../types';

export const CreateReportPage: React.FC = () => {
  const navigate = useNavigate();
  const session = getStoredSession();

  const [title, setTitle] = useState('');
  const [species, setSpecies] = useState<Species>('cat');
  const [sex, setSex] = useState<AnimalSex>('unknown');
  const [coatColor, setCoatColor] = useState('');
  const [breed, setBreed] = useState('');
  const [shelterName, setShelterName] = useState('');
  const [contactPhone, setContactPhone] = useState('');
  const [description, setDescription] = useState('');
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [position, setPosition] = useState<[number, number]>([52.2297, 21.0122]);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!session) {
    return (
      <div className="page-container">
        <div className="alert alert-error">
          Aby dodać zgłoszenie, zaloguj się na górnym pasku (jako Mieszkaniec lub Straż Miejska).
        </div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      let uploadedPhotoUrl: string | undefined;
      if (photoFile) {
        uploadedPhotoUrl = await uploadPhoto(photoFile);
      }

      const created = await createReport({
        title: title.trim(),
        species,
        sex,
        coat_color: coatColor.trim() || undefined,
        breed: breed.trim() || undefined,
        shelter_name:
          session.role === 'municipal' ? shelterName.trim() || undefined : undefined,
        contact_phone: contactPhone.trim() || undefined,
        description: description.trim() || undefined,
        photo_url: uploadedPhotoUrl,
        latitude: position[0],
        longitude: position[1],
      });

      navigate(`/listing?id=${created.id}`);
    } catch (err: any) {
      setError(err.message || 'Nie udało się utworzyć zgłoszenia.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-container">
      <div className="form-card">
        <h2>
          {session.role === 'municipal'
            ? 'Nowy raport interwencyjny Straży Miejskiej (found_patrol)'
            : 'Zgłoś zaginięcie zwierzęcia (lost)'}
        </h2>
        <p className="muted-line">
          Zalogowano jako: <strong>{session.display_name}</strong> ({session.identifier})
        </p>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit} className="report-form">
          <label>
            Tytuł zgłoszenia *
            <input
              type="text"
              required
              minLength={3}
              maxLength={120}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={
                session.role === 'municipal'
                  ? 'np. Odłowiono rudego kota przy ul. Marszałkowskiej'
                  : 'np. Zaginął rudy kot Karmel na Mokotowie'
              }
            />
          </label>

          <div className="form-grid-3">
            <label>
              Gatunek *
              <select
                value={species}
                onChange={(e) => setSpecies(e.target.value as Species)}
              >
                <option value="cat">Kot</option>
                <option value="dog">Pies</option>
                <option value="other">Inne</option>
              </select>
            </label>

            <label>
              Płeć
              <select
                value={sex}
                onChange={(e) => setSex(e.target.value as AnimalSex)}
              >
                <option value="unknown">Nieznana</option>
                <option value="male">Samiec</option>
                <option value="female">Samica</option>
              </select>
            </label>

            <label>
              Telefon kontaktowy
              <input
                type="text"
                value={contactPhone}
                onChange={(e) => setContactPhone(e.target.value)}
                placeholder="+48 500 000 000"
              />
            </label>
          </div>

          <div className="form-grid-2">
            <label>
              Umaszczenie / kolor sierści
              <input
                type="text"
                value={coatColor}
                onChange={(e) => setCoatColor(e.target.value)}
                placeholder="np. rudy pręgowany z białym krawatem"
              />
            </label>

            <label>
              Rasa / typ
              <input
                type="text"
                value={breed}
                onChange={(e) => setBreed(e.target.value)}
                placeholder="np. Europejski / Beagle / Mieszaniec"
              />
            </label>
          </div>

          {session.role === 'municipal' && (
            <label>
              Schronisko / placówka docelowa *
              <input
                type="text"
                required
                value={shelterName}
                onChange={(e) => setShelterName(e.target.value)}
                placeholder="np. Schronisko na Paluchu"
              />
            </label>
          )}

          <label>
            Opis okoliczności i znaki szczególne
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Opisz zachowanie zwierzęcia, obrożę, czip, godzinę zdarzenia..."
            />
          </label>

          <label>
            Zdjęcie zwierzęcia (JPG, PNG, WEBP do 5 MB)
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => setPhotoFile(e.target.files?.[0] || null)}
            />
          </label>

          <div>
            <p style={{ fontWeight: 600, marginBottom: '8px' }}>
              Kliknij na mapie miejsce zdarzenia ({position[0].toFixed(4)},{' '}
              {position[1].toFixed(4)}):
            </p>
            <MapView
              selectable
              center={position}
              selectedPosition={position}
              onSelectPosition={(lat, lon) => setPosition([lat, lon])}
              height="340px"
            />
          </div>

          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Zapisywanie zgłoszenia...' : 'Opublikuj zgłoszenie'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateReportPage;