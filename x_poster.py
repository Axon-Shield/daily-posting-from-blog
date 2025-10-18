"""
X (Twitter) posting module.
"""
import tweepy
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
        """Initialize Tweepy client."""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            print("Warning: X (Twitter) credentials not fully configured")
            return
        
        try:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                wait_on_rate_limit=True
            )
        except Exception as e:
            print(f"Error initializing X client: {e}")
    
    def post(self, text: str) -> Dict:
        """
        Post a tweet to X.
        
        Args:
            text: The text content to tweet (max 280 characters)
            
        Returns:
            Dictionary with response information
        """
        if not self.client:
            raise ValueError("X (Twitter) credentials not configured")
        
        # Ensure text fits within character limit
        if len(text) > 280:
            text = text[:277] + "..."
        
        try:
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

