"""
AI-powered image generation using xAI's Grok API.
"""
import requests
import os
import base64
import tempfile
import hashlib
from typing import Optional, Dict
from config import Config
from anthropic import Anthropic


class ImageGenerator:
    """Generate images for social media posts using Grok."""
    
    XAI_API_BASE = "https://api.x.ai/v1"
    IMAGE_MODEL = "grok-2-image"
    
    def __init__(self, api_key: str = None):
        """
        Initialize image generator with xAI API.
        
        Args:
            api_key: xAI API key
        """
        self.api_key = api_key or Config.XAI_API_KEY
        self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    
    def create_image_prompt(self, blog_title: str, message_text: str) -> str:
        """
        Create an optimized image prompt from blog content using Claude.
        
        Args:
            blog_title: Title of the blog post
            message_text: The social media message text
            
        Returns:
            Optimized prompt for image generation
        """
        try:
            prompt = f"""You are an expert at creating prompts for AI image generation.

Blog Post Title: {blog_title}
Social Media Message: {message_text}

Create a concise, visual image generation prompt (max 100 words) that:
1. Captures the core concept from the message
2. Is professional and business-appropriate
3. Works well for social media (LinkedIn/Twitter)
4. Avoids text/words in the image
5. Uses metaphors or visual concepts
6. Specifies professional, modern style

Return ONLY the image prompt, nothing else."""

            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            image_prompt = response.content[0].text.strip()
            return image_prompt
        
        except Exception as e:
            print(f"Error creating image prompt: {e}")
            # Fallback to simple prompt
            return f"Professional illustration representing: {blog_title}"
    
    def generate_image(self, prompt: str) -> Optional[str]:
        """
        Generate an image using xAI Grok API.
        
        Args:
            prompt: Image generation prompt
            
        Returns:
            URL of generated image, or None if failed
        """
        if not self.api_key:
            print("Warning: XAI_API_KEY not configured, skipping image generation")
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.IMAGE_MODEL,
                "prompt": prompt,
                "n": 1,  # Generate 1 image
                "response_format": "b64_json"  # Get base64 encoded image
            }
            
            response = requests.post(
                f"{self.XAI_API_BASE}/images/generations",
                headers=headers,
                json=data,
                timeout=60
            )
            
            # Check for errors
            response.raise_for_status()
            
            result = response.json()
            
            # Extract base64 image data
            if 'data' in result and len(result['data']) > 0:
                b64_data = result['data'][0]['b64_json']
                
                # Decode base64 to bytes
                image_bytes = base64.b64decode(b64_data)
                
                # Save to configured output directory with deterministic filename
                os.makedirs(Config.IMAGE_OUTPUT_DIR, exist_ok=True)
                prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()[:16]
                image_path = os.path.join(Config.IMAGE_OUTPUT_DIR, f"img_{prompt_hash}.jpg")
                with open(image_path, 'wb') as f:
                    f.write(image_bytes)
                print(f"✓ Generated image saved to: {image_path}")
                return image_path
            else:
                print(f"Warning: No image data in response: {result}")
                return None
        
        except requests.exceptions.RequestException as e:
            print(f"Error generating image: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response body: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error generating image: {e}")
            return None
    
    def download_image(self, image_url: str, save_path: str) -> bool:
        """
        Download an image from URL to local file.
        
        Args:
            image_url: URL of the image
            save_path: Path to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Downloaded image to: {save_path}")
            return True
        
        except Exception as e:
            print(f"Error downloading image: {e}")
            return False
    
    def generate_image_for_message(
        self,
        blog_title: str,
        message_text: str,
        message_id: int = None
    ) -> Optional[str]:
        """
        Complete workflow: create prompt, generate image, and optionally download.
        
        Args:
            blog_title: Blog post title
            message_text: Social media message
            message_id: Optional message ID for filename
            
        Returns:
            Image URL if successful, None otherwise
        """
        print(f"\n🎨 Generating image...")
        
        # Step 1: Create optimized prompt
        image_prompt = self.create_image_prompt(blog_title, message_text)
        print(f"Image prompt: {image_prompt[:100]}...")
        
        # Step 2: Generate image (returns local file path)
        image_path = self.generate_image(image_prompt)
        
        if not image_path:
            return None
        
        # Image is already saved to the output directory; return path
        return image_path

