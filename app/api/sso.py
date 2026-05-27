from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone, timedelta

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, Profile, UserRefreshToken
from app.core.security import create_access_token, create_refresh_token

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

oauth.register(
    name='github',
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

router = APIRouter(prefix="/auth/sso", tags=["sso"])

@router.get("/{provider}/login")
async def sso_login(provider: str, request: Request):
    client = oauth.create_client(provider)
    if not client:
        raise HTTPException(status_code=404, detail="SSO provider not found")
    redirect_uri = request.url_for('sso_callback', provider=provider)
    return await client.authorize_redirect(request, redirect_uri)

@router.get("/{provider}/callback")
async def sso_callback(
    provider: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)
    user_info = token.get('userinfo')
    
    if not user_info or not user_info.get('email'):
        raise HTTPException(status_code=400, detail="Failed to fetch user details")

    query = select(User).where(User.email == user_info['email'])
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=user_info['email'],
            hashed_password=None,
            auth_provider=provider,
            external_id=user_info['sub'],
            is_verified=True,
            profile=Profile(full_name=user_info.get('name', ''))
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    access_token = create_access_token(user.id)
    refresh_token_str, jti = create_refresh_token(user.id)
    
    db_refresh_token = UserRefreshToken(
        user_id=user.id,
        token_jti=jti,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_refresh_token)
    await db.commit()

    response.set_cookie(
        key="access_token", value=access_token, httponly=True, secure=True, samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token_str, httponly=True, secure=True, samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return {"message": f"Successfully logged in via {provider}"}