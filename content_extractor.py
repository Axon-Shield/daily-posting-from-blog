"""
AI-powered content extraction using Anthropic Claude API.
"""
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
3. Be between 150-250 characters for maximum engagement
4. Highlight a key insight, statistic, or takeaway from the post
5. Be written in an engaging, professional tone
6. Include a call-to-action or thought-provoking element where appropriate

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
            # X has character limit, so be more conservative
            max_length = 280 - len(blog_url) - 10  # Leave room for URL and spacing
            
            if len(message) > max_length:
                message = message[:max_length-3] + "..."
            
            enhanced = f"{message}\n\n{blog_url}"
            
            # Add hashtags if they fit
            if hashtags:
                hashtag_str = " ".join(f"#{tag}" for tag in hashtags[:3])  # Limit to 3 hashtags
                if len(enhanced) + len(hashtag_str) + 2 <= 280:
                    enhanced += "\n" + hashtag_str
            
            return enhanced
        
        return message

