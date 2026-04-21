from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

import jwt
import uuid
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.api.deps import get_current_user
from app.models.user import User, UserRefreshToken
from app.schemas.user import UserCreate, User as UserSchema, TokenRequest


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserSchema)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    # Create user
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login")
async def login(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    
    refresh_token_str, jti = create_refresh_token(user.id)
    
    db_refresh_token = UserRefreshToken(
        user_id=user.id,
        token_jti=jti,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_refresh_token)
    await db.commit()
    
    return {
        "status": status.HTTP_200_OK,
        "access_token": create_access_token(user.id),
        "refresh_token": refresh_token_str,
    }


@router.post("/refresh")
async def refresh_token(body: TokenRequest, db: AsyncSession = Depends(get_db)):
    refresh_token = body.refresh_token
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        
        user_id_str = payload.get("sub")
        jti = payload.get("jti")
        user_id = uuid.UUID(user_id_str)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate refresh token")

    query = select(UserRefreshToken).where(
        UserRefreshToken.user_id == user_id, 
        UserRefreshToken.token_jti == jti
    )
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate refresh token")
    await db.delete(db_token)
    
    new_access_token = create_access_token(user_id)
    new_refresh_token, new_jti = create_refresh_token(user_id)

    db_new_token = UserRefreshToken(
        user_id=user_id,
        token_jti=new_jti,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_new_token)
    await db.commit()

    return {
        "status": status.HTTP_200_OK,
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }


@router.post("/logout")
async def logout(body: TokenRequest, db: AsyncSession = Depends(get_db)):
    refresh_token = body.refresh_token
    try:
        payload = jwt.decode(
            refresh_token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        jti = payload.get("jti")
        token_type = payload.get("type")
        
        if token_type != "refresh" or not jti:
             raise HTTPException(status_code=400, detail="Invalid token type for logout")
             
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    query = delete(UserRefreshToken).where(UserRefreshToken.token_jti == jti)
    result = await db.execute(query)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Session already closed or not found")

    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all_devices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    query = delete(UserRefreshToken).where(UserRefreshToken.user_id == current_user.id)
    await db.execute(query)
    await db.commit()

    return {
        "message": "Successfully logged out from all devices."
    }