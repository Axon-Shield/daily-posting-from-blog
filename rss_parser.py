"""
RSS feed parser for extracting blog posts.
"""
import feedparser
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from config import Config


class RSSParser:
    """Parser for blog RSS feeds."""
    
    def __init__(self, feed_url: str = None):
        """Initialize RSS parser with feed URL."""
        self.feed_url = feed_url or Config.BLOG_RSS_FEED_URL
    
    def fetch_latest_posts(self, limit: int = 5) -> List[Dict]:
        """
        Fetch the latest posts from the RSS feed.
        
        Args:
            limit: Maximum number of posts to fetch
            
        Returns:
            List of dictionaries containing post information
        """
        try:
            feed = feedparser.parse(self.feed_url)
            posts = []
            
            for entry in feed.entries[:limit]:
                post = self._parse_entry(entry)
                if post:
                    posts.append(post)
            
            return posts
        
        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
            return []
    
    def _parse_entry(self, entry) -> Optional[Dict]:
        """Parse a single RSS feed entry."""
        try:
            # Extract content
            content = ""
            if hasattr(entry, 'content'):
                content = entry.content[0].value
            elif hasattr(entry, 'summary'):
                content = entry.summary
            elif hasattr(entry, 'description'):
                content = entry.description
            
            # Clean HTML from content
            clean_content = self._clean_html(content)
            
            # Extract published date
            published_date = None
            if hasattr(entry, 'published_parsed'):
                published_date = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'updated_parsed'):
                published_date = datetime(*entry.updated_parsed[:6]).isoformat()
            else:
                published_date = datetime.now().isoformat()
            
            return {
                'url': entry.link,
                'title': entry.title,
                'content': clean_content,
                'published_date': published_date,
                'summary': entry.get('summary', '')[:500]
            }
        
        except Exception as e:
            print(f"Error parsing entry: {e}")
            return None
    
    def _clean_html(self, html_content: str) -> str:
        """Remove HTML tags and clean up content."""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

