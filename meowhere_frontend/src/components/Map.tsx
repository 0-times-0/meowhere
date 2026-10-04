import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import CustomMarker from "./custom_marker";

export function MiniMap({cat=true, latitude=50.067394, longtitude=19.914549}) {
  return (
    <MapContainer className="minimap" center={[latitude, longtitude]} zoom={12} scrollWheelZoom={false} dragging={false}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <CustomMarker iscat={cat} position={[latitude, longtitude]}>
        <Popup>
          {latitude} {longtitude}
        </Popup>
      </CustomMarker>
    </MapContainer>
  );
}

export function MaxiMap({cat=true, latitude=50.067394, longtitude=19.914549}) {
  return (
    <MapContainer className="maximap" center={[latitude, longtitude]} zoom={17} scrollWheelZoom={true}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <CustomMarker iscat={cat} position={[latitude, longtitude]}>
        <Popup>
          {latitude} {longtitude}
        </Popup>
      </CustomMarker>
    </MapContainer>
  );
}

/*export function ClickMap({latitude=50.067394, longtitude=19.914549}) {
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
}*/