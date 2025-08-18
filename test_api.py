#!/usr/bin/env python3
"""
Test script for TikTok Login API
This script demonstrates how to use the TikTok OAuth API endpoints
"""

import requests
import json
from urllib.parse import parse_qs, urlparse

# API base URL
BASE_URL = "http://localhost:8000"

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

def main():
    """Run all tests"""
    print("🚀 Starting TikTok Login API Tests")
    print("=" * 50)
    
    test_health_check()
    test_tiktok_login()
    test_get_accounts()
    test_create_video_post()
    
    print("✅ All tests completed!")
    print("\nTo view the interactive API documentation, visit:")
    print(f"{BASE_URL}/docs")

if __name__ == "__main__":
    main()
