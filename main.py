from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os
from typing import Optional

import oauth_controller

app = FastAPI(title="TikTok Login API", version="1.0.0")

# Add session middleware for OAuth state management
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-in-production")

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# OAuth configuration
oauth = OAuth()

# TikTok OAuth configuration
# Note: TikTok doesn't have a standard OAuth discovery endpoint like Google
# You'll need to configure this manually with your TikTok app credentials
oauth.register(
    name='tiktok',
    client_id=os.getenv('TIKTOK_CLIENT_ID'),
    client_secret=os.getenv('TIKTOK_CLIENT_SECRET'),
    authorization_endpoint='https://www.tiktok.com/v2/auth/authorize/',
    token_endpoint='https://open.tiktokapis.com/v2/oauth/token/',
    client_kwargs={
        'scope': 'user.info.basic video.publish video.upload',
        'response_type': 'code',
    }
)

# Mock user authentication for testing
def get_current_user():
    """Mock function to get current user - replace with your actual authentication"""
    return {"email": "test@example.com", "id": "test_user_id"}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "TikTok Login API is running", "status": "ok"}

@app.get("/auth/{provider}/login")
async def login_endpoint(
    request: Request,
    provider: str,
    email: Optional[str] = None,
    platform: str = "web"
):
    """Initiate OAuth login with TikTok"""
    if not email:
        email = "test@example.com"  # Default for testing
    
    redirect_uri = str(request.url_for("callback_endpoint", provider=provider))
    
    return await oauth_controller.login(
        request, provider, oauth, redirect_uri, email, platform
    )

@app.get("/auth/{provider}/callback")
async def callback_endpoint(
    request: Request,
    provider: str,
    email: Optional[str] = None,
    platform: str = "web"
):
    """Handle OAuth callback from TikTok"""
    if not email:
        email = "test@example.com"  # Default for testing
    
    return await oauth_controller.callback(
        request, provider, oauth, email, platform
    )

@app.get("/api/{provider}/accounts")
async def get_accounts_endpoint(
    provider: str,
    user: dict = Depends(get_current_user)
):
    """Get user's TikTok accounts"""
    return await oauth_controller.get_accounts(provider, user)

@app.get("/api/{provider}/videos/{provider_id}")
async def get_videos_endpoint(
    provider: str,
    provider_id: str,
    user: dict = Depends(get_current_user)
):
    """Get user's TikTok videos"""
    return await oauth_controller.get_videos(provider, provider_id, oauth, user)

@app.post("/api/{provider}/video/create")
async def create_video_endpoint(
    request: Request,
    provider: str,
    user: dict = Depends(get_current_user)
):
    """Create a new TikTok video post"""
    return await oauth_controller.create_video_post(request, provider, oauth, user)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
