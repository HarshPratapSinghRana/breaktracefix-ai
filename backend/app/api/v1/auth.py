from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.tenant import Tenant
from backend.app.schemas.auth import LoginRequest, Token, UserRead, UserCreate
from backend.app.schemas.common import ResponseEnvelope
from backend.app.core.security import verify_password, create_access_token, hash_password
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=ResponseEnvelope[Token])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with email and password, returning JWT access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive."
        )
    
    token_str = create_access_token(
        subject=user.id,
        tenant_id=user.tenant_id,
        role=user.role
    )
    return ResponseEnvelope(
        data=Token(
            access_token=token_str,
            tenant_id=user.tenant_id,
            role=user.role,
            user_name=user.full_name
        ),
        message="Authentication successful."
    )

@router.post("/register", response_model=ResponseEnvelope[UserRead])
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user under a tenant."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )
    
    # Assign to default tenant if none specified
    tenant_id = payload.tenant_id
    if not tenant_id:
        default_tenant = db.query(Tenant).first()
        tenant_id = default_tenant.id if default_tenant else "tenant-default-001"
    
    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        tenant_id=tenant_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return ResponseEnvelope(data=new_user, message="User registered successfully.")

@router.get("/me", response_model=ResponseEnvelope[UserRead])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve currently authenticated user profile."""
    return ResponseEnvelope(data=current_user)

