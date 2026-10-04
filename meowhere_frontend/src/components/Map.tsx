import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";

export function MiniMap({latitude=50.067394, longtitude=19.914549}) {
  return (
    <MapContainer className="minimap" center={[latitude, longtitude]} zoom={12} scrollWheelZoom={false}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={[latitude, longtitude]}>
        <Popup>
          {latitude} {longtitude}
        </Popup>
      </Marker>
    </MapContainer>
  );
}

export function MaxiMap({latitude=50.067394, longtitude=19.914549}) {
  return (
    <MapContainer className="maximap" center={[latitude, longtitude]} zoom={17} scrollWheelZoom={true}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Marker position={[latitude, longtitude]}>
        <Popup>
          {latitude} {longtitude}
        </Popup>
      </Marker>
    </MapContainer>
  );
}