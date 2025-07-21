# Due Diligence Scrapper API

API para búsqueda de entidades en múltiples fuentes de riesgo: Offshore Leaks Database (ICIJ), World Bank Debarred Firms y OFAC Sanctions List.

## Requisitos del Sistema

- Python 3.7 o superior
- pip (gestor de paquetes de Python)
- Postman (para probar la API)

## Instrucciones para Despliegue Local

### 1. Extraer el Proyecto y entrar a la carpeta de trabajo del proyecto
```bash
# Extraer el archivo zip
unzip pruebaTecnica-Scrappers-EY-Canez.zip
cd pruebaTecnica-Scrappers-EY-Canez
```

### 2. En la terminal, crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la API
```bash
uvicorn app.main:app --reload
```

La API estará disponible en: `http://localhost:8000`

### 5. Verificar que Funciona
Abre tu navegador en: `http://localhost:8000/health`

Deberías ver:
```json
{
  "status": "ok",
  "timestamp": "2024-01-21T14:29:50.159493"
}
```

### 6. Probar con Postman
1. Abre Postman
2. Importa la colección: `Due_Diligence_Scrapper_API.postman_collection.json`
3. Usa los ejemplos incluidos para probar la API

## Endpoints Disponibles

- `GET /health` - Verificar estado del servicio (público)
- `POST /token` - Obtener token JWT (requiere credenciales)
- `POST /search` - Buscar entidades (requiere token JWT)

## Autenticación JWT

Para acceder al endpoint `/search` necesitas un token JWT.

### Usuarios Válidos
- **Usuario:** ocanez - **Contraseña:** Lucky2018
- **Usuario:** admin - **Contraseña:** admin123
- **Usuario:** testuser - **Contraseña:** testpass

### Cómo Obtener el Token

Haz un POST a `/token` con los datos en formato x-www-form-urlencoded:

```bash
POST http://localhost:8000/token
Content-Type: application/x-www-form-urlencoded

#Usuario de prueba:
username=ocanez&password=Lucky2018
```

Respuesta:
```json
{
  "access_token": "<token>",
  "token_type": "bearer"
}
```

### Cómo Usar el Token

En cada request a `/search`, agrega el header:
```
Authorization: Bearer <token>
```

### Ejemplo de Búsqueda

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"entity_name": "Guangdong"}'
```

## Rate Limiting

- Máximo 20 búsquedas por minuto por dirección IP
- Error 429 si se excede el límite

## Fuentes Consultadas

1. **Offshore Leaks Database (ICIJ)** - Empresas offshore y fundaciones
2. **World Bank Debarred Firms** - Empresas sancionadas por el Banco Mundial
3. **OFAC Sanctions List** - Lista de sanciones del Tesoro de EE.UU.

## Estructura de Respuesta

```json
{
  "entity_name": "Empresa Buscada",
  "total_hits": 5,
  "results_by_source": {
    "offshore_leaks": {
      "hits": 2,
      "results": [...]
    },
    "world_bank": {
      "hits": 1,
      "results": [...]
    },
    "ofac": {
      "hits": 2,
      "results": [...]
    }
  }
}
```

## Solución de Problemas

### La API no inicia
- Verifica que el entorno virtual esté activado
- Verifica que todas las dependencias estén instaladas: `pip list`

### Error 401 en /search
- Verifica que el token JWT sea válido
- Obtén un nuevo token usando el endpoint `/token`