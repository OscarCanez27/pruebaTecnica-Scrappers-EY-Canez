from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from app.models import SearchRequest, SearchResponse, EntityResult
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
    results = search_entities_scraper(request.entity_name, request.source)
    entity_results = [EntityResult(**r) for r in results]
    return SearchResponse(
        entity_name=request.entity_name,
        source=request.source,
        total_hits=len(entity_results),
        results=entity_results
    )

