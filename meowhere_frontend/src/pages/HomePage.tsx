import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  fetchMyReports,
  fetchReports,
  getStoredSession,
  resolvePhotoUrl,
} from '../api';
import MapView from '../components/MapView';
import { Report, ReportStatus, Species } from '../types';

export const HomePage: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [species, setSpecies] = useState<Species | ''>('');
  const [statusFilter, setStatusFilter] = useState<ReportStatus | ''>('');
  const [onlyMine, setOnlyMine] = useState<boolean>(false);

  const [useRadiusFilter, setUseRadiusFilter] = useState<boolean>(false);
  const [searchCenter, setSearchCenter] = useState<[number, number]>([52.2297, 21.0122]);
  const [radiusKm, setRadiusKm] = useState<number>(5);

  const session = getStoredSession();

  const loadReports = async () => {
    setLoading(true);
    setError(null);
    try {
      if (onlyMine && session) {
        const myData = await fetchMyReports();
        setReports(myData);
      } else {
        const data = await fetchReports({
          species,
          status: statusFilter,
          ...(useRadiusFilter
            ? {
                lat: searchCenter[0],
                lon: searchCenter[1],
                radius_km: radiusKm,
              }
            : {}),
        });
        setReports(data);
      }
    } catch (err: any) {
      setError(err.message || 'Nie udało się pobrać zgłoszeń.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, [species, statusFilter, onlyMine, useRadiusFilter, searchCenter[0], searchCenter[1], radiusKm]);

  const statusBadge = (status: ReportStatus) => {
    if (status === 'lost') {
      return <span className="badge badge-lost">Zaginione</span>;
    }
    if (status === 'found_patrol') {
      return <span className="badge badge-patrol">Straż Miejska / Odłowione</span>;
    }
    return <span className="badge badge-resolved">Rozwiązane</span>;
  };

  return (
    <div className="page-container">
      <section className="hero-banner">
        <div>
          <h1>MEOWHERE — Mapa Zaginionych i Odnalezionych Zwierząt</h1>
          <p>
            Wspólna baza mieszkańców oraz Eko-Patrolu Straży Miejskiej z wyszukiwaniem
            przestrzennym PostGIS i dopasowywaniem zgłoszeń AI.
          </p>
        </div>
        <div className="hero-actions">
          <Link to="/post" className="btn btn-primary">
            + Dodaj zgłoszenie
          </Link>
        </div>
      </section>

      <section className="filters-card">
        <div className="filters-row">
          <label>
            Gatunek:
            <select
              value={species}
              onChange={(e) => setSpecies(e.target.value as Species | '')}
              disabled={onlyMine}
            >
              <option value="">Wszystkie</option>
              <option value="cat">Kot</option>
              <option value="dog">Pies</option>
              <option value="other">Inne</option>
            </select>
          </label>

          <label>
            Status:
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as ReportStatus | '')}
              disabled={onlyMine}
            >
              <option value="">Wszystkie</option>
              <option value="lost">Zaginione (mieszkańcy)</option>
              <option value="found_patrol">Odłowione (Straż Miejska)</option>
              <option value="resolved">Rozwiązane</option>
            </select>
          </label>

          <label className="checkbox-inline">
            <input
              type="checkbox"
              checked={useRadiusFilter}
              onChange={(e) => setUseRadiusFilter(e.target.checked)}
              disabled={onlyMine}
            />
            Filtruj w promieniu ({radiusKm} km — kliknij na mapie środek)
          </label>

          {useRadiusFilter && !onlyMine && (
            <input
              type="range"
              min={1}
              max={30}
              value={radiusKm}
              onChange={(e) => setRadiusKm(Number(e.target.value))}
            />
          )}

          {session && (
            <label className="checkbox-inline">
              <input
                type="checkbox"
                checked={onlyMine}
                onChange={(e) => setOnlyMine(e.target.checked)}
              />
              Tylko moje zgłoszenia
            </label>
          )}
        </div>
      </section>

      <section style={{ marginBottom: '24px' }}>
        <MapView
          reports={reports}
          center={searchCenter}
          selectable={useRadiusFilter && !onlyMine}
          selectedPosition={useRadiusFilter && !onlyMine ? searchCenter : null}
          searchRadiusKm={useRadiusFilter && !onlyMine ? radiusKm : null}
          onSelectPosition={(lat, lon) => setSearchCenter([lat, lon])}
          height="430px"
        />
      </section>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <p>Ładowanie zgłoszeń...</p>
      ) : reports.length === 0 ? (
        <div className="empty-card">Brak zgłoszeń spełniających wybrane kryteria.</div>
      ) : (
        <div className="reports-grid">
          {reports.map((report) => {
            const img = resolvePhotoUrl(report.photo_url);
            return (
              <article key={report.id} className="report-card">
                <div className="report-card-image">
                  {img ? (
                    <img src={img} alt={report.title} />
                  ) : (
                    <div className="placeholder-img">
                      {report.species === 'cat' ? '🐱' : report.species === 'dog' ? '🐶' : '🐾'}
                    </div>
                  )}
                </div>
                <div className="report-card-body">
                  <div className="report-card-meta">
                    {statusBadge(report.status)}
                    <span className="species-tag">
                      {report.species === 'cat'
                        ? 'Kot'
                        : report.species === 'dog'
                        ? 'Pies'
                        : 'Inne'}
                    </span>
                  </div>
                  <h3>{report.title}</h3>
                  {report.coat_color && (
                    <p className="muted-line">Umaszczenie: {report.coat_color}</p>
                  )}
                  {report.shelter_name && (
                    <p className="shelter-line">Placówka: {report.shelter_name}</p>
                  )}
                  <Link to={`/listing?id=${report.id}`} className="btn btn-outline">
                    Szczegóły i dopasowania AI →
                  </Link>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default HomePage;