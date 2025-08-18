from fastapi import Request
from src.oauth_service import tiktok_service

# TikTok OAuth
async def login(request: Request, provider: str, oauth, redirect_uri, email, platform):
    """Gọi đến hàm login của TikTok"""
    if provider == "tiktok":
        return await tiktok_service.login(
            request, provider, oauth, redirect_uri, email, platform
        )
    else:
        return {"error": "Unsupported provider"}

async def callback(request: Request, provider, oauth, email, platform):
    """Gọi đến hàm để handle callback từ TikTok"""
    if provider == "tiktok":
        return await tiktok_service.handle_callback(
            request, provider, oauth, email, platform
        )
    else:
        return {"error": "Unsupported provider"}

async def get_accounts(provider, user):
    """Lấy danh sách tài khoản TikTok"""
    if provider == "tiktok":
        return await tiktok_service.get_tiktok_accounts(provider, user)
    else:
        return {"error": "Unsupported provider"}

async def get_videos(provider, provider_id, oauth, user):
    """Lấy danh sách video TikTok"""
    try:
        if provider == "tiktok":
            return await tiktok_service.get_user_videos(provider, provider_id, oauth, user)
        else:
            return {"error": "Unsupported provider"}
    except Exception as e:
        print(f"Error getting videos: {e}")
        return {"error": str(e)}

async def create_video_post(request: Request, provider, oauth, user):
    """Gọi đến hàm tạo video TikTok"""
    if provider == "tiktok":
        return await tiktok_service.create_video_post(request, provider, oauth, user)
    else:
        return {"error": "Unsupported provider"}
