import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_sso_google_callback_registers_new_user():
    # 1. Mock the user data Google would normally return
    mock_user_info = {
        "userinfo": {
            "email": "test@google.com",
            "name": "Test User",
            "sub": "1234567890" # Google's external ID
        }
    }

    # 2. Patch Authlib's authorize_access_token to return our mock data instantly
    with patch("authlib.integrations.starlette_client.apps.StarletteOAuth2App.authorize_access_token", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = mock_user_info
        
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            # 3. Hit the callback directly
            response = await client.get("/api/v1/auth/sso/callback/google")
            
            # 4. Assert success and cookie creation
            assert response.status_code == 200
            assert "access_token" in response.cookies
            assert "refresh_token" in response.cookies