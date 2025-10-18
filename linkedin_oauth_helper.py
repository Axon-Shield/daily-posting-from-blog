#!/usr/bin/env python3
"""
LinkedIn OAuth Helper - Get Access Token and User/Org ID
"""
import requests
import webbrowser
from urllib.parse import urlencode, parse_qs

# Your LinkedIn App Credentials
# Set these as environment variables or edit here:
import os
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "782udb7msn2pvi")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "")  # Set via: export LINKEDIN_CLIENT_SECRET='your_secret'
REDIRECT_URI = "https://blog.axonshield.com"  # Must match app settings

if not CLIENT_SECRET:
    print("ERROR: LINKEDIN_CLIENT_SECRET environment variable not set")
    print("Run: export LINKEDIN_CLIENT_SECRET='your_linkedin_client_secret_here'")
    import sys
    sys.exit(1)

# OAuth Scopes - Choose based on posting type
# For personal posting:
# SCOPES = ["openid", "profile", "email", "w_member_social"]

# For organization posting (Axon Shield company page):
SCOPES = [
    "openid",
    "profile", 
    "email",
    "w_organization_social",  # Post to organization pages
    "r_organization_social",  # Read organization data
]

def get_authorization_url():
    """Generate LinkedIn authorization URL."""
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": "random_state_string_12345"
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    return auth_url

def exchange_code_for_token(authorization_code):
    """Exchange authorization code for access token."""
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()

def get_user_info(access_token):
    """Get user profile information."""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Get basic profile
    response = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers=headers
    )
    response.raise_for_status()
    user_info = response.json()
    
    # Get detailed profile to extract person URN
    response = requests.get(
        "https://api.linkedin.com/v2/me",
        headers=headers
    )
    response.raise_for_status()
    me_info = response.json()
    
    return {
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "user_id": me_info.get("id"),
        "sub": user_info.get("sub")
    }

def main():
    """Main OAuth flow."""
    print("=" * 60)
    print("LINKEDIN OAUTH HELPER")
    print("=" * 60)
    print()
    print("This will help you get your LinkedIn Access Token and User ID.")
    print()
    
    # Step 1: Get authorization URL
    auth_url = get_authorization_url()
    print("STEP 1: Authorize the App")
    print("-" * 60)
    print("Opening LinkedIn authorization page in your browser...")
    print()
    print("If it doesn't open automatically, visit this URL:")
    print(auth_url)
    print()
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
    except:
        pass
    
    # Step 2: Get authorization code
    print("STEP 2: Get Authorization Code")
    print("-" * 60)
    print("After authorizing, LinkedIn will redirect you to:")
    print(f"{REDIRECT_URI}?code=XXXXX&state=XXXXX")
    print()
    print("Copy the ENTIRE URL from your browser address bar:")
    redirect_url = input("Paste the redirect URL here: ").strip()
    print()
    
    # Extract code from URL
    if "code=" in redirect_url:
        parsed = parse_qs(redirect_url.split("?")[1])
        authorization_code = parsed.get("code", [None])[0]
    else:
        print("❌ Error: Could not find authorization code in URL")
        print("Make sure you copied the entire URL")
        return
    
    if not authorization_code:
        print("❌ Error: Invalid authorization code")
        return
    
    print(f"✓ Found authorization code: {authorization_code[:20]}...")
    print()
    
    # Step 3: Exchange code for access token
    print("STEP 3: Get Access Token")
    print("-" * 60)
    try:
        token_data = exchange_code_for_token(authorization_code)
        access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", "unknown")
        
        print(f"✅ SUCCESS! Got access token")
        print(f"   Expires in: {expires_in} seconds")
        print()
    except Exception as e:
        print(f"❌ Error getting access token: {e}")
        return
    
    # Step 4: Get user info
    print("STEP 4: Get User Information")
    print("-" * 60)
    try:
        user_info = get_user_info(access_token)
        print(f"✅ User: {user_info['name']}")
        print(f"   Email: {user_info['email']}")
        print(f"   User ID: {user_info['user_id']}")
        print()
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        print("Continuing anyway...")
        user_info = {"user_id": "UNKNOWN"}
    
    # Step 5: Show credentials
    print("=" * 60)
    print("YOUR LINKEDIN CREDENTIALS")
    print("=" * 60)
    print()
    print("Add these to your GitHub Secrets:")
    print()
    print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
    print(f"LINKEDIN_USER_ID={user_info['user_id']}")
    print()
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT NOTES:")
    print("- Access tokens typically expire in 60 days")
    print("- You'll need to refresh the token periodically")
    print("- This posts to your PERSONAL LinkedIn profile")
    print("- For company page posting, you need organization URN")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

