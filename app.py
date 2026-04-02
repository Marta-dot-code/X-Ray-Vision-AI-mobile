import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from PIL import Image
import io

app = Flask(__name__)
# Permettiamo l'accesso da qualsiasi origine (fondamentale per Netlify)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caricamento database e modello
try:
    with open(os.path.join(BASE_DIR, 'database_strumenti.json'), 'r', encoding='utf-8') as f:
        database_metadati = json.load(f)
    model = joblib.load(os.path.join(BASE_DIR, 'identificatore.pkl'))
    print("LOG: Tutto caricato!")
except Exception as e:
    print(f"ERRORE: {e}")

@app.route('/')
def home():
    return "SERVER IA ATTIVO. Prova a visitare /test per verifica."

@app.route('/test')
def test():
    return "La rotta /identify e' pronta a ricevere POST."

@app.route('/identify', methods=['POST'])
def identify():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file"}), 400
        
        file = request.files['file']
        img = Image.open(io.BytesIO(file.read())).convert('RGB')

        # Simulazione (qui andrà la tua logica)
        label_identificata = "reperto_01" 

        risultato = database_metadati.get(label_identificata)
        if risultato:
            return jsonify(risultato)
        return jsonify({"error": "Non trovato nel JSON"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
