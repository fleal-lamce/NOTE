
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
import os
from datetime import datetime

BASE_DIR = Path("E:/GOES-Organized")

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

@app.route("/bands", methods=["GET"])
def get_bands():
    """Retorna a lista de bandas disponíveis (nomes de subpastas)."""
    bands = [f.name for f in BASE_DIR.iterdir() if f.is_dir()]
    return jsonify(sorted(bands))

@app.route("/images", methods=["GET"])
def get_images():
    """
    Retorna a lista de imagens JPEG para uma banda específica, região e data (opcional).
    Exemplo: /images?band=Band13&region=Brasil&date=2025-07-22
    """
    band = request.args.get("band")
    region = request.args.get("region", "Brasil")
    date_str = request.args.get("date")  # formato esperado: YYYY-MM-DD

    if not band:
        return jsonify({"error": "Parâmetro 'band' é obrigatório"}), 400

    band_path = BASE_DIR / band
    if not band_path.exists():
        return jsonify({"error": f"Banda '{band}' não encontrada"}), 404

    image_list = []

    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            path = band_path / f"{date.year:04d}" / f"{date.month:02d}" / f"{date.day:02d}" / region
            if path.exists():
                image_list = sorted([f.name for f in path.glob("*.jpg")])
                image_list = [f"/goes-image/{band}/{date.year:04d}/{date.month:02d}/{date.day:02d}/{region}/{img}" for img in image_list]
        except ValueError:
            return jsonify({"error": "Formato de data inválido, use YYYY-MM-DD"}), 400
    else:
        # Sem data → tenta achar imagens mais recentes automaticamente
        for year in sorted(band_path.glob("*"), reverse=True):
            for month in sorted(year.glob("*"), reverse=True):
                for day in sorted(month.glob("*"), reverse=True):
                    day_path = day / region
                    if day_path.exists():
                        image_list = sorted([f.name for f in day_path.glob("*.jpg")])
                        image_list = [f"/static/{band}/{year.name}/{month.name}/{day.name}/{region}/{img}" for img in image_list]
                        if image_list:
                            break
                if image_list:
                    break
            if image_list:
                break

    return jsonify(image_list)

@app.route("/goes-image/<path:filename>")
def serve_image(filename):
    try:
        full_path = BASE_DIR / filename
        print("🔍 Flask recebeu o path:", filename)
        print("📁 Caminho completo calculado:", full_path)
        print("📂 Existe no disco?", full_path.exists())

        if full_path.exists():
            return send_from_directory(full_path.parent, full_path.name)
        else:
            return f"Arquivo não encontrado em: {full_path}", 404
    except Exception as e:
        return f"Erro ao servir imagem: {e}", 500

app.config["JSON_SORT_KEYS"] = False
app.config["JSON_AS_ASCII"] = False

if __name__ == "__main__":
    app.run(debug=True)
