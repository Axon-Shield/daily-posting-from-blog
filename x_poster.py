"""
X (Twitter) posting module.
"""
import tweepy
import requests
import tempfile
import os
from typing import Dict, Optional
from config import Config


class XPoster:
    """Post content to X (Twitter)."""
    
    def __init__(self, api_key: str = None, api_secret: str = None,
                 access_token: str = None, access_token_secret: str = None,
                 bearer_token: str = None):
        """
        Initialize X poster with API credentials.
        
        Args:
            api_key: X API key (consumer key)
            api_secret: X API secret (consumer secret)
            access_token: X access token
            access_token_secret: X access token secret
            bearer_token: X bearer token
        """
        self.api_key = api_key or Config.X_API_KEY
        self.api_secret = api_secret or Config.X_API_SECRET
        self.access_token = access_token or Config.X_ACCESS_TOKEN
        self.access_token_secret = access_token_secret or Config.X_ACCESS_TOKEN_SECRET
        self.bearer_token = bearer_token or Config.X_BEARER_TOKEN
        
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Tweepy client and API (v1.1 for media upload)."""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            print("Warning: X (Twitter) credentials not fully configured")
            return
        
        try:
            # Client for v2 API (creating tweets)
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # API v1.1 for media upload
            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_token_secret
            )
            self.api = tweepy.API(auth)
            
        except Exception as e:
            print(f"Error initializing X client: {e}")
            self.api = None
    
    def post(self, text: str, image_url: Optional[str] = None) -> Dict:
        """
        Post a tweet to X with optional image.
        
        Args:
            text: The text content to tweet (max 280 characters)
            image_url: Optional URL of image to attach
            
        Returns:
            Dictionary with response information
        """
        if not self.client:
            raise ValueError("X (Twitter) credentials not configured")
        
        # Ensure text fits within character limit
        if len(text) > 280:
            text = text[:277] + "..."
        
        try:
            # Upload media if provided
            media_id = None
            if image_url and self.api:
                media_id = self._upload_image(image_url)
            
            # Create tweet with or without media
            if media_id:
                response = self.client.create_tweet(text=text, media_ids=[media_id])
            else:
                response = self.client.create_tweet(text=text)
            
            return {
                "success": True,
                "platform": "x",
                "tweet_id": response.data['id'],
                "response": response.data
            }
        
        except Exception as e:
            print(f"Error posting to X: {e}")
            return {
                "success": False,
                "platform": "x",
                "error": str(e)
            }
    
    def verify_credentials(self) -> bool:
        """
        Verify that X credentials are valid.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        if not self.client:
            return False
        
        try:
            me = self.client.get_me()
            return me.data is not None
        except:
            return False
    
    def _upload_image(self, image_path: str) -> Optional[str]:
        """
        Upload image to X and return media ID.
        
        Args:
            image_path: Local file path or URL of image to upload
            
        Returns:
            Media ID string if successful, None otherwise
        """
        if not self.api:
            print("Warning: X API v1.1 not initialized, cannot upload media")
            return None
        
        try:
            # Check if it's a local file or URL
            if os.path.isfile(image_path):
                # Already a local file, upload directly
                media = self.api.media_upload(filename=image_path)
                print(f"✓ Uploaded image to X: {media.media_id}")
                return str(media.media_id)
            else:
                # It's a URL, download first
                response = requests.get(image_path, timeout=30)
                response.raise_for_status()
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_path = tmp_file.name
                
                try:
                    # Upload to X using v1.1 API
                    media = self.api.media_upload(filename=tmp_path)
                    print(f"✓ Uploaded image to X: {media.media_id}")
                    return str(media.media_id)
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
            
        except Exception as e:
            print(f"Error uploading image to X: {e}")
            return None

