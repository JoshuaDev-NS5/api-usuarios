from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserPublic, UserListResponse
from core.hashing import hash_password
from core.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("", response_model=UserListResponse)
def list_users(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100),
               db: Session = Depends(get_db), _: User = Depends(require_admin)):
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    return UserListResponse(total=total, users=[UserPublic.model_validate(u) for u in users])


@router.post("", response_model=UserPublic, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="El username ya esta en uso")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="El email ya esta registrado")
    user = User(username=body.username, email=body.email, full_name=body.full_name,
                hashed_password=hash_password(body.password), role=body.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)


@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserPublic.model_validate(user)


@router.put("/{user_id}", response_model=UserPublic)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No puedes editar este usuario")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    data = body.model_dump(exclude_unset=True)
    if current_user.role != "admin":
        data.pop("role", None)
        data.pop("is_active", None)
    if "password" in data:
        user.hashed_password = hash_password(data.pop("password"))
    if "email" in data and data["email"] != user.email:
        if db.query(User).filter(User.email == data["email"]).first():
            raise HTTPException(status_code=400, detail="El email ya esta en uso")
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return UserPublic.model_validate(user)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"message": f"Usuario '{user.username}' eliminado correctamente"}
