"""
LinkedIn posting module.
"""
import requests
import os
import tempfile
from typing import Dict, Optional
from config import Config


class LinkedInPoster:
    """Post content to LinkedIn."""
    
    def __init__(self, access_token: str = None, user_id: str = None, org_id: str = None, post_as_org: bool = None):
        """
        Initialize LinkedIn poster.
        
        Args:
            access_token: LinkedIn API access token
            user_id: LinkedIn user ID (URN format)
            org_id: LinkedIn organization ID (for posting as company)
            post_as_org: If True, post as organization; if False, post as person
        """
        self.access_token = access_token or Config.LINKEDIN_ACCESS_TOKEN
        self.user_id = user_id or Config.LINKEDIN_USER_ID
        self.org_id = org_id or Config.LINKEDIN_ORG_ID
        self.post_as_org = post_as_org if post_as_org is not None else Config.LINKEDIN_POST_AS_ORG
        self.api_base = "https://api.linkedin.com/v2"
    
    def post(self, text: str, image_url: Optional[str] = None) -> Dict:
        """
        Post content to LinkedIn with optional image.
        
        Args:
            text: The text content to post
            image_url: Optional URL of image to attach
            
        Returns:
            Dictionary with response information
        """
        if not self.access_token:
            raise ValueError("LinkedIn access token not configured")
        
        # Determine author URN (person or organization)
        if self.post_as_org:
            if not self.org_id:
                raise ValueError("LinkedIn organization ID not configured")
            author_urn = f"urn:li:organization:{self.org_id}"
            print(f"Posting as organization: {self.org_id}")
        else:
            if not self.user_id:
                raise ValueError("LinkedIn user ID not configured")
            author_urn = f"urn:li:person:{self.user_id}"
            print(f"Posting as person: {self.user_id}")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Prepare the post data
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE" if image_url else "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # If image URL provided, upload and attach it
        if image_url:
            try:
                image_urn = self._upload_image(image_url)
                if image_urn:
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                        "status": "READY",
                        "media": image_urn
                    }]
                else:
                    print("Warning: Image upload failed, posting without image")
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "NONE"
            except Exception as e:
                print(f"Warning: Failed to attach image: {e}")
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "NONE"
        
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
    
    def _upload_image(self, image_path: str) -> Optional[str]:
        """
        Upload image to LinkedIn and return media URN.
        
        Args:
            image_path: Local file path or URL of image to upload
            
        Returns:
            Media URN string if successful, None otherwise
        """
        try:
            # Step 1: Register upload
            register_upload_url = f"{self.api_base}/assets?action=registerUpload"
            # Determine owner URN (person or organization)
            if self.post_as_org:
                owner_urn = f"urn:li:organization:{self.org_id}"
            else:
                owner_urn = f"urn:li:person:{self.user_id}"
            
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": owner_urn,
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            response = requests.post(register_upload_url, headers=headers, json=register_data, timeout=30)
            response.raise_for_status()
            
            register_result = response.json()
            upload_url = register_result['value']['uploadMechanism'][
                'com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            asset_urn = register_result['value']['asset']
            
            # Step 2: Read image data (from file path or URL)
            if os.path.isfile(image_path):
                # Local file
                with open(image_path, 'rb') as f:
                    image_data = f.read()
            else:
                # Assume it's a URL
                img_response = requests.get(image_path, timeout=30)
                img_response.raise_for_status()
                image_data = img_response.content
            
            # Step 3: Upload image binary
            upload_headers = {
                "Authorization": f"Bearer {self.access_token}",
            }
            
            upload_response = requests.put(upload_url, headers=upload_headers, data=image_data, timeout=60)
            upload_response.raise_for_status()
            
            print(f"✓ Uploaded image to LinkedIn: {asset_urn}")
            return asset_urn
            
        except Exception as e:
            print(f"Error uploading image to LinkedIn: {e}")
            return None

