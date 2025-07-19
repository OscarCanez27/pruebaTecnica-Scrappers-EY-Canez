import requests
from bs4 import BeautifulSoup

def search_entities_scraper(entity_name: str, source: str = "all"):
    # Usaremos Wikipedia como ejemplo de scraping real
    url = f"https://es.wikipedia.org/wiki/{entity_name.replace(' ', '_')}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # Extraer el primer párrafo de la página
        p = soup.find("p")
        resumen = p.get_text(strip=True) if p else "Sin resumen disponible"
        return [{
            "name": entity_name,
            "source": "Wikipedia",
            "details": resumen
        }]
    else:
        return []
