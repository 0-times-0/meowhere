import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import {
  deleteReportById,
  fetchReportById,
  fetchReportMatches,
  getStoredSession,
  resolvePhotoUrl,
  resolveReportById,
} from '../api';
import MapView from '../components/MapView';
import type { Report, ReportMatch } from '../types';

export const ReportDetailsPage: React.FC = () => {
  const { id: paramId } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const rawId = paramId || searchParams.get('id');
  const reportId = rawId ? Number(rawId) : NaN;

  const [report, setReport] = useState<Report | null>(null);
  const [matches, setMatches] = useState<ReportMatch[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const session = getStoredSession();

  useEffect(() => {
    if (!Number.isFinite(reportId)) {
      setError('Brak poprawnego identyfikatora zgłoszenia.');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    Promise.all([fetchReportById(reportId), fetchReportMatches(reportId).catch(() => [])])
      .then(([rep, matched]) => {
        setReport(rep);
        setMatches(matched);
      })
      .catch((err: any) => setError(err.message || 'Nie znaleziono zgłoszenia.'))
      .finally(() => setLoading(false));
  }, [reportId]);

  if (loading) {
    return <div className="page-container">Ładowanie szczegółów zgłoszenia...</div>;
  }

  if (error || !report) {
    return (
      <div className="page-container">
        <div className="alert alert-error">{error || 'Zgłoszenie nie istnieje.'}</div>
        <Link to="/" className="btn btn-outline">
          ← Wróć do mapy
        </Link>
      </div>
    );
  }

  const isOwner =
    (session?.role === 'resident' && report.user_id === session.user_id) ||
    (session?.role === 'municipal' && report.municipal_user_id === session.user_id);
  const canResolve = isOwner || session?.role === 'municipal';

  const handleResolve = async () => {
    try {
      const updated = await resolveReportById(report.id);
      setReport(updated);
    } catch (err: any) {
      alert(err.message || 'Nie udało się zmienić statusu.');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Czy na pewno chcesz usunąć to zgłoszenie?')) return;
    try {
      await deleteReportById(report.id);
      navigate('/');
    } catch (err: any) {
      alert(err.message || 'Nie udało się usunąć zgłoszenia.');
    }
  };

  const photo = resolvePhotoUrl(report.photo_url);

  return (
    <div className="page-container">
      <div style={{ marginBottom: '14px' }}>
        <Link to="/" className="btn btn-outline">
          ← Wróć do mapy zgłoszeń
        </Link>
      </div>

      <div className="details-layout">
        <div className="details-card">
          {photo && (
            <img
              src={photo}
              alt={report.title}
              style={{
                width: '100%',
                maxHeight: '380px',
                objectFit: 'cover',
                borderRadius: '12px',
                marginBottom: '16px',
              }}
            />
          )}

          <div className="report-card-meta">
            <span
              className={`badge ${
                report.status === 'lost'
                  ? 'badge-lost'
                  : report.status === 'found_patrol'
                  ? 'badge-patrol'
                  : 'badge-resolved'
              }`}
            >
              {report.status === 'lost'
                ? 'Zaginione'
                : report.status === 'found_patrol'
                ? 'Odłowione przez Straż Miejską'
                : 'Rozwiązane'}
            </span>
            <span className="species-tag">
              Gatunek:{' '}
              {report.species === 'cat'
                ? 'Kot'
                : report.species === 'dog'
                ? 'Pies'
                : 'Inne'}
            </span>
          </div>

          <h1>{report.title}</h1>
          {report.description && <p style={{ lineHeight: 1.6 }}>{report.description}</p>}

          <div className="details-specs">
            {report.coat_color && (
              <div>
                <strong>Umaszczenie:</strong> {report.coat_color}
              </div>
            )}
            {report.breed && (
              <div>
                <strong>Rasa / typ:</strong> {report.breed}
              </div>
            )}
            {report.sex && (
              <div>
                <strong>Płeć:</strong>{' '}
                {report.sex === 'male'
                  ? 'Samiec'
                  : report.sex === 'female'
                  ? 'Samica'
                  : 'Nieznana'}
              </div>
            )}
            {report.shelter_name && (
              <div>
                <strong>Schronisko / placówka:</strong> {report.shelter_name}
              </div>
            )}
            {report.contact_phone && (
              <div>
                <strong>Telefon kontaktowy:</strong> {report.contact_phone}
              </div>
            )}
          </div>

          <div className="details-actions">
            {canResolve && report.status !== 'resolved' && (
              <button onClick={handleResolve} className="btn btn-primary">
                ✓ Oznacz jako rozwiązane
              </button>
            )}
            {isOwner && (
              <button onClick={handleDelete} className="btn btn-danger">
                Usuń zgłoszenie
              </button>
            )}
          </div>
        </div>

        <div className="details-side">
          <MapView
            reports={[report]}
            center={[report.latitude, report.longitude]}
            zoom={14}
            height="300px"
          />

          <div className="matches-card">
            <h3>🤖 Sugerowane dopasowania AI ({matches.length})</h3>
            {matches.length === 0 ? (
              <p className="muted-line">
                Brak pasujących zgłoszeń przeciwnego typu w bazie.
              </p>
            ) : (
              matches.map((m) => (
                <div key={m.report_id} className="match-item">
                  <div className="match-header">
                    <strong>{m.title}</strong>
                    <span className="match-score">
                      {Math.round(m.similarity_score * 100)}% zgodności
                    </span>
                  </div>
                  <p className="muted-line">{m.reasons.join(' • ')}</p>
                  <Link to={`/listing?id=${m.report_id}`} className="btn btn-outline">
                    Porównaj zgłoszenie →
                  </Link>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportDetailsPage;