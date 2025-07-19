def search_entities_scraper(entity_name: str, source: str = "all"):
    # Aquí irá la lógica real de scraping
    # Por ahora, devolvemos resultados simulados
    if entity_name.lower() == "john doe":
        return [
            {
                "name": "John Doe",
                "source": source,
                "details": "Entidad simulada para pruebas"
            }
        ]
    return []

