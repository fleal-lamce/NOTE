// frontend/src/App.jsx

import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import logoLeft from "./assets/assVisual_LAMCE_COR_SemTextoTransparente.png";
import logoRight from "./assets/BaiaDigital-03.png";
import "./App.css";

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
    const [allBands, setAllBands] = useState([]);
    
    const [selectedBand, setSelectedBand] = useState(null);
    const [lightboxImage, setLightboxImage] = useState(null);

    useEffect(() => {
        axios.get(`${API_BASE_URL}/bands`).then(res => {
            setAllBands(res.data);
        }).catch(err => console.error("Erro ao buscar lista de bandas:", err));
    }, []);

    const handleBackToMain = () => {
        setSelectedBand(null);
    };

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

            {!selectedBand ? (
                <MainGridView allBands={allBands} region={region} onBandClick={setSelectedBand} />
            ) : (
                <BandDetailView 
                    bandName={selectedBand} 
                    region={region} 
                    onImageClick={setLightboxImage}
                    onBack={handleBackToMain}
                />
            )}

            {lightboxImage && (
                <Lightbox imageUrl={lightboxImage} onClose={() => setLightboxImage(null)} />
            )}
        </div>
    );
}

function MainGridView({ allBands, region, onBandClick }) {
    const [frames, setFrames] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const animationIntervalRef = useRef(null);

    useEffect(() => {
        const fetchMainImages = () => {
            setIsLoading(true);
            axios.get(`${API_BASE_URL}/images`, { params: { region, hours: 24 } })
                .then(res => setFrames(res.data))
                .catch(err => console.error("Erro ao buscar imagens principais:", err))
                .finally(() => setIsLoading(false));
        };
        fetchMainImages();
        const intervalId = setInterval(fetchMainImages, 600000);
        return () => clearInterval(intervalId);
    }, [region]);

    useEffect(() => {
        clearInterval(animationIntervalRef.current);
        if (!isLoading && frames.length > 0) {
            animationIntervalRef.current = setInterval(() => {
                setCurrentIndex(prev => (prev + 1) % frames.length);
            }, 700);
        }
        return () => clearInterval(animationIntervalRef.current);
    }, [isLoading, frames]);

    const currentFrame = frames[currentIndex] || {};
    const imagesByBand = currentFrame.images || {};
    const timestamp = currentFrame.timestamp || "";

    return (
        <>
            {timestamp && !isLoading && (
                <div className="timestamp-display">
                    Exibindo dados de: {formatTimestamp(timestamp)}
                </div>
            )}
            <div className="grid">
                {isLoading ? (
                    <p className="loading-text">Carregando imagens...</p>
                ) : (
                    allBands.map((band) => {
                        const url = imagesByBand[band];
                        return (
                            <div key={band} className="card" onClick={() => onBandClick(band)}>
                                <div className="card-title">{BAND_NAMES[band] || band}</div>
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
        </>
    );
}

function BandDetailView({ bandName, region, onImageClick, onBack }) {
    const [bandImages, setBandImages] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        setIsLoading(true);
        axios.get(`${API_BASE_URL}/band/${bandName}/images`, { params: { region, hours: 24 } })
            .then(res => setBandImages(res.data))
            .catch(err => console.error(`Erro ao buscar imagens para a banda ${bandName}:`, err))
            .finally(() => setIsLoading(false));
    }, [bandName, region]);

    return (
        <>
            <div className="detail-header">
                <button onClick={onBack} className="back-button">← Voltar</button>
                <h2 className="detail-title">{BAND_NAMES[bandName] || bandName} - Últimas 24h</h2>
            </div>
            <div className="grid static-grid">
                {isLoading ? (
                    <p className="loading-text">Carregando imagens da banda...</p>
                ) : bandImages.length > 0 ? (
                    bandImages.map(({ timestamp, url }) => (
                        <div key={url} className="card" onClick={() => onImageClick(`${API_BASE_URL}${url}`)}>
                            <div className="card-title">{formatTimestamp(timestamp)}</div>
                            <img src={`${API_BASE_URL}${url}`} alt={timestamp} className="band-image" />
                        </div>
                    ))
                ) : (
                    <p className="loading-text">Nenhuma imagem encontrada para esta banda nas últimas 24 horas.</p>
                )}
            </div>
        </>
    );
}

// --- COMPONENTE LIGHTBOX CORRIGIDO ---
function Lightbox({ imageUrl, onClose }) {
    return (
        <div className="lightbox-overlay" onClick={onClose}>
            {/* O botão agora é irmão do conteúdo, não filho, para facilitar o posicionamento */}
            <button onClick={onClose} className="lightbox-close-button">×</button>
            <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
                <img src={imageUrl} alt="Imagem em tela cheia" className="lightbox-image" />
            </div>
        </div>
    );
}

function formatTimestamp(ts) {
    if (!ts) return "";
    const [date, time] = ts.split('_');
    const [year, month, day] = date.split('-');
    const [hour, minute] = time.split('-');
    return `${day}/${month}/${year} ${hour}:${minute} UTC`;
}

export default App;