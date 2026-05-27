import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from app.main import app

# Create the reusable client fixture just like your other files
@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="https://testserver")


@pytest.mark.asyncio
async def test_sso_login_redirect(client):
    """Test that the login endpoint successfully redirects to Google's OAuth page."""
    # We use follow_redirects=False to catch the 302 Redirect response
    response = await client.get("/api/v1/auth/sso/login/google", follow_redirects=False)
    
    assert response.status_code == 302
    assert "accounts.google.com/o/oauth2" in response.headers["location"]


@pytest.mark.asyncio
async def test_sso_invalid_provider(client):
    """Test that an unregistered provider throws a 404."""
    response = await client.get("/api/v1/auth/sso/login/yahoo")
    
    assert response.status_code == 404
    assert "SSO provider not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_sso_callback_registers_new_user(client):
    """Test that a first-time SSO login creates a user and sets cookies."""
    mock_user_info = {
        "userinfo": {
            "email": "sso_new@example.com",
            "name": "SSO Test User",
            "sub": "google_12345"
        }
    }

    with patch("authlib.integrations.starlette_client.apps.StarletteOAuth2App.authorize_access_token", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = mock_user_info
        
        response = await client.get("/api/v1/auth/sso/callback/google")
        
        # 1. Assert successful login
        assert response.status_code == 200
        assert "Successfully logged in via google" in response.json()["message"]
        
        # 2. Assert cookies are set
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies
        
        # 3. Assert user was saved to DB correctly (Hitting the protected route)
        me_response = await client.get("/api/v1/user/me")
        assert me_response.status_code == 200
        
        data = me_response.json()
        assert data["email"] == "sso_new@example.com"
        assert data["is_verified"] is True  # SSO accounts should be auto-verified
        assert data["profile"]["full_name"] == "SSO Test User"


@pytest.mark.asyncio
async def test_sso_callback_logs_in_existing_user(client):
    """Test that subsequent SSO logins for the same email just log them in safely."""
    # We use the same mock data as the previous test
    mock_user_info = {
        "userinfo": {
            "email": "sso_new@example.com",
            "name": "SSO Test User",
            "sub": "google_12345"
        }
    }

    with patch("authlib.integrations.starlette_client.apps.StarletteOAuth2App.authorize_access_token", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = mock_user_info
        
        # Hit the callback AGAIN
        response = await client.get("/api/v1/auth/sso/callback/google")
        
        # It should NOT throw an IntegrityError for duplicate email, 
        # it should just successfully issue new cookies.
        assert response.status_code == 200
        assert "access_token" in response.cookies
        
        
@pytest.mark.asyncio
async def test_sso_callback_missing_email(client):
    """Test that Google returning an incomplete payload is handled gracefully."""
    # Missing the 'email' field
    bad_mock_info = {
        "userinfo": {
            "name": "No Email User",
            "sub": "google_999"
        }
    }

    with patch("authlib.integrations.starlette_client.apps.StarletteOAuth2App.authorize_access_token", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = bad_mock_info
        
        response = await client.get("/api/v1/auth/sso/callback/google")
        
        assert response.status_code == 400
        assert "Failed to fetch user details" in response.json()["detail"]