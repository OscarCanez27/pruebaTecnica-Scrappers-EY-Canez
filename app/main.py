import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.models import SearchRequest, SearchResponse
from app.scraping import search_entities_scraper

# =====================
# CONFIGURACIÓN JWT
# =====================
SECRET_KEY = "supersecretkey"  # Clave secreta para firmar los tokens JWT
ALGORITHM = "HS256"            # Algoritmo de firma utilizado para el JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Tiempo de expiración del token (en minutos)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Esquema OAuth2 para obtener el token

app = FastAPI()  # Instancia principal de la aplicación FastAPI

# =====================
# Rate limiting (slowapi)
# =====================
limiter = Limiter(key_func=get_remote_address)  # Limita por dirección IP
app.state.limiter = limiter  # Asocia el limitador a la app
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # Maneja errores de límite

# =====================
# USUARIOS VÁLIDOS
# =====================
# Lista de diccionarios preliminar (por ahora hardcodeada) con los usuarios y contraseñas permitidos
valid_users = [
    {"username": "ocanez", "password": "Lucky2018"},
    {"username": "admin", "password": "admin123"},
    {"username": "testuser", "password": "testpass"}
]

def authenticate_user(username: str, password: str):
    """
    Verifica si el usuario y contraseña coinciden con algún usuario válido.
    Devuelve True si es válido, False si no.
    """
    # Recorre la lista de usuarios y compara username y password
    return any(u["username"] == username and u["password"] == password for u in valid_users)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Genera un token JWT firmado con los datos del usuario y una expiración.
    """
    to_encode = data.copy()  # Copia los datos a codificar
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))  # Calcula la expiración
    to_encode.update({"exp": expire})  # Agrega la expiración al payload
    # Crea el token JWT usando la clave secreta y el algoritmo
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decodifica y valida el token JWT recibido en el header Authorization.
    Si es válido, devuelve el username. Si no, lanza un error 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodifica el token usando la clave secreta y el algoritmo
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # Extrae el username del payload
        if username is None:
            raise credentials_exception  # Si no hay username, lanza error
    except jwt.PyJWTError:
        raise credentials_exception  # Si el token es inválido o expiró, lanza error
    return username  # Devuelve el username autenticado

# =====================
# ENDPOINT PARA OBTENER TOKEN JWT
# =====================
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Recibe usuario y contraseña, los valida y genera un token JWT si son correctos.
    Si las credenciales son incorrectas, responde con 401.
    """
    # Valida usuario y contraseña usando la función definida arriba
    if not authenticate_user(form_data.username, form_data.password):
        # Si no es válido, responde con error 401 y mensaje personalizado
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Si es válido, genera el token JWT con el username como 'sub'
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # Devuelve el token y el tipo (bearer)
    return {"access_token": access_token, "token_type": "bearer"}

# =====================
# ENDPOINT PROTEGIDO CON JWT
# =====================
@app.post("/search", response_model=SearchResponse)
@limiter.limit("20/minute")  # Limita a 20 requests por minuto por IP
async def search_entities(
    request: Request,  # Necesario para slowapi (rate limiting)
    search_request: SearchRequest,  # Modelo de entrada con el nombre de la entidad
    current_user: str = Depends(get_current_user)  # Valida el token JWT antes de ejecutar
):
    """
    Endpoint protegido: solo accesible con un token JWT válido.
    Si el token es válido, ejecuta la búsqueda y retorna los resultados.
    Si ocurre un error interno, retorna un mensaje de error 500.
    """
    try:
        # Llama al scrapper principal con el nombre de la entidad
        result = search_entities_scraper(search_request.entity_name)
        return result  # Devuelve los resultados de las tres fuentes
    except Exception as e:
        # Si ocurre un error, responde con un mensaje de error 500
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Error interno en el scrapper: {str(e)}"}
        )

# =====================
# ENDPOINT DE SALUD
# =====================
@app.get("/health")
def health_check():
    """
    Endpoint público para verificar que el servidor está corriendo.
    """
    # Devuelve un estado simple y la fecha/hora actual
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }
