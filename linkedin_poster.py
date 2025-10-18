"""
LinkedIn posting module.
"""
import requests
from typing import Dict, Optional
from config import Config


class LinkedInPoster:
    """Post content to LinkedIn."""
    
    def __init__(self, access_token: str = None, user_id: str = None):
        """
        Initialize LinkedIn poster.
        
        Args:
            access_token: LinkedIn API access token
            user_id: LinkedIn user ID (URN format)
        """
        self.access_token = access_token or Config.LINKEDIN_ACCESS_TOKEN
        self.user_id = user_id or Config.LINKEDIN_USER_ID
        self.api_base = "https://api.linkedin.com/v2"
    
    def post(self, text: str) -> Dict:
        """
        Post content to LinkedIn.
        
        Args:
            text: The text content to post
            
        Returns:
            Dictionary with response information
        """
        if not self.access_token or not self.user_id:
            raise ValueError("LinkedIn credentials not configured")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Prepare the post data
        post_data = {
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/ugcPosts",
                headers=headers,
                json=post_data,
                timeout=30
            )
            
            response.raise_for_status()
            
            return {
                "success": True,
                "platform": "linkedin",
                "response": response.json(),
                "status_code": response.status_code
            }
        
        except requests.exceptions.RequestException as e:
            print(f"Error posting to LinkedIn: {e}")
            return {
                "success": False,
                "platform": "linkedin",
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def verify_credentials(self) -> bool:
        """
        Verify that LinkedIn credentials are valid.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        if not self.access_token:
            return False
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        
        try:
            response = requests.get(
                f"{self.api_base}/me",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        
        except:
            return False

