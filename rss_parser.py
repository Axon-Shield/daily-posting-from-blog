"""
RSS/JSON feed parser for extracting blog posts.
Supports RSS, Atom, and JSON Feed formats.
"""
import feedparser
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from config import Config


class RSSParser:
    """Parser for blog RSS/JSON feeds."""
    
    def __init__(self, feed_url: str = None):
        """Initialize feed parser with feed URL."""
        self.feed_url = feed_url or Config.BLOG_RSS_FEED_URL
    
    def fetch_latest_posts(self, limit: int = 5) -> List[Dict]:
        """
        Fetch the latest posts from RSS/Atom/JSON feed.
        
        Args:
            limit: Maximum number of posts to fetch
            
        Returns:
            List of dictionaries containing post information
        """
        try:
            print(f"Fetching from: {self.feed_url}", flush=True)
            
            # Check if this is a JSON feed by URL or content type
            if self.feed_url.endswith('.json'):
                print("Detected JSON feed format", flush=True)
                return self._fetch_json_feed(limit)
            
            # Try parsing with feedparser (supports RSS, Atom, and JSON Feed)
            print("Parsing feed with feedparser...", flush=True)
            feed = feedparser.parse(self.feed_url)
            print("Feed parsed successfully", flush=True)
            
            # Check for errors
            if hasattr(feed, 'bozo') and feed.bozo:
                if hasattr(feed, 'bozo_exception'):
                    print(f"Feed parsing warning: {feed.bozo_exception}")
            
            posts = []
            
            for entry in feed.entries[:limit]:
                post = self._parse_entry(entry)
                if post and self._is_post_recent_enough(post):
                    posts.append(post)
            
            return posts
        
        except Exception as e:
            print(f"Error fetching feed: {e}")
            return []
    
    def _fetch_json_feed(self, limit: int = 5) -> List[Dict]:
        """
        Fetch posts from a JSON Feed.
        
        Args:
            limit: Maximum number of posts to fetch
            
        Returns:
            List of dictionaries containing post information
        """
        try:
            print(f"Making HTTP request to JSON feed (timeout: 30s)...", flush=True)
            response = requests.get(self.feed_url, timeout=30)
            print(f"Response status: {response.status_code}", flush=True)
            response.raise_for_status()
            
            feed_data = response.json()
            posts = []
            
            items = feed_data.get('items', [])[:limit]
            for item in items:
                post = self._parse_json_item(item)
                if post and self._is_post_recent_enough(post):
                    posts.append(post)
            
            return posts
        
        except Exception as e:
            print(f"Error fetching JSON feed: {e}")
            return []
    
    def _parse_json_item(self, item: Dict) -> Optional[Dict]:
        """Parse a single JSON Feed item."""
        try:
            # Extract content (JSON Feed uses content_html or content_text)
            content = ""
            if 'content_html' in item:
                content = item['content_html']
            elif 'content_text' in item:
                content = item['content_text']
            elif 'summary' in item:
                content = item['summary']
            
            # Clean HTML from content
            clean_content = self._clean_html(content)
            
            # Extract published date
            published_date = item.get('date_published', datetime.now().isoformat())
            
            return {
                'url': item.get('url', ''),
                'title': item.get('title', 'Untitled'),
                'content': clean_content,
                'published_date': published_date,
                'summary': item.get('summary', clean_content[:500])
            }
        
        except Exception as e:
            print(f"Error parsing JSON item: {e}")
            return None
    
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
    
    def _is_post_recent_enough(self, post: Dict) -> bool:
        """
        Check if a post is recent enough based on the minimum date configuration.
        
        Args:
            post: Dictionary containing post information with 'published_date' key
            
        Returns:
            True if post is recent enough, False otherwise
        """
        try:
            # Parse the published date from the post
            published_date_str = post.get('published_date', '')
            if not published_date_str:
                # If no published date, assume it's recent enough
                return True
            
            # Parse the published date
            published_date = datetime.fromisoformat(published_date_str.replace('Z', '+00:00'))
            
            # Parse the minimum date from configuration
            min_date = datetime.fromisoformat(Config.MINIMUM_POST_DATE)
            
            # Check if the post is recent enough
            is_recent = published_date.date() >= min_date.date()
            
            if not is_recent:
                print(f"Skipping post '{post.get('title', 'Untitled')}' - published {published_date.date()} (before {min_date.date()})")
            
            return is_recent
            
        except Exception as e:
            print(f"Error checking post date: {e}")
            # If we can't parse the date, assume it's recent enough
            return True

