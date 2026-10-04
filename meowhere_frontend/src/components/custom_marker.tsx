import React from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import CatMarkerUrl from "../assets/cat_marker.svg";
import DogMarkerUrl from "../assets/dog_marker.svg";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";

interface CustomMarkerProps {
  iscat: boolean;
  position: L.LatLngExpression;
  children: React.ReactNode; // Content to display inside the marker
}

const CustomMarker: React.FC<CustomMarkerProps> = ({ iscat, position, children }) => {
  const map = useMap();

  const customIcon = L.icon({
    iconUrl: iscat ? CatMarkerUrl : DogMarkerUrl,
    iconSize: [50, 50],
    iconAnchor: [25, 50],
    popupAnchor: [0, -50],
  });

  return (
    <Marker position={position} icon={customIcon}>
      {children}
    </Marker>
  );
};

export default CustomMarker;