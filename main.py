from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from db.database import Base, engine
from models.user import User  # noqa: F401 – importar para que SQLAlchemy lo registre
from routers import auth, users
from core.hashing import hash_password
from db.database import SessionLocal


# ── Crear tablas ─────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)


# ── Seed: crear admin por defecto si no existe ───────────────────────────────
def _seed_admin():
    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.username == "admin").first()
        if not exists:
            admin = User(
                username="admin",
                email="admin@example.com",
                full_name="Administrador",
                hashed_password=hash_password("admin123"),
                role="admin",
            )
            db.add(admin)
            db.commit()
            print("✅ Usuario admin creado → username: admin | password: admin123")
    finally:
        db.close()


_seed_admin()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API REST para gestión de usuarios con autenticación JWT.\n\n"
        "**Flujo básico:**\n"
        "1. `POST /auth/login` → obtén `access_token` y `refresh_token`\n"
        "2. Envía `Authorization: Bearer <access_token>` en cada request\n"
        "3. `GET /auth/verify` → comprueba si el token sigue siendo válido\n"
        "4. `POST /auth/refresh` → renueva el access_token con el refresh_token\n"
        "5. `POST /auth/logout` → invalida el token actual\n"
    ),
)

# CORS – ajusta los orígenes según tus necesidades
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # En producción pon aquí la URL de tu app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/", tags=["Estado"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Estado"])
def health():
    return {"status": "ok"}
