import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Percorso assoluto della cartella corrente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caricamento file con percorsi sicuri
try:
    model_path = os.path.join(BASE_DIR, 'identificatore.pkl')
    db_path = os.path.join(BASE_DIR, 'database_strumenti.json')
    
    model = joblib.load(model_path)
    with open(db_path, 'r', encoding='utf-8') as f:
        database_metadati = json.load(f)
    print("LOG: Caricamento completato con successo!")
except Exception as e:
    print(f"LOG ERRORE: {e}")

@app.route('/')
def home():
    return "<h1>SERVER ATTIVO</h1>La rotta /identify è pronta."

@app.route('/identify', methods=['POST'])
def identify():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Nessun file"}), 400
        
        file = request.files['file']
        img = Image.open(io.BytesIO(file.read())).convert('RGB')

        # Simuliamo la predizione (sostituisci con la tua logica se diversa)
        label_identificata = "reperto_01" 

        risultato = database_metadati.get(label_identificata)
        if risultato:
            return jsonify(risultato)
        return jsonify({"error": "Non trovato"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
