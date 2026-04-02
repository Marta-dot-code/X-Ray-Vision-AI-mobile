import os
import pickle
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer, util
from PIL import Image

app = FastAPI()

# Permettiamo la comunicazione con Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Percorso sicuro per i file su Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PKL_PATH = os.path.join(BASE_DIR, 'database_museo.pkl')

# 1. Carichiamo CLIP e il Database .pkl
print("LOG: Caricamento CLIP (clip-ViT-B-32)...")
model = SentenceTransformer('clip-ViT-B-32')

try:
    with open(PKL_PATH, 'rb') as f:
        data = pickle.load(f)
        db_embeddings = data['embeddings']
        metadati_db = data['metadati']
    print("LOG: Memoria .pkl caricata con successo!")
except Exception as e:
    print(f"LOG ERRORE: Impossibile caricare .pkl: {e}")

@app.get("/")
def home():
    return {"status": "online", "message": "Server IA del Museo pronto"}

@app.post("/identify")
async def identify_artifact(file: UploadFile = File(...)):
    try:
        # 2. Leggiamo l'immagine
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # 3. Trasformiamo la foto in un vettore
        query_embedding = model.encode(image)
        
        # 4. Confronto con il database
        best_match_id = None
        highest_score = -1
        
        for item in db_embeddings:
            score = util.cos_sim(query_embedding, item['vettore']).item()
            if score > highest_score:
                highest_score = score
                best_match_id = item['reperto_id']
        
        # SOGLIA DI SICUREZZA
        if highest_score < 0.6:
            return {"error": "Reperto non riconosciuto", "score": highest_score}

        # 5. Restituiamo i metadati contenuti nel PKL
        result = metadati_db[best_match_id]
        result['id'] = best_match_id
        result['score'] = highest_score
        
        print(f"LOG: Trovato {best_match_id} (Score: {highest_score:.2f})")
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
