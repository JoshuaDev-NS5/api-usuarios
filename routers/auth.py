from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from db.database import get_db
from models.user import User
from schemas.user import LoginRequest, TokenResponse, RefreshRequest, RefreshResponse, VerifyResponse, UserPublic
from core.hashing import verify_password
from core.security import create_access_token, create_refresh_token, decode_token, revoke_token, is_token_revoked
from core.config import settings
from core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticacion"])
bearer_scheme = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="La cuenta esta desactivada")
    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        refresh_token=create_refresh_token({"sub": str(user.id)}),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserPublic.model_validate(user),
    )


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: User = Depends(get_current_user),
):
    revoke_token(credentials.credentials)
    return {"message": f"Sesion cerrada. Hasta pronto, {current_user.username}!"}


@router.post("/refresh", response_model=RefreshResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    exc = HTTPException(status_code=401, detail="Refresh token invalido o expirado")
    if is_token_revoked(body.refresh_token):
        raise exc
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise exc
        user_id = payload.get("sub")
    except JWTError:
        raise exc
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise exc
    return RefreshResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/verify", response_model=VerifyResponse)
def verify_token(current_user: User = Depends(get_current_user)):
    return VerifyResponse(valid=True, user=UserPublic.model_validate(current_user), message="Token valido")


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)):
    return UserPublic.model_validate(current_user)
