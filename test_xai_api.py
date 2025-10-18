#!/usr/bin/env python3
"""
Simple test to verify xAI API key and image generation access.
"""
import requests
import os
import base64
from config import Config

def test_xai_api():
    """Test xAI API access."""
    print("🧪 Testing xAI Grok API Access\n")
    
    api_key = Config.XAI_API_KEY
    
    if not api_key:
        print("❌ XAI_API_KEY not configured")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    # Test 1: Simple image generation request
    print("Test 1: Attempting image generation...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "grok-2-image",
        "prompt": "A simple red circle on a white background",
        "n": 1,
        "response_format": "b64_json"
    }
    
    try:
        response = requests.post(
            "https://api.x.ai/v1/images/generations",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text[:500]}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                b64_data = result['data'][0]['b64_json']
                # Decode and save test image
                image_bytes = base64.b64decode(b64_data)
                test_path = "test_image.jpg"
                with open(test_path, 'wb') as f:
                    f.write(image_bytes)
                print(f"✅ SUCCESS! Image generated and saved to: {test_path}")
                print(f"   Image size: {len(image_bytes)} bytes")
                return True
            else:
                print(f"⚠️  Response missing image data")
                return False
        
        elif response.status_code == 403:
            print("❌ 403 Forbidden Error")
            print()
            print("Possible causes:")
            print("  1. API key is invalid or expired")
            print("  2. Image generation not enabled on your account")
            print("  3. Account needs verification or payment method")
            print("  4. Beta access required (not yet approved)")
            print()
            print("Next steps:")
            print("  → Visit https://x.ai/api")
            print("  → Check account status and permissions")
            print("  → Verify API key is active")
            print("  → Check if image generation requires special access")
            return False
        
        elif response.status_code == 401:
            print("❌ 401 Unauthorized - API key is invalid")
            print("  → Regenerate your API key at https://x.ai/api")
            return False
        
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_xai_api()
    exit(0 if success else 1)

