"""
AI-powered content extraction using Anthropic Claude API.
"""
import os
from anthropic import Anthropic
from typing import List
from config import Config


class ContentExtractor:
    """Extract key messaging points from blog posts using AI."""
    
    def __init__(self, api_key: str = None):
        """Initialize the content extractor with Anthropic API."""
        self.api_key = api_key or Config.ANTHROPIC_API_KEY
        self.client = Anthropic(api_key=self.api_key)
    
    def extract_daily_messages(self, title: str, content: str, 
                              num_messages: int = 7) -> List[str]:
        """
        Extract key messaging points from a blog post.
        
        Args:
            title: Blog post title
            content: Blog post content
            num_messages: Number of messages to extract (default 7 for daily posting)
            
        Returns:
            List of extracted messages suitable for social media posting
        """
        prompt = self._create_extraction_prompt(title, content, num_messages)
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response
            response_text = message.content[0].text
            messages = self._parse_messages(response_text)
            
            # Ensure we have exactly the requested number of messages
            if len(messages) < num_messages:
                print(f"Warning: Only extracted {len(messages)} messages, expected {num_messages}")
            
            return messages[:num_messages]
        
        except Exception as e:
            print(f"Error extracting content: {e}")
            raise
    
    def _create_extraction_prompt(self, title: str, content: str, 
                                 num_messages: int) -> str:
        """Create the prompt for content extraction."""
        return f"""You are a social media content strategist. I have a blog post that I want to promote on LinkedIn and X (Twitter) over the course of a week with daily posts.

Blog Title: {title}

Blog Content:
{content[:3000]}  # Limit content to avoid token limits

Please extract {num_messages} distinct, engaging messaging points from this blog post. Each message should:
1. Be standalone and make sense without context
2. Be suitable for both LinkedIn and X (Twitter)
3. Be between 100-200 words for optimal engagement and readability
4. Highlight a key insight, statistic, or takeaway from the post
5. Be written in an engaging, professional tone
6. Include a call-to-action or thought-provoking element where appropriate
7. Provide enough detail to be valuable while remaining concise

Format your response as a numbered list (1. 2. 3. etc.) with one message per line.
Do not include hashtags or emojis - I will add those when posting.
Do not include the link to the blog post - I will add that separately.

Messages:"""
    
    def _parse_messages(self, response_text: str) -> List[str]:
        """Parse the AI response into individual messages."""
        messages = []
        lines = response_text.strip().split('\n')
        
        current_message = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a numbered line (e.g., "1.", "2.", etc.)
            if line[0].isdigit() and '.' in line[:4]:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message.strip())
                
                # Start new message (remove the number and dot)
                parts = line.split('.', 1)
                if len(parts) > 1:
                    current_message = parts[1].strip()
                else:
                    current_message = line
            else:
                # Continue current message
                current_message += " " + line
        
        # Add the last message
        if current_message:
            messages.append(current_message.strip())
        
        return messages
    
    def enhance_for_platform(self, message: str, platform: str, 
                            blog_url: str, hashtags: List[str] = None) -> str:
        """
        Enhance a message for a specific platform.
        
        Args:
            message: The base message
            platform: 'linkedin' or 'x'
            blog_url: URL to the blog post
            hashtags: List of hashtags to include
            
        Returns:
            Platform-optimized message
        """
        if platform == 'linkedin':
            enhanced = f"{message}\n\nRead more: {blog_url}"
            if hashtags:
                enhanced += "\n\n" + " ".join(f"#{tag}" for tag in hashtags)
            return enhanced
        
        elif platform == 'x':
            # Check if Premium account is enabled for longer messages
            # Reload from environment to get current value
            is_premium = os.getenv('X_PREMIUM_ACCOUNT', 'true').lower() == 'true'
            
            # Calculate word limits based on account type
            if is_premium:
                # Premium accounts: allow up to ~5000 words (well within 25,000 char limit)
                max_words = 5000
            else:
                # Standard accounts: limit to ~35 words to stay within 280 character limit
                max_words = 35
            
            # For standard accounts, truncate message before adding URL and hashtags
            if not is_premium:
                # Account for URL length and some buffer for hashtags
                url_length = len(blog_url) + 4  # URL + "\n\n"
                hashtag_buffer = 50  # Buffer for potential hashtags
                available_chars = 280 - url_length - hashtag_buffer
                
                # Truncate the original message to fit
                if len(message) > available_chars:
                    message = message[:available_chars-3] + "..."
            
            # Create enhanced message with URL
            enhanced = f"{message}\n\n{blog_url}"
            
            # Add hashtags if they fit within character limits
            if hashtags:
                hashtag_limit = 10 if is_premium else 3  # More hashtags allowed for Premium
                hashtag_str = " ".join(f"#{tag}" for tag in hashtags[:hashtag_limit])
                
                # Check if hashtags fit within character limits
                char_limit = 25000 if is_premium else 280
                if len(enhanced) + len(hashtag_str) + 2 <= char_limit:
                    enhanced += "\n" + hashtag_str
            
            return enhanced
        
        return message
    
    def _count_words(self, text: str) -> int:
        """Count the number of words in a text."""
        return len(text.split())
    
    def _truncate_to_word_limit(self, text: str, max_words: int) -> str:
        """Truncate text to a maximum number of words."""
        words = text.split()
        if len(words) <= max_words:
            return text
        
        # Truncate and add ellipsis
        truncated_words = words[:max_words-1]
        return ' '.join(truncated_words) + '...'

