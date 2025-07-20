import requests
from bs4 import BeautifulSoup
from app.models import OffshoreLeaksResult, WorldBankResult, OFACResult
from typing import List

def search_offshore_leaks(entity_name: str) -> List[OffshoreLeaksResult]:
    search_url = "https://offshoreleaks.icij.org/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    all_results = []
    params = {
        "q": entity_name,
        "c": "",
        "j": "",
        "d": ""
    }
    response = requests.get(search_url, params=params, headers=headers, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Procesar primera página
    all_results.extend(process_offshore_results_page(soup))
    
    # Seguir "More results" hasta que no haya más
    max_iter = 20  # Protección extra ante bucles infinitos
    iter_count = 0
    while True:
        more_results_link = soup.find("a", attrs={"data-more-results": True})
        if not more_results_link or "href" not in more_results_link.attrs:
            break
        
        more_url = "https://offshoreleaks.icij.org" + more_results_link["href"]
        more_response = requests.get(more_url, headers=headers, timeout=20)
        soup = BeautifulSoup(more_response.text, "html.parser")
        
        page_results = process_offshore_results_page(soup)
        if not page_results:
            break  # No hay más resultados, terminamos
        all_results.extend(page_results)

        iter_count += 1
        if iter_count > max_iter:
            print("¡Demasiadas páginas! Rompiendo el bucle por seguridad.")
            break

    return [OffshoreLeaksResult(**result) for result in all_results]

def process_offshore_results_page(soup: BeautifulSoup) -> List[dict]:
    """
    Procesa una página de resultados de Offshore Leaks y devuelve lista de diccionarios.
    """
    results = []
    tbody = soup.find("tbody")
    if tbody:
        for row in tbody.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 1:
                entity_cell = cells[0]
                entity_link = entity_cell.find("a")
                entity_text = entity_link.get_text(strip=True) if entity_link else entity_cell.get_text(strip=True)
                if entity_text and entity_text.strip():
                    jurisdiction = cells[1].get_text(strip=True) if len(cells) > 1 and cells[1].get_text(strip=True) != "" else None
                    linked_to = cells[2].get_text(strip=True) if len(cells) > 2 and cells[2].get_text(strip=True) != "" else None
                    data_from = cells[3].get_text(strip=True) if len(cells) > 3 and cells[3].get_text(strip=True) != "" else None

                    results.append({
                        "entity": entity_text,
                        "jurisdiction": jurisdiction,
                        "linked_to": linked_to,
                        "data_from": data_from,
                        "source": "Offshore Leaks"
                    })
    return results

def search_world_bank(entity_name: str) -> List[WorldBankResult]:
    # TODO: Implementar scraping de World Bank
    return []

def search_ofac(entity_name: str) -> List[OFACResult]:
    # TODO: Implementar scraping de OFAC
    return []

def search_entities_scraper(entity_name: str):
    # Buscar en las 3 fuentes
    offshore_results = search_offshore_leaks(entity_name)
    world_bank_results = search_world_bank(entity_name)
    ofac_results = search_ofac(entity_name)
    
    # Construir respuesta separada por fuente
    response = {
        "entity_name": entity_name,
        "total_hits": len(offshore_results) + len(world_bank_results) + len(ofac_results),
        "results_by_source": {
            "offshore_leaks": {
                "hits": len(offshore_results),
                "results": offshore_results
            },
            "world_bank": {
                "hits": len(world_bank_results),
                "results": world_bank_results
            },
            "ofac": {
                "hits": len(ofac_results),
                "results": ofac_results
            }
        }
    }
    
    return response