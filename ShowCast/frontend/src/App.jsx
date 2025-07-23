import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [bands, setBands] = useState([]);
  const [images, setImages] = useState([]);
  const [selectedBand, setSelectedBand] = useState("Band13");
  const [region, setRegion] = useState("Sudeste");

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/bands").then(res => setBands(res.data));
  }, []);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/images", {
        params: { band: selectedBand, region }
      })
      .then(res => {
        console.log("🔎 Imagens recebidas:", res.data);
        setImages(res.data);
      });
  }, [selectedBand, region]);

  return (
    <div style={{ fontFamily: "Arial", padding: 20 }}>
      <h1>SHOWCast - GOES-19</h1>

      <div style={{ display: "flex", gap: 20 }}>
        <div>
          <h2>Bandas</h2>
          <ul>
            {bands.map((b) => (
              <li key={b}>
                <button
                  onClick={() => setSelectedBand(b)}
                  style={{ fontWeight: b === selectedBand ? "bold" : "normal" }}
                >
                  {b}
                </button>
              </li>
            ))}
          </ul>

          <h2>Região</h2>
          <select value={region} onChange={e => setRegion(e.target.value)}>
            <option value="Brasil">Brasil</option>
            <option value="Sudeste">Sudeste</option>
          </select>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
          {images.map((img, i) => {
            const url = `http://127.0.0.1:5000${img.replace("/static", "/goes-image")}`;
            return (
              <a key={i} href={url} target="_blank" rel="noreferrer">
                <img src={url} alt={`frame ${i}`} width="200" />
              </a>
          );
})}
        </div>
      </div>
    </div>
  );
}

export default App;
