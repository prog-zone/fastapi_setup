import jwt
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.limiter import limiter
from app.api.deps import get_current_user
from app.models.user import User, UserRefreshToken
from app.schemas.user import UserCreateSchema, UserSchema, UserBaseSchema, TokenRequestSchema, VerifyEmailRequestSchema
from app.core.email import send_verification_email, generate_otp


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserSchema)
async def register(user_in: UserCreateSchema, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    raw_otp = generate_otp()

    # Create user
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        verification_code=get_password_hash(raw_otp),
        verification_expire=datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    background_tasks.add_task(send_verification_email, user_in.email, raw_otp)
    return new_user


@router.post("/verify-email")
@limiter.limit("5/minute")
async def verify_email(
    request: Request,
    body: VerifyEmailRequestSchema,
    db: AsyncSession = Depends(get_db)
    ):
    query = select(User).where(User.email == body.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    if user.is_verified:
        return {"message": "Email is already verified"}
        
    if not user.verification_code or not user.verification_expire:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No verification code found")

    if datetime.now(timezone.utc) > user.verification_expire:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification code has expired")

    if not verify_password(body.code, user.verification_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")

    # Mark as verified and cleanup
    user.is_verified = True
    user.verification_code = None
    user.verification_expire = None
    
    await db.commit()
    return {"message": "Email successfully verified"}

@router.post("/resend-verification")
@limiter.limit("3/minute")
async def resend_verification(
    request: Request,
    body: UserBaseSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.email == body.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # Generic response prevents email enumeration attacks
    generic_response = {"message": "If that email exists and is unverified, a new code has been sent."}

    if not user or user.is_verified:
        return generic_response

    # Generate new OTP and overwrite existing
    raw_otp = generate_otp()
    user.verification_code = get_password_hash(raw_otp)
    user.verification_expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    await db.commit()
    
    background_tasks.add_task(send_verification_email, user.email, raw_otp)
    
    return generic_response


@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email address to log in")
    
    access_token = create_access_token(user.id)
    refresh_token_str, jti = create_refresh_token(user.id)
    
    db_refresh_token = UserRefreshToken(
        user_id=user.id,
        token_jti=jti,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_refresh_token)
    await db.commit()

    # Set both tokens as HttpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7*24*60*60 # 7 days (#TODO: change this env and fix max time)
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_str,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7*24*60*60 # 7 days (#TODO: change this to env)
    )
    
    return {"message": "Successfully logged in"}


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    # Read refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
        
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session invalid or expired")
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

    # Set new cookies
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7*24*60*60 # 7 days (#TODO: change this to env and fix max time)
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7*24*60*60 # 7 days (#TODO: change this to env and fix max time)
    )

    return {"message": "Tokens refreshed successfully"}


@router.post("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    
    if refresh_token:
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            jti = payload.get("jti")
            if jti:
                query = delete(UserRefreshToken).where(UserRefreshToken.token_jti == jti)
                await db.execute(query)
                await db.commit()
        except jwt.PyJWTError:
            pass

    # Clear both cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all_devices(
    response: Response, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Invalidate all refresh tokens in the database
    query = delete(UserRefreshToken).where(UserRefreshToken.user_id == current_user.id)
    await db.execute(query)
    await db.commit()

    # 2. Clear the cookies for the current active device
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {
        "message": "Successfully logged out from all devices."
    }