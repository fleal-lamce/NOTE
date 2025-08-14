from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from pathlib import Path
from collections import defaultdict
import os
from datetime import datetime, timedelta, timezone

BASE_DIR = Path("E:/GOES-Organized")

app = Flask(__name__, static_folder=None)
CORS(app, origins=["http://localhost:5173"])

@app.route("/bands", methods=["GET"])
def get_bands():
    """Retorna a lista de bandas disponíveis (nomes de subpastas)."""
    bands = [f.name for f in BASE_DIR.iterdir() if f.is_dir()]
    return jsonify(sorted(bands))

@app.route("/images")
def get_images():
    region = request.args.get("region", "Brasil")
    hours = int(request.args.get("hours", "24"))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    # {timestamp: {band: path}}
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
                        full = Path(root) / f
                        if datetime.fromtimestamp(full.stat().st_mtime, timezone.utc) >= cutoff:
                            # Extrai timestamp no formato "YYYY-MM-DD_HH-MM"
                            name_parts = f.split("_")
                            if len(name_parts) >= 2:
                                timestamp = f"{name_parts[0]}_{name_parts[1]}"
                                rel = full.relative_to(BASE_DIR)
                                frames_map[timestamp][band] = f"/static/{rel.as_posix()}"

    # Filtra apenas os timestamps que têm imagens em pelo menos 12 bandas (ajuste conforme desejar)
    result = []
    for ts in sorted(frames_map):
        if len(frames_map[ts]) >= 12:
            result.append({
                "timestamp": ts,
                "images": frames_map[ts]
            })

    return jsonify(result)

@app.route("/static/<path:filename>")
def serve_static(filename):
    full_path = BASE_DIR / filename
    print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
    print(f"[DEBUG] filename: {filename}")
    print(f"[DEBUG] Caminho final: {full_path}")
    if not full_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {full_path}")
        return f"Arquivo não encontrado: {full_path}", 404
    return send_file(full_path)

app.config["JSON_SORT_KEYS"] = False
app.config["JSON_AS_ASCII"] = False

if __name__ == "__main__":
    app.run(debug=True)
