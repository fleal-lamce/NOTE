import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import logoLeft from "./assets/assVisual_LAMCE_COR_SemTextoTransparente.png";
import logoRight from "./assets/BaiaDigital-02.png";
import "./App.css";

function App() {
  const [bands, setBands] = useState([]);
  const [selectedBand, setSelectedBand] = useState("Band13");
  const [region, setRegion] = useState("Sudeste");
  const [images, setImages] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const intervalRef = useRef(null);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/bands").then(res => setBands(res.data));
  }, []);

  // recarrega imagens quando banda ou região mudarem
  useEffect(() => {
    axios.get("http://127.0.0.1:5000/images", {
      params: { band: selectedBand, region, hours: 24 }
    }).then(res => {
      setImages(res.data);
      setCurrentIndex(0);
    });
  }, [selectedBand, region]);

  // animação automática
  useEffect(() => {
    if (images.length > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentIndex(prev => (prev + 1) % images.length);
      }, 700); // 700 ms entre quadros
      return () => clearInterval(intervalRef.current);
    }
  }, [images]);

  return (
    <div className="container">
      <header className="header">
        <img src={logoLeft} className="logo" alt="Logo LAMCE" />
        <h1>GOES‑19 – Monitoramento</h1>
        <img src={logoRight} className="logo" alt="Logo Baía Digital" />
      </header>

      <div className="controls">
        <label>
          Banda:&nbsp;
          <select value={selectedBand} onChange={e => setSelectedBand(e.target.value)}>
            {bands.map(b => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </label>
        <label>
          Região:&nbsp;
          <select value={region} onChange={e => setRegion(e.target.value)}>
            <option value="Brasil">Brasil</option>
            <option value="Sudeste">Sudeste</option>
          </select>
        </label>
      </div>

      <div className="image-container">
        {images.length > 0 && (
          <img
            src={`http://127.0.0.1:5000${images[currentIndex]}`}
            alt={`Imagem ${currentIndex}`}
            className="main-image"
          />
        )}
        {images.length === 0 && <p>Sem imagens nas últimas 24 h.</p>}
      </div>
    </div>
  );
}

export default App;
