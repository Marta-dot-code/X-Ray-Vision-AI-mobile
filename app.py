import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from PIL import Image
import io

app = Flask(__name__)
CORS(app) # Fondamentale per l'accesso da smartphone

# 1. Carichiamo la "memoria" IA (.pkl)
# Assicurati che il nome del file sia identico al tuo
model = joblib.load('identificatore.pkl')

# 2. Carichiamo il database dei metadati
with open('database_strumenti.json', 'r', encoding='utf-8') as f:
    database_metadati = json.load(f)

@app.route('/identify', methods=['POST'])
def identify():
    if 'file' not in request.files:
        return jsonify({"error": "Nessun file inviato"}), 400
    
    file = request.files['file']
    img_bytes = file.read()
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')

    # --- QUI VA LA TUA LOGICA DI PREDIZIONE ---
    # Esempio generico (adattalo al tuo modello):
    # prediction = model.predict(img) 
    # label_identificata = prediction[0]
    
    # Per ora simuliamo che l'IA abbia trovato "reperto_01"
    # Sostituisci questa riga con il risultato reale del tuo modello
    label_identificata = "reperto_01" 

    # 3. Cerchiamo i dati nel database e li inviamo al cellulare
    risultato = database_metadati.get(label_identificata)
    
    if risultato:
        return jsonify(risultato)
    else:
        return jsonify({"error": "Reperto non trovato nel database"}), 404

if __name__ == "__main__":
    # Render assegna una porta dinamica, quindi usiamo os.environ
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)