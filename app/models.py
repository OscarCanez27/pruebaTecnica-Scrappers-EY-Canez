from pydantic import BaseModel

class SearchRequest(BaseModel):
    entity_name: str
    source: str = "all"  # Por defecto busca en todas las fuentes