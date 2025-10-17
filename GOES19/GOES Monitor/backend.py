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
    "http://192.168.248.147:5173"
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
    """Retorna o frame mais recente de cada banda para a visão geral animada."""
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
                            timestamp_str = f.split('_')[0] + "_" + f.split('_')[1]
                            file_time_utc = datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M').replace(tzinfo=timezone.utc)
                        except (IndexError, ValueError):
                            continue
                        
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

# --- NOVA ROTA PARA A VISÃO DETALHADA ---
@app.route("/band/<string:band_name>/images")
def get_images_for_band(band_name):
    """Retorna TODAS as imagens de uma banda específica nas últimas 24h."""
    region = request.args.get("region", "Brasil")
    hours = int(request.args.get("hours", "24"))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    band_dir = BASE_DIR / band_name
    if not band_dir.exists():
        return jsonify({"error": "Band not found"}), 404

    images_list = []
    for root, _, files in os.walk(band_dir):
        if root.endswith(region):
            for f in files:
                if f.lower().endswith(".jpg"):
                    try:
                        timestamp_str = f.split('_')[0] + "_" + f.split('_')[1]
                        file_time_utc = datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M').replace(tzinfo=timezone.utc)
                    except (IndexError, ValueError):
                        continue
                    
                    if file_time_utc >= cutoff:
                        full_path = Path(root) / f
                        rel = full_path.relative_to(BASE_DIR)
                        images_list.append({
                            "timestamp": timestamp_str,
                            "url": f"/static/{rel.as_posix()}"
                        })

    # Ordena as imagens da mais antiga para a mais recente
    sorted_images = sorted(images_list, key=lambda k: k['timestamp'])
    return jsonify(sorted_images)


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