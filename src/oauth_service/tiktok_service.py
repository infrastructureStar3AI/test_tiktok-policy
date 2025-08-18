import json
import base64
import httpx
from fastapi import Request
from fastapi.responses import RedirectResponse

from schema.User import User
from shared_module.log import logging_config
from shared_module.DB import connect

logger = logging_config.get_logger("tiktok_service")

# TikTok OAuth endpoints
TIKTOK_AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TIKTOK_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
TIKTOK_USER_INFO_URL = "https://open.tiktokapis.com/v2/user/info/"
TIKTOK_VIDEO_UPLOAD_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"

async def login(request: Request, provider, oauth, redirect_uri, email, platform):
    """Handle TikTok OAuth login"""
    if provider != "tiktok":
        logger.warning(
            "Unsupported provider - Hiện phương thức đăng nhập này chưa hỗ trợ",
            log_type="app",
            extra_data={},
        )
        return {"error": "Unsupported provider"}
    
    logger.info("Điều hướng sang trang xác thực TikTok OAuth", log_type="app")
    oauth_provider = oauth.create_client(provider)
    
    state_data = {"email": email, "platform": platform}
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()
    
    # TikTok requires specific scopes for video publishing
    scopes = ["user.info.basic", "video.publish", "video.upload"]
    
    return await oauth_provider.authorize_redirect(
        request, 
        redirect_uri, 
        state=encoded_state,
        scope=" ".join(scopes)
    )

async def handle_callback(request: Request, provider, oauth, email, platform):
    """Handle TikTok OAuth callback"""
    try:
        if provider != "tiktok":
            logger.warning(
                "Unsupported provider - Hiện phương thức đăng nhập này chưa hỗ trợ",
                log_type="app",
                extra_data={},
            )
            return {"error": "Unsupported provider"}
        
        oauth_provider = oauth.create_client(provider)
        token = await oauth_provider.authorize_access_token(request)
        print("TikTok token:", token)
        
        # Get user info from TikTok
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                TIKTOK_USER_INFO_URL,
                headers={
                    "Authorization": f"Bearer {token['access_token']}",
                    "Content-Type": "application/json"
                },
                params={"fields": "open_id,union_id,avatar_url,display_name"}
            )
            user_response.raise_for_status()
            user_data = user_response.json()
            
        logger.info(
            f"OAuth callback from {provider} | User ID: {user_data['data']['user']['open_id']}",
            log_type="app",
        )
        
        user_info = User(email=email)
        
        # Create user if not exists
        async with httpx.AsyncClient() as client:
            create = await client.post(
                "http://user_service.railway.internal:8080/api/user/create_oauth_user",
                json={
                    "user": user_info.dict(),
                    "name": user_data['data']['user']['display_name'],
                    "provider_id": user_data['data']['user']['open_id'],
                    "provider": provider,
                    "token": token["access_token"],
                    "avatar": user_data['data']['user']['avatar_url'],
                },
            )
            create.raise_for_status()
            create = create.json()
        
        print(create)
        
        if create:
            if platform == "app":
                response = RedirectResponse(
                    url="star3ai://tiktok-login-success",
                    status_code=302,
                )
            else:
                response = RedirectResponse(
                    url="https://star3.ai/createproduct?icon=tiktok",
                    status_code=302,
                )
            
            response.set_cookie(
                key="access_token",
                value=json.dumps(token),
                httponly=True,
                secure=True,
                samesite="None",
                max_age=3600,
            )
            return response
            
    except Exception as e:
        logger.error(
            f"Authentication failed. Please try again: {str(e)}", log_type="error"
        )
        if platform == "app":
            response = RedirectResponse(
                url="yourapp://oauth/tiktok/callback?error={error_type}",
                status_code=302,
            )
        return {"error": f"Authentication failed. Please try again: {str(e)}"}

async def get_tiktok_accounts(provider, user):
    """Get TikTok accounts for user"""
    try:
        check = connect.db["users"].find_one({"email": user["email"]})
        list_accounts = []
        
        if check and "social_account" in check:
            for social_account in check["social_account"]:
                if social_account["provider"] == provider:
                    info = {
                        "name": social_account["name"],
                        "account_id": social_account["provider_id"],
                        "avatar": social_account["avatar"],
                    }
                    list_accounts.append(info)
        return list_accounts
    except Exception as e:
        raise e

async def create_video_post(request: Request, provider, oauth, user):
    """Create TikTok video post"""
    print("create TikTok video post------------")
    try:
        if provider != "tiktok":
            logger.warning(
                "Unsupported provider - Hiện phương thức đăng nhập này chưa hỗ trợ",
                log_type="app",
                extra_data={},
            )
            return {"error": "Unsupported provider"}
        
        logger.info("Tiến hành tạo video TikTok", log_type="app")
        logger.audit_log("Tiến hành tạo video TikTok", log_type="audit")
        
        try:
            data = await request.json()
            check = connect.db["users"].find_one({"email": user["email"]})
            
            # Find TikTok account
            tiktok_token = None
            if check and "social_account" in check:
                for social_account in check["social_account"]:
                    if data.get("provider_id") == social_account["provider_id"] and social_account["provider"] == "tiktok":
                        tiktok_token = social_account["token"]
                        break
            
            if not tiktok_token:
                return {"error": "TikTok account not found"}
            
            content = data.get("content", {})
            video_url = content.get("video_url")
            description = content.get("description", "")
            
            if not video_url:
                return {"error": "Video URL is required for TikTok posts"}
            
            # Step 1: Initialize video upload
            async with httpx.AsyncClient() as client:
                init_response = await client.post(
                    TIKTOK_VIDEO_UPLOAD_URL,
                    headers={
                        "Authorization": f"Bearer {tiktok_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "post_info": {
                            "title": description,
                            "privacy_level": "SELF_ONLY",  # or "PUBLIC_TO_EVERYONE"
                            "disable_duet": False,
                            "disable_comment": False,
                            "disable_stitch": False,
                            "video_cover_timestamp_ms": 1000
                        },
                        "source_info": {
                            "source": "FILE_UPLOAD",
                            "video_size": 50000000,  # Placeholder size
                            "chunk_size": 10000000,
                            "total_chunk_count": 5
                        }
                    }
                )
                init_response.raise_for_status()
                upload_data = init_response.json()
            
            print("TikTok upload initialization:", upload_data)
            
            # Step 2: Upload video chunks (simplified for example)
            # In a real implementation, you would need to:
            # 1. Download the video from video_url
            # 2. Split it into chunks
            # 3. Upload each chunk
            # 4. Publish the video
            
            logger.info(
                "Tạo video TikTok thành công",
                log_type="app",
                extra_data={"publish_id": upload_data.get("data", {}).get("publish_id")},
            )
            logger.audit_log(
                "Tạo video TikTok thành công",
                log_type="audit",
                extra_data={"publish_id": upload_data.get("data", {}).get("publish_id")},
            )
            
            return upload_data
            
        except Exception as e:
            raise e
            
    except Exception as e:
        logger.error(f"Fail to create TikTok video: {str(e)}", log_type="error")
        return {"error": f"Fail to create TikTok video. Please try again: {str(e)}"}

async def get_user_videos(provider, provider_id, oauth, user):
    """Get user's TikTok videos"""
    try:
        check = connect.db["users"].find_one({"email": user["email"]})
        
        # Find TikTok account
        tiktok_token = None
        if check and "social_account" in check:
            for social_account in check["social_account"]:
                if provider_id == social_account["provider_id"] and social_account["provider"] == "tiktok":
                    tiktok_token = social_account["token"]
                    break
        
        if not tiktok_token:
            return {"error": "TikTok account not found"}
        
        # Get user videos (if API supports it)
        async with httpx.AsyncClient() as client:
            videos_response = await client.get(
                "https://open.tiktokapis.com/v2/video/list/",
                headers={
                    "Authorization": f"Bearer {tiktok_token}",
                    "Content-Type": "application/json"
                },
                params={
                    "fields": "id,title,video_description,duration,cover_image_url,create_time"
                }
            )
            videos_response.raise_for_status()
            videos_data = videos_response.json()
        
        return videos_data.get("data", {}).get("videos", [])
        
    except Exception as e:
        print(f"Error getting TikTok videos: {e}")
        raise e
