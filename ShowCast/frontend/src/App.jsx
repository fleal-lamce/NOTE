// frontend/src/App.jsx

import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import logoLeft from "./assets/assVisual_LAMCE_COR_SemTextoTransparente.png";
import logoRight from "./assets/BaiaDigital-03.png";
import "./App.css";

// O endereço do seu backend fica fixo aqui
const API_BASE_URL = "http://192.168.248.147:5001";

const BAND_NAMES = {
    Band01: "Blue Visible", Band02: "Red Visible", "Band02-0.5km": "Red Visible – 0.5 km",
    Band03: "Veggie (Near-IR)", Band04: "Cirrus (Near-IR)", Band05: "Snow/Ice (Near-IR)",
    Band06: "Cloud Particle Size (Near-IR)", Band07: "Shortwave IR", Band08: "Upper-Level Water Vapor",
    Band09: "Mid-Level Water Vapor", Band10: "Lower-Level Water Vapor", Band11: "Cloud-Top Phase IR",
    Band12: "Ozone IR", Band13: "Clean Longwave IR", Band14: "IR Longwave Window",
    Band15: "Dirty Longwave IR", Band16: "CO₂ Longwave IR"
};

function App() {
    const [region, setRegion] = useState("Sudeste");
    const [frames, setFrames] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [allBands, setAllBands] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const intervalRef = useRef(null);

    // --- LÓGICA DE ATUALIZAÇÃO AUTOMÁTICA ---

    // 1. A busca de dados foi movida para uma função reutilizável
    const fetchImages = () => {
        // Mostra o "Carregando..." apenas na primeira vez
        if (frames.length === 0) {
            setIsLoading(true);
        }

        axios.get(`${API_BASE_URL}/images`, {
            params: { region, hours: 24 }
        })
        .then(res => {
            setFrames(res.data);
        })
        .catch(err => {
            console.error("Erro ao buscar dados da API:", err);
            // Evita múltiplos alertas em caso de falha contínua
            if (frames.length === 0) {
                alert("Não foi possível carregar os dados do servidor. Verifique o console (F12).");
            }
        })
        .finally(() => {
            setIsLoading(false);
        });
    };
    
    // Este useEffect busca a lista de bandas apenas uma vez
    useEffect(() => {
        axios.get(`${API_BASE_URL}/bands`).then(res => {
            setAllBands(res.data);
        }).catch(err => console.error("Erro ao buscar lista de bandas:", err));
    }, []);

    // 2. Este useEffect agora controla a busca inicial E o timer de atualização
    useEffect(() => {
        fetchImages(); // Busca as imagens imediatamente ao carregar ou mudar de região

        // Configura um timer para buscar os dados a cada 10 minutos (600000 ms)
        const intervalId = setInterval(fetchImages, 600000);

        // 3. Limpa o timer anterior sempre que a região muda, para evitar timers duplicados
        return () => clearInterval(intervalId);

    }, [region]); // A lógica roda novamente sempre que a 'region' é alterada

    // O useEffect da animação permanece exatamente o mesmo
    useEffect(() => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
        }
        if (!isLoading && frames.length > 0) {
            intervalRef.current = setInterval(() => {
                setCurrentIndex(prev => (prev + 1) % frames.length);
            }, 700);
            return () => clearInterval(intervalRef.current);
        }
    }, [isLoading, frames]);

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
                <label htmlFor="region-select">Região:&nbsp;</label>
                <select id="region-select" name="region" value={region} onChange={e => setRegion(e.target.value)}>
                    <option value="Brasil">Brasil</option>
                    <option value="Sudeste">Sudeste</option>
                </select>
            </div>
            {timestamp && !isLoading && (
                <div style={{ textAlign: "center", marginTop: "8px", marginBottom: "4px", fontSize: "1rem", color: "#ccc", fontWeight: "500" }}>
                    Exibindo dados de: {formatTimestamp(timestamp)}
                </div>
            )}
            <div className="grid">
                {isLoading ? (
                    <p style={{ gridColumn: '1 / -1', textAlign: 'center' }}>Carregando imagens...</p>
                ) : (
                    allBands.map((band) => {
                        const productName = BAND_NAMES[band] || band;
                        const url = imagesByBand[band];
                        return (
                            <div key={band} className="card">
                                <div className="card-title">{productName}</div>
                                {url ? (
                                    <img src={`${API_BASE_URL}${url}`} alt={band} className="band-image" />
                                ) : (
                                    <div className="no-image">Sem imagem</div>
                                )}
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
}

function formatTimestamp(ts) {
    if (!ts) return "";
    const match = ts.match(/(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})/);
    if (!match) return ts;
    const [_, year, month, day, hour, minute] = match;
    return `${day}/${month}/${year} às ${hour}:${minute} UTC`;
}

export default App;