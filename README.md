# API Usuarios — FastAPI + JWT

API REST para gestión de usuarios con autenticación JWT, lista para conectar con una app Android.

---

## Instalación rápida

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Edita .env y cambia SECRET_KEY por una clave segura

# 4. Iniciar el servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Accede a la documentación interactiva en: **http://localhost:8000/docs**

---

## Endpoints

### Autenticación (`/auth`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| POST | `/auth/login` | Iniciar sesión | ❌ |
| POST | `/auth/logout` | Cerrar sesión | ✅ |
| POST | `/auth/refresh` | Renovar access token | ❌ |
| GET | `/auth/verify` | Verificar si el token es válido | ✅ |
| GET | `/auth/me` | Perfil del usuario autenticado | ✅ |

### Usuarios (`/users`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| GET | `/users` | Listar usuarios | Admin |
| POST | `/users` | Crear usuario | Admin |
| GET | `/users/{id}` | Ver usuario por ID | ✅ |
| PUT | `/users/{id}` | Editar usuario | ✅ |
| DELETE | `/users/{id}` | Eliminar usuario | Admin |

---

## Flujo para app Android

### 1. Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```
**Respuesta:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": { "id": 1, "username": "admin", "role": "admin", ... }
}
```
→ Guarda ambos tokens en **SharedPreferences / EncryptedSharedPreferences**.

---

### 2. Verificar sesión al abrir la app
```http
GET /auth/verify
Authorization: Bearer <access_token>
```
**Respuesta (token válido):**
```json
{ "valid": true, "user": { ... }, "message": "Token válido" }
```
**Respuesta (token expirado → 401):**
```json
{ "detail": "Token inválido o expirado" }
```

---

### 3. Renovar token (cuando expires 401)
```http
POST /auth/refresh
Content-Type: application/json

{ "refresh_token": "eyJ..." }
```
→ Guarda el nuevo `access_token` y reintenta la petición original.

---

### 4. Logout
```http
POST /auth/logout
Authorization: Bearer <access_token>
```
→ El token queda revocado. Borra ambos tokens del dispositivo.

---

## Usuario admin por defecto

Al iniciar por primera vez se crea automáticamente:

| Campo | Valor |
|-------|-------|
| username | `admin` |
| password | `admin123` |
| role | `admin` |

> ⚠️ **Cambia la contraseña en producción.**

---

## Estructura del proyecto

```
api_usuarios/
├── main.py              # Punto de entrada
├── requirements.txt
├── .env.example
├── core/
│   ├── config.py        # Settings (Pydantic)
│   ├── security.py      # JWT: crear, decodificar, revocar
│   ├── hashing.py       # bcrypt
│   └── dependencies.py  # get_current_user, require_admin
├── db/
│   └── database.py      # SQLAlchemy engine + sesión
├── models/
│   └── user.py          # Modelo ORM
├── schemas/
│   └── user.py          # Schemas Pydantic (request/response)
└── routers/
    ├── auth.py          # Login, logout, refresh, verify, me
    └── users.py         # CRUD usuarios
```
