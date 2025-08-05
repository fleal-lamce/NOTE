from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
import os
from datetime import datetime, timedelta
from flask import send_file

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
    band = request.args.get("band")
    region = request.args.get("region", "Brasil")
    # número de horas para “lookback”; usa 24 por padrão
    hours = int(request.args.get("hours", "24"))
    if not band:
        return jsonify({"error": "Parâmetro 'band' é obrigatório"}), 400

    band_dir = BASE_DIR / band
    if not band_dir.exists():
        return jsonify({"error": f"Banda '{band}' não encontrada"}), 404

    cutoff = datetime.utcnow() - timedelta(hours=hours)
    images = []
    # percorre recursivamente as pastas <ano>/<mes>/<dia>/<region>
    for root, _, files in os.walk(band_dir):
        if root.endswith(region):
            for f in files:
                if f.lower().endswith(".jpg"):
                    full = Path(root) / f
                    # verifica a data de modificação do arquivo
                    if datetime.fromtimestamp(full.stat().st_mtime) >= cutoff:
                        rel = full.relative_to(BASE_DIR)
                        images.append(f"/static/{rel.as_posix()}")
    # classifica pelo nome (ou timestamp extraído do nome, se houver)
    images.sort()
    return jsonify(images)

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
