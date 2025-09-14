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

# --- FUNÇÃO CORRIGIDA ---
# Restaurada para usar os.walk, que funciona corretamente com sua estrutura de pastas aninhada.
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

        # Usar os.walk para percorrer TODAS as subpastas (incluindo ano/mês/dia)
        for root, _, files in os.walk(band_dir):
            # A condição original e correta: verifica se o diretório atual termina com a região
            if root.endswith(region):
                for f in files:
                    if f.lower().endswith(".jpg"):
                        full_path = Path(root) / f
                        try:
                            file_mtime = datetime.fromtimestamp(full_path.stat().st_mtime, timezone.utc)
                        except FileNotFoundError:
                            continue
                        
                        if file_mtime >= cutoff:
                            name_parts = f.split("_")
                            if len(name_parts) >= 2:
                                timestamp = f"{name_parts[0]}_{name_parts[1]}"
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