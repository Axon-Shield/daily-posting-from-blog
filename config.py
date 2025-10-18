"""
Configuration management for the blog posting automation system.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for application settings."""
    
    # Blog Configuration
    BLOG_RSS_FEED_URL = os.getenv('BLOG_RSS_FEED_URL')
    
    # Anthropic API Configuration
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # xAI Grok API Configuration (for image generation)
    XAI_API_KEY = os.getenv('XAI_API_KEY')
    GENERATE_IMAGES = os.getenv('GENERATE_IMAGES', 'true').lower() == 'true'
    
    # LinkedIn Configuration
    LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN')
    LINKEDIN_USER_ID = os.getenv('LINKEDIN_USER_ID')
    LINKEDIN_ORG_ID = os.getenv('LINKEDIN_ORG_ID')  # For posting as organization
    LINKEDIN_POST_AS_ORG = os.getenv('LINKEDIN_POST_AS_ORG', 'true').lower() == 'true'
    LINKEDIN_ENABLED = os.getenv('LINKEDIN_ENABLED', 'false').lower() == 'true'  # Disabled by default
    
    # X (Twitter) Configuration
    X_API_KEY = os.getenv('X_API_KEY')
    X_API_SECRET = os.getenv('X_API_SECRET')
    X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
    X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')
    X_BEARER_TOKEN = os.getenv('X_BEARER_TOKEN')
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', './data/posts.db')
    
    # Schedule Configuration
    POSTS_PER_BLOG = int(os.getenv('POSTS_PER_BLOG', 5))
    
    # Date Filtering Configuration
    MINIMUM_POST_DATE = os.getenv('MINIMUM_POST_DATE', '2025-10-15')
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present."""
        required_fields = [
            'BLOG_RSS_FEED_URL',
            'ANTHROPIC_API_KEY',
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing_fields)}\n"
                f"Please check your .env file."
            )
        
        # Create data directory if it doesn't exist
        Path(cls.DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
        
        return True

