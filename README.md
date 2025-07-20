# Autenticación JWT (PyJWT)

Para acceder al endpoint `/search` necesito un token JWT.

## Usuarios válidos de ejemplo
- **Usuario:** ocanez
  - **Contraseña:** Lucky2018
- **Usuario:** admin
  - **Contraseña:** admin123
- **Usuario:** testuser
  - **Contraseña:** testpass

## Cómo obtener el token

Puedo obtener el token JWT de dos formas:

### 1. Desde Swagger UI
- Voy a `/docs` (por ejemplo, http://localhost:8000/docs)
- Hago clic en el botón "Authorize" (candado)
- Ingreso el username y password de un usuario válido
- Hago clic en "Authorize" y luego en "Close"
- Ahoro puedo usar los endpoints protegidos directamente desde Swagger

### 2. Desde curl o Postman

Hago un POST a `/token` con los datos en formato x-www-form-urlencoded:

```
POST http://127.0.0.1:8000/token
Content-Type: application/x-www-form-urlencoded

username=ocanez&password=Lucky2018
```

Recibiré una respuesta como:
```
{
  "access_token": "<tu_token>",
  "token_type": "bearer"
}
```

## Cómo usar el token

En cada request a `/search`, agregaré el header:

```
Authorization: Bearer <access_token>
```

Si el token es inválido o falta, recibiré un error 401.

## Ejemplo de uso con curl

```
curl -X POST "http://127.0.0.1:8000/search" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"entity_name": "Guangdong"}'
```

## Notas de seguridad
- Solo los usuarios válidos pueden obtener un token.
- Si intento acceder a un endpoint protegido sin token o con un token inválido, recibiré un error 401.
- Puedo agregar más usuarios en el código, al menos por ahora que están hardcodeados.