import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import logoLeft from "./assets/assVisual_LAMCE_COR_SemTextoTransparente.png";
import logoRight from "./assets/BaiaDigital-03.png";
import "./App.css";

const BAND_NAMES = {
  Band01: "Blue Visible",
  Band02: "Red Visible",
  "Band02-0.5km": "Red Visible – 0.5 km",
  Band03: "Veggie (Near-IR)",
  Band04: "Cirrus (Near-IR)",
  Band05: "Snow/Ice (Near-IR)",
  Band06: "Cloud Particle Size (Near-IR)",
  Band07: "Shortwave IR",
  Band08: "Upper-Level Water Vapor",
  Band09: "Mid-Level Water Vapor",
  Band10: "Lower-Level Water Vapor",
  Band11: "Cloud-Top Phase IR",
  Band12: "Ozone IR",
  Band13: "Clean Longwave IR",
  Band14: "IR Longwave Window",
  Band15: "Dirty Longwave IR",
  Band16: "CO₂ Longwave IR"
};

function App() {
  const [region, setRegion] = useState("Sudeste");
  const [frames, setFrames] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const intervalRef = useRef(null);

  // Carrega frames sincronizados ao trocar a região
  useEffect(() => {
    axios.get("http://127.0.0.1:5000/images", {
      params: { region, hours: 24 }
    }).then(res => {
      setFrames(res.data);
      setCurrentIndex(0);
    });
  }, [region]);

  // Animação sincronizada por frame
  useEffect(() => {
    if (frames.length > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentIndex(prev => (prev + 1) % frames.length);
      }, 700);
      return () => clearInterval(intervalRef.current);
    }
  }, [frames]);

  const currentFrame = frames[currentIndex] || {};
  const imagesByBand = currentFrame.images || {};
  const timestamp = currentFrame.timestamp || "";

  return (
    <div className="container">
      <header className="header">
        <img src={logoLeft} className="logo" alt="Logo LAMCE" />
        <h1 className="title">GOES‑19 – Monitoramento</h1>
        <img src={logoRight} className="logo" alt="Logo Baía Digital" />
      </header>

      <div className="controls">
        <label>
          Região:&nbsp;
          <select value={region} onChange={e => setRegion(e.target.value)}>
            <option value="Brasil">Brasil</option>
            <option value="Sudeste">Sudeste</option>
          </select>
        </label>
      </div>

      {/* Mostra o horário atual da imagem exibida */}
      {timestamp && (
        <div style={{
          textAlign: "center",
          marginTop: "8px",
          marginBottom: "4px",
          fontSize: "1rem",
          color: "#ccc",
          fontWeight: "500"
        }}>
          Exibindo dados de: {formatTimestamp(timestamp)}
        </div>
      )}

      <div className="grid">
        {Object.entries(imagesByBand).map(([band, url]) => {
          const productName = BAND_NAMES[band] || band;
          return (
            <div key={band} className="card">
              <div className="card-title">{productName}</div>
              {url ? (
                <img src={`http://127.0.0.1:5000${url}`} alt={band} className="band-image" />
              ) : (
                <div className="no-image">Sem imagens</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Formata o timestamp "YYYY-MM-DD_HH-MM" para "DD/MM/YYYY às HH:MM UTC"
function formatTimestamp(ts) {
  const match = ts.match(/(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})/);
  if (!match) return ts;
  const [_, year, month, day, hour, minute] = match;
  return `${day}/${month}/${year} às ${hour}:${minute} UTC`;
}

export default App;
