# AI-Powered Image Generation

## Overview

The system now integrates **xAI's Grok API** to automatically generate professional images for each social media post. This enhancement makes your posts more engaging and visually appealing.

## Features

### 🎨 Automatic Image Creation
- Generates unique images for every social media message
- Uses Claude to create optimized prompts from your blog content
- Images are tailored to the specific message being posted

### 📱 Platform Integration
- Images automatically attached to **LinkedIn** posts
- Images automatically attached to **X (Twitter)** posts
- Falls back to text-only posting if image generation fails

### 💾 Image Storage
- Image URLs stored in database with each message
- Optional local backup of images to `./data/images/`
- Images persist in Grok's CDN for posting

## How It Works

### 1. Prompt Generation
When extracting messages from a blog post, the system:
1. Analyzes the blog title and message content
2. Uses Claude Sonnet 4.5 to create an optimized image prompt
3. Ensures prompts are professional and business-appropriate

Example prompt creation:
```
Blog Title: "Advanced Threat Detection with AI"
Message: "Machine learning can identify zero-day exploits 10x faster than traditional methods"

Generated Prompt: "Professional minimalist illustration of AI neural network analyzing digital security threats, modern tech style, dark blue and cyan colors, clean abstract design representing cybersecurity defense"
```

### 2. Image Generation
The system calls xAI's Grok API:
- **Model**: `grok-2-image-1212`
- **Format**: JPG
- **Cost**: $0.07 per image
- **Speed**: ~5-10 seconds per generation

### 3. Platform Posting
When posting to social media:
- **LinkedIn**: Uploads image using LinkedIn's media API
- **X (Twitter)**: Uploads image using Twitter API v1.1
- Both platforms attach the image to the post

## Configuration

### Environment Variables

```bash
# xAI Grok API key from https://x.ai/api
XAI_API_KEY=your_xai_api_key_here

# Enable/disable image generation (default: true)
GENERATE_IMAGES=true
```

### Getting xAI API Access

1. Visit [https://x.ai/api](https://x.ai/api)
2. Sign up for API access
3. Get your API key
4. Add to GitHub Secrets as `XAI_API_KEY`

### Costs

With 5 messages per blog post:
- **Per blog post**: $0.35 (5 images × $0.07)
- **Per month** (4 posts): $1.40
- **Per year**: ~$17

Very affordable for high-quality, custom images!

## Database Schema

The `posted_messages` table now includes:

```sql
CREATE TABLE posted_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    blog_post_id INTEGER NOT NULL,
    message_index INTEGER NOT NULL,
    message_text TEXT NOT NULL,
    image_url TEXT,  -- NEW: URL of generated image
    scheduled_for TEXT,
    posted_to_linkedin BOOLEAN DEFAULT 0,
    posted_to_x BOOLEAN DEFAULT 0,
    posted_at TEXT,
    ...
);
```

## Workflow

### When Fetching Posts (Daily)

```
1. Fetch blog post from RSS feed
2. Extract N messages with Claude
3. For each message:
   a. Generate optimized image prompt with Claude
   b. Call Grok API to create image
   c. Store image URL in database
   d. Optionally download image for backup
4. Schedule messages across business days
```

### When Posting (Daily)

```
1. Get next scheduled message
2. Retrieve associated image URL
3. Post to LinkedIn:
   a. Upload image to LinkedIn
   b. Create post with text + image
4. Post to X:
   a. Upload image to Twitter
   b. Create tweet with text + image
5. Mark as posted
```

## Disabling Images

If you want to disable image generation:

```bash
# In .env or GitHub Secrets
GENERATE_IMAGES=false
```

Or remove the `XAI_API_KEY` - the system will gracefully fall back to text-only posts.

## Error Handling

The system is robust and handles failures gracefully:

- **Image generation fails**: Posts without image (text-only)
- **Image upload fails**: Posts without image (text-only)
- **API rate limits**: Respects rate limits, retries if needed
- **Network errors**: Logs error, continues with next message

## Image Quality

Generated images are:
- ✅ Professional and business-appropriate
- ✅ Relevant to the message content
- ✅ Modern and visually appealing
- ✅ Optimized for social media dimensions
- ✅ Metaphorical/conceptual (no text in images)

## Migration

To enable image generation on existing database:

```bash
python database_migration_images.py
```

This adds the `image_url` column to the `posted_messages` table.

## Examples

### Cybersecurity Blog Post

**Message**: "Multi-factor authentication reduces breach risk by 99.9%"

**Generated Image**: Modern illustration of layered security shields with binary code background, professional blue gradient, symbolizing defense layers

### AI/ML Blog Post

**Message**: "Neural networks can process 1 million data points per second"

**Generated Image**: Abstract visualization of interconnected nodes with data flowing through them, tech-focused color scheme, representing neural network architecture

## Troubleshooting

### Images Not Generating

1. Check `XAI_API_KEY` is set correctly
2. Verify `GENERATE_IMAGES=true`
3. Check logs for error messages
4. Ensure account has API credits

### Images Not Posting

1. Verify LinkedIn/X credentials are valid
2. Check platform API permissions include media upload
3. Review error logs in GitHub Actions

### Image URLs Expired

Grok's CDN URLs should persist, but if they expire:
- System stores URLs, not binary data
- Consider enabling local backup in `./data/images/`
- Re-run fetch to generate new images

## Future Enhancements

Potential improvements:
- [ ] Custom image styles per blog category
- [ ] A/B testing different image styles
- [ ] Analytics on posts with/without images
- [ ] Watermarking or branding options
- [ ] Multiple images per post option

