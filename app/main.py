from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from app.models import SearchRequest

app = FastAPI()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/search")
def search_entities(request: SearchRequest):
    # Por ahora, devolvemos una respuesta simulada
    return {
        "entity_name": request.entity_name,
        "source": request.source,
        "total_hits": 0,
        "results": [],
        "mensaje": "Búsqueda simulada. Aquí irán los resultados reales."
    }

