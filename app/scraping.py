import requests
from bs4 import BeautifulSoup
from app.models import OffshoreLeaksResult, WorldBankResult, OFACResult
from typing import List

#Offshore Leaks
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

#World Bank
def build_world_bank_address(entry):
    parts = []
    for key in ["SUPP_ADDR", "SUPP_CITY", "SUPP_STATE_CODE", "SUPP_ZIP_CODE"]:
        val = entry.get(key)
        if val:
            parts.append(val)
    return ", ".join(parts)

def matches_world_bank(entry, search_term):
    search_term = search_term.lower()
    fields = [
        entry.get("SUPP_NAME", ""),
        entry.get("SUPP_ADDR", ""),
        entry.get("SUPP_CITY", ""),
        entry.get("SUPP_STATE_CODE", ""),
        entry.get("COUNTRY_NAME", ""),
        entry.get("DEBAR_REASON", "")
    ]
    return any(search_term in (field or "").lower() for field in fields)

def search_world_bank(entity_name: str) -> List[WorldBankResult]:
    url = "https://apigwext.worldbank.org/dvsvc/v1.0/json/APPLICATION/ADOBE_EXPRNCE_MGR/FIRM/SANCTIONED_FIRM"
    headers = {
        "apikey": "z9duUaFUiEUYSHs97CU38fcZO7ipOPvm"
    }
    response = requests.get(url, headers=headers, timeout=30)
    data = response.json()
    results = []
    for entry in data["response"]["ZPROCSUPP"]:
        if matches_world_bank(entry, entity_name):
            results.append(WorldBankResult(
                firm_name=entry.get("SUPP_NAME"),
                address=build_world_bank_address(entry),
                country=entry.get("COUNTRY_NAME"),
                from_date=entry.get("DEBAR_FROM_DATE"),
                to_date=entry.get("DEBAR_TO_DATE"),
                grounds=entry.get("DEBAR_REASON"),
                source="World Bank"
            ))
    return results

#OFAC
def search_ofac(entity_name: str) -> List[OFACResult]:
    url = "https://sanctionssearch.ofac.treas.gov/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    session = requests.Session()

    # 1. GET inicial para obtener los campos ocultos
    response = session.get(url, headers=headers, timeout=30)
    soup = BeautifulSoup(response.text, "html.parser")
    form = soup.find("form", id="aspnetForm")
    hidden_inputs = form.find_all("input", type="hidden")
    form_data = {input.get("name"): input.get("value", "") for input in hidden_inputs}

    # 2. Añadir los campos manualmente con valores por defecto
    form_data["ctl00$MainContent$txtLastName"] = entity_name
    form_data["ctl00$MainContent$ddlType"] = "All"
    form_data["ctl00$MainContent$lstPrograms"] = "All"
    form_data["ctl00$MainContent$Slider1_Boundcontrol"] = "100"
    form_data["ctl00$MainContent$ddlCountry"] = "All"
    form_data["ctl00$MainContent$ddlList"] = "All"
    form_data["ctl00$MainContent$btnSearch"] = "Search"

    # 3. POST con todos los datos
    post_response = session.post(url, data=form_data, headers=headers, timeout=30)
    soup = BeautifulSoup(post_response.text, "html.parser")

    results = []
    # Encuentra el div de resultados
    scroll_div = soup.find("div", id="scrollResults")
    if scroll_div:
        table = scroll_div.find("table", id="gvSearchResults")
        if table:
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 6:
                    name_cell = cells[0]
                    name_link = name_cell.find("a")
                    name = name_link.get_text(strip=True) if name_link else name_cell.get_text(strip=True)
                    address = cells[1].get_text(strip=True)
                    entity_type = cells[2].get_text(strip=True)
                    programs = cells[3].get_text(strip=True)
                    list_name = cells[4].get_text(strip=True)
                    score = cells[5].get_text(strip=True)
                    results.append(OFACResult(
                        name=name,
                        address=address if address else None,
                        entity_type=entity_type if entity_type else None,
                        programs=programs if programs else None,
                        list_name=list_name if list_name else None,
                        score=score if score else None,
                        source="OFAC"
                    ))
    return results

#Scrapper final
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