import React, { useEffect } from 'react';
import {
  Circle,
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
  useMapEvents,
} from 'react-leaflet';
import L from 'leaflet';
import { Link } from 'react-router-dom';
import { Report } from '../types';
import { resolvePhotoUrl } from '../api';

const createPinIcon = (color: string, badge: string) =>
  L.divIcon({
    className: 'custom-map-pin',
    html: `<div style="
      background:${color};
      color:#fff;
      width:34px;
      height:34px;
      border-radius:50%;
      border:3px solid #fff;
      box-shadow:0 2px 8px rgba(0,0,0,0.35);
      display:flex;
      align-items:center;
      justify-content:center;
      font-weight:700;
      font-size:15px;
    ">${badge}</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  });

const lostIcon = createPinIcon('#dc2626', '!');
const patrolIcon = createPinIcon('#2563eb', 'SM');
const resolvedIcon = createPinIcon('#16a34a', '✓');
const selectedPointIcon = createPinIcon('#7c3aed', '★');

interface MapViewProps {
  reports?: Report[];
  center?: [number, number];
  zoom?: number;
  selectable?: boolean;
  selectedPosition?: [number, number] | null;
  onSelectPosition?: (lat: number, lon: number) => void;
  searchRadiusKm?: number | null;
  height?: string;
}

function ClickHandler({
  onSelect,
}: {
  onSelect?: (lat: number, lon: number) => void;
}) {
  useMapEvents({
    click(e) {
      if (onSelect) {
        onSelect(e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null;
}

function RecenterMap({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center);
  }, [center[0], center[1], map]);
  return null;
}

export const MapView: React.FC<MapViewProps> = ({
  reports = [],
  center = [52.2297, 21.0122],
  zoom = 12,
  selectable = false,
  selectedPosition = null,
  onSelectPosition,
  searchRadiusKm = null,
  height = '440px',
}) => {
  return (
    <div style={{ height, width: '100%', borderRadius: '14px', overflow: 'hidden' }}>
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <RecenterMap center={center} />

        {selectable && <ClickHandler onSelect={onSelectPosition} />}

        {selectedPosition && (
          <Marker position={selectedPosition} icon={selectedPointIcon}>
            <Popup>Wybrana lokalizacja ({selectedPosition[0].toFixed(4)}, {selectedPosition[1].toFixed(4)})</Popup>
          </Marker>
        )}

        {selectedPosition && searchRadiusKm && (
          <Circle
            center={selectedPosition}
            radius={searchRadiusKm * 1000}
            pathOptions={{ color: '#2563eb', fillColor: '#60a5fa', fillOpacity: 0.15 }}
          />
        )}

        {reports.map((report) => {
          const icon =
            report.status === 'resolved'
              ? resolvedIcon
              : report.status === 'found_patrol'
              ? patrolIcon
              : lostIcon;
          const img = resolvePhotoUrl(report.photo_url);

          return (
            <Marker
              key={report.id}
              position={[report.latitude, report.longitude]}
              icon={icon}
            >
              <Popup>
                <div style={{ minWidth: '190px' }}>
                  {img && (
                    <img
                      src={img}
                      alt={report.title}
                      style={{
                        width: '100%',
                        height: '110px',
                        objectFit: 'cover',
                        borderRadius: '8px',
                        marginBottom: '6px',
                      }}
                    />
                  )}
                  <strong style={{ display: 'block', marginBottom: '4px' }}>
                    {report.title}
                  </strong>
                  <div style={{ fontSize: '12px', color: '#475569', marginBottom: '6px' }}>
                    {report.status === 'lost'
                      ? 'Zaginione zwierzę'
                      : report.status === 'found_patrol'
                      ? 'Interwencja Straży Miejskiej'
                      : 'Sprawa rozwiązana'}
                  </div>
                  <Link
                    to={`/listing?id=${report.id}`}
                    style={{ fontSize: '13px', fontWeight: 600, color: '#2563eb' }}
                  >
                    Zobacz szczegóły →
                  </Link>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default MapView;