from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    entity_name: str
    source: str = "all"  # Por defecto busca en todas las fuentes

class EntityResult(BaseModel):
    name: str
    source: str
    details: str

class SearchResponse(BaseModel):
    entity_name: str
    source: str
    total_hits: int
    results: List[EntityResult]