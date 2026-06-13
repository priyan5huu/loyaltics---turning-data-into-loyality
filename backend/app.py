"""
app.py — Main Flask application for Loyaltics.
Serves the API and the frontend static files.
"""
from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import sys

# Ensure local modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes import api_bp
import routes
from model_loader import ModelLoader

# ── Paths ────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
MODELS_DIR  = os.path.join(PROJECT_DIR, 'models')
FRONTEND_DIR = os.path.join(PROJECT_DIR, 'frontend')

# ── App Setup ────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ── Load ML Model ───────────────────────────────────────
routes.ml = ModelLoader(MODELS_DIR)

# ── Register API Blueprint ──────────────────────────────
app.register_blueprint(api_bp, url_prefix='/api')


# ── Serve Frontend ──────────────────────────────────────
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ── Entry Point ─────────────────────────────────────────
if __name__ == '__main__':
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║          🚀  Loyaltics Backend Server             ║")
    print("╠══════════════════════════════════════════════════╣")
    print("║                                                  ║")
    print("║  Frontend : http://localhost:8000                ║")
    print("║  API Base : http://localhost:8000/api            ║")
    print("║                                                  ║")
    print("║  Endpoints:                                      ║")
    print("║    POST /api/predict      → Run prediction       ║")
    print("║    GET  /api/history      → Prediction history   ║")
    print("║    GET  /api/analytics    → Analytics data       ║")
    print("║    GET  /api/model-metrics→ Model metrics        ║")
    print("║                                                  ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, port=port, host='0.0.0.0')
