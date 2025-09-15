# backend/app.py

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from pathlib import Path
from collections import defaultdict
import os
from datetime import datetime, timedelta, timezone

BASE_DIR = Path("Y:/GOES-Organized")

app = Flask(__name__, static_folder=None)

CORS(app, origins=[
    "http://localhost:5173",
    "http://192.168.248.147:5173" # Adicione aqui outros IPs/domínios se necessário
])

@app.route("/bands", methods=["GET"])
def get_bands():
    """Retorna a lista de todas as bandas disponíveis, que servirá de molde para o grid."""
    bands = [f.name for f in BASE_DIR.iterdir() if f.is_dir()]
    try:
        sorted_bands = sorted(bands, key=lambda b: int(b.replace("Band", "").split('-')[0]))
    except ValueError:
        sorted_bands = sorted(bands)
    return jsonify(sorted_bands)

@app.route("/images")
def get_images():
    region = request.args.get("region", "Brasil")
    hours = int(request.args.get("hours", "24"))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    frames_map = defaultdict(dict)
    
    bands = [f.name for f in BASE_DIR.iterdir() if f.is_dir()]
    for band in bands:
        band_dir = BASE_DIR / band
        if not band_dir.exists():
            continue

        for root, _, files in os.walk(band_dir):
            if root.endswith(region):
                for f in files:
                    if f.lower().endswith(".jpg"):
                        try:
                            # --- NOVA LÓGICA AQUI ---
                            # 1. Extrai a data e hora do nome do arquivo (ex: "2025-09-15_12-10_...")
                            timestamp_str = f.split('_')[0] + "_" + f.split('_')[1]
                            # 2. Converte a string para um objeto datetime ciente do fuso horário UTC
                            file_time_utc = datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M').replace(tzinfo=timezone.utc)
                        except (IndexError, ValueError):
                            # Se o nome do arquivo não tiver o formato esperado, ignora este arquivo
                            continue
                        
                        # 3. Compara o tempo do arquivo com o limite de 24 horas
                        if file_time_utc >= cutoff:
                            full_path = Path(root) / f
                            timestamp = f"{f.split('_')[0]}_{f.split('_')[1]}"
                            rel = full_path.relative_to(BASE_DIR)
                            frames_map[timestamp][band] = f"/static/{rel.as_posix()}"

    result = []
    for ts in sorted(frames_map):
        result.append({
            "timestamp": ts,
            "images": frames_map[ts]
        })

    return jsonify(result)

@app.route("/static/<path:filename>")
def serve_static(filename):
    full_path = BASE_DIR.joinpath(filename)
    try:
        resolved_path = full_path.resolve(strict=True)
        if not resolved_path.is_relative_to(BASE_DIR.resolve(strict=True)):
                return "Acesso negado.", 403
    except FileNotFoundError:
        return f"Arquivo não encontrado: {full_path}", 404
    return send_file(resolved_path, mimetype='image/jpeg')


app.config["JSON_SORT_KEYS"] = False
app.config["JSON_AS_ASCII"] = False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)