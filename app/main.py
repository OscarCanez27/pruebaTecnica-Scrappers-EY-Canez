from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from app.models import SearchRequest, SearchResponse
from app.scraping import search_entities_scraper

app = FastAPI()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/search", response_model=SearchResponse)
def search_entities(request: SearchRequest):
    # Ahora solo pasamos entity_name
    response_data = search_entities_scraper(request.entity_name)
    
    return SearchResponse(
        entity_name=response_data["entity_name"],
        total_hits=response_data["total_hits"],
        results_by_source=response_data["results_by_source"]
    )

