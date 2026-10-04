import React, { useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMapEvents } from "react-leaflet";
import CustomMarker from "./custom_marker";
import L from "leaflet";

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

function LocationMarker() {
  const [position, setPosition] = useState<L.LatLng | null>(null);

  const map = useMapEvents({
    click(e) {
      setPosition(e.latlng);
      map.flyTo(e.latlng, map.getZoom());
    },
  });

  if (position === null) return null;

  const { lat, lng } = position;

  return (
    <CustomMarker iscat={true} position={position}>
      <Popup>{lat.toFixed(6)}, {lng.toFixed(6)}</Popup>
    </CustomMarker>
  );
}

export function ClickMap() {
  return (
    <MapContainer className="maximap" center={[50.0614, 19.9366]} zoom={13} scrollWheelZoom={true}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <LocationMarker />
    </MapContainer>
  );
}