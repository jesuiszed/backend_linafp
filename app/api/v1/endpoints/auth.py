from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import RefreshTokenRequest, TokenPair
from app.schemas.user import BootstrapAdminRequest, UserMe

router = APIRouter()


@router.post("/login", response_model=TokenPair)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenPair:
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token = create_token(
        subject=str(user.id),
        role=user.role.value,
        token_type="access",
        expires_delta_minutes=settings.access_token_expire_minutes,
    )
    refresh_token = create_token(
        subject=str(user.id),
        role=user.role.value,
        token_type="refresh",
        expires_delta_minutes=settings.refresh_token_expire_minutes,
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenPair:
    decoded = decode_token(payload.refresh_token)
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = decoded.get("sub")
    role = decoded.get("role")
    if not user_id or not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not available")

    access_token = create_token(
        subject=str(user.id),
        role=user.role.value,
        token_type="access",
        expires_delta_minutes=settings.access_token_expire_minutes,
    )
    new_refresh_token = create_token(
        subject=str(user.id),
        role=user.role.value,
        token_type="refresh",
        expires_delta_minutes=settings.refresh_token_expire_minutes,
    )
    return TokenPair(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserMe)
def me(current_user: User = Depends(get_current_user)) -> UserMe:
    return UserMe.model_validate(current_user)


@router.post("/bootstrap-admin", response_model=UserMe)
def bootstrap_admin(payload: BootstrapAdminRequest, db: Session = Depends(get_db)) -> UserMe:
    existing = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admin already exists")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserMe.model_validate(user)
