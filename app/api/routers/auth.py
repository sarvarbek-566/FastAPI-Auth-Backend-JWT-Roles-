from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.auth import RegisterRequest, RegisterResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_db, get_current_user, require_admin
from app.repositories.user_repo import get_by_email, create_user, set_role

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = get_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    hashed = hash_password(data.password)
    create_user(db, email=data.email, hashed_password=hashed)

    return {"email": data.email, "message": "user registered successfully"}

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = get_by_email(db, form_data.username)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.email, role=user.role)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(current_user = Depends(get_current_user)):
    return {"email": current_user.email, "role": current_user.role}

@router.get("/admin/ping")
def admin_ping(admin_user = Depends(require_admin)):
    return {"message": "admin ok", "email": admin_user.email}

@router.post("/make-admin")
def make_admin(email: str, db: Session = Depends(get_db), admin_user = Depends(require_admin)):
    user = set_role(db, email=email, role="admin")
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return {"email": user.email, "role": user.role}
