#!/usr/bin/env python3
"""
Test script for TikTok Login API
This script demonstrates how to use the TikTok OAuth API endpoints
"""

import requests
import json
import os
from urllib.parse import parse_qs, urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000"
# Ngrok public URL for external testing
NGROK_URL = "https://ce1df3eca9e6.ngrok-free.app"

# TikTok credentials from environment
TIKTOK_CLIENT_ID = os.getenv('TIKTOK_CLIENT_ID')
TIKTOK_CLIENT_SECRET = os.getenv('TIKTOK_CLIENT_SECRET')

def test_credentials():
    """Test TikTok credentials configuration"""
    print("🔑 Testing TikTok credentials configuration...")
    
    if not TIKTOK_CLIENT_ID:
        print("❌ TIKTOK_CLIENT_ID not found in environment variables")
    else:
        print(f"✅ TIKTOK_CLIENT_ID: {TIKTOK_CLIENT_ID}")
    
    if not TIKTOK_CLIENT_SECRET:
        print("❌ TIKTOK_CLIENT_SECRET not found in environment variables")
    else:
        # Only show first 8 characters for security
        masked_secret = TIKTOK_CLIENT_SECRET[:8] + "*" * (len(TIKTOK_CLIENT_SECRET) - 8)
        print(f"✅ TIKTOK_CLIENT_SECRET: {masked_secret}")
    
    print()

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_tiktok_login():
    """Test TikTok OAuth login initiation"""
    print("🎯 Testing TikTok login initiation...")
    try:
        response = requests.get(
            f"{BASE_URL}/auth/tiktok/login",
            params={
                "email": "test@example.com",
                "platform": "web"
            },
            allow_redirects=False
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 307:
            redirect_url = response.headers.get('location')
            print(f"Redirect URL: {redirect_url}")
            
            # Parse the redirect URL to show OAuth parameters
            parsed_url = urlparse(redirect_url)
            params = parse_qs(parsed_url.query)
            print("OAuth Parameters:")
            for key, value in params.items():
                print(f"  {key}: {value[0] if value else 'N/A'}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_get_accounts():
    """Test getting TikTok accounts"""
    print("📱 Testing get TikTok accounts...")
    try:
        response = requests.get(f"{BASE_URL}/api/tiktok/accounts")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_create_video_post():
    """Test creating a TikTok video post"""
    print("🎬 Testing create TikTok video post...")
    try:
        test_data = {
            "provider_id": "test_tiktok_id",
            "content": {
                "video_url": "https://example.com/test_video.mp4",
                "description": "Test video description for TikTok API"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tiktok/video/create",
            json=test_data
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_with_ngrok():
    """Test with ngrok public URL"""
    print("🌐 Testing with ngrok public URL...")
    try:
        response = requests.get(f"{NGROK_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print(f"✅ Your API is accessible via: {NGROK_URL}")
    except Exception as e:
        print(f"❌ Error accessing ngrok URL: {e}")
    print()

def main():
    """Run all tests"""
    print("🚀 Starting TikTok Login API Tests")
    print("=" * 50)
    
    test_credentials()
    test_health_check()
    test_tiktok_login()
    test_get_accounts()
    test_create_video_post()
    test_with_ngrok()
    
    print("✅ All tests completed!")
    print("\nTo view the interactive API documentation, visit:")
    print(f"Local: {BASE_URL}/docs")
    print(f"Public: {NGROK_URL}/docs")
    print(f"\n📋 For TikTok OAuth callback, use: {NGROK_URL}/auth/tiktok/callback")

if __name__ == "__main__":
    main()
