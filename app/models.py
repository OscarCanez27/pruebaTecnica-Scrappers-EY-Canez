from pydantic import BaseModel
from typing import List, Optional

class SearchRequest(BaseModel):
    entity_name: str

#Para los resultados de las fuentes: Algunos campos sonopcionales pues algunos resultados en la fuente no cuentan con todos los campos.

# Modelo para Offshore Leaks
class OffshoreLeaksResult(BaseModel):
    entity: str
    jurisdiction: Optional[str] = None 
    linked_to: Optional[str] = None
    data_from: Optional[str] = None
    source: str = "Offshore Leaks"

# Modelo para World Bank
class WorldBankResult(BaseModel):
    firm_name: str
    address: Optional[str] = None
    country: Optional[str] = None
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    grounds: Optional[str] = None
    source: str = "World Bank"

# Modelo para OFAC
class OFACResult(BaseModel):
    name: str
    address: Optional[str] = None
    entity_type: Optional[str] = None
    programs: Optional[str] = None
    list_name: Optional[str] = None
    score: Optional[str] = None
    source: str = "OFAC"

# Estructura de respuesta que separa por fuente
class SearchResponse(BaseModel):
    entity_name: str
    total_hits: int
    results_by_source: dict = {
        "offshore_leaks": {
            "hits": 0,
            "results": []
        },
        "world_bank": {
            "hits": 0,
            "results": []
        },
        "ofac": {
            "hits": 0,
            "results": []
        }
    }