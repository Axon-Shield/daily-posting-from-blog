# 🧪 Testing Guide

This guide explains how to test your automated social media posting system.

## Test Workflows

We provide two GitHub Actions workflows for testing the complete posting flow without touching your database:

### 1. Test X (Twitter) Posting

**What it does:**
- Extracts a test message using Claude
- Generates an AI image using Grok
- Posts to X (Twitter) with the image
- No database storage - pure API flow test

**How to run:**
1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Select **Test X Posting** from the left sidebar
4. Click **Run workflow** button
5. Click the green **Run workflow** button in the dropdown
6. Wait for the workflow to complete (~30 seconds)
7. Check the logs to see the complete flow

**Requirements:**
- `ANTHROPIC_API_KEY` (required)
- `XAI_API_KEY` (required for images)
- `X_API_KEY` (required)
- `X_API_SECRET` (required)
- `X_ACCESS_TOKEN` (required)
- `X_ACCESS_TOKEN_SECRET` (required)
- `X_BEARER_TOKEN` (required)

**Result:**
- A test tweet will be posted to your X account
- Will include an AI-generated image
- Logs will show each step of the process

### 2. Test LinkedIn Posting

**What it does:**
- Extracts a test message using Claude
- Generates an AI image using Grok
- Posts to LinkedIn with the image
- No database storage - pure API flow test

**How to run:**
1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Select **Test LinkedIn Posting** from the left sidebar
4. Click **Run workflow** button
5. Click the green **Run workflow** button in the dropdown
6. Wait for the workflow to complete (~30 seconds)
7. Check the logs to see the complete flow

**Requirements:**
- `ANTHROPIC_API_KEY` (required)
- `XAI_API_KEY` (required for images)
- `LINKEDIN_ACCESS_TOKEN` (required)
- `LINKEDIN_USER_ID` (required)

**Result:**
- A test post will appear on your LinkedIn profile
- Will include an AI-generated image
- Logs will show each step of the process

## Local Testing

You can also run these tests locally:

### Test X Posting Locally

```bash
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog

# Make sure your .env file has all the required keys
python test_x_post.py
```

### Test LinkedIn Posting Locally

```bash
cd /Users/dancvrcek/Documents/GitHub/daily-posting-from-blog

# Make sure your .env file has all the required keys
python test_linkedin_post.py
```

## What Gets Tested

Both test scripts verify the complete end-to-end flow:

### Step 1: Content Extraction
- Calls Claude API to extract a meaningful message
- Tests the Anthropic integration
- Validates message format

### Step 2: Message Enhancement
- Optimizes the message for the target platform
- Adds appropriate formatting
- Includes test hashtags and URLs

### Step 3: Image Generation
- Creates an optimized prompt with Claude
- Calls Grok API to generate professional image
- Validates image URL
- Falls back gracefully if image generation fails

### Step 4: Platform Posting
- Uploads the image to the platform
- Creates the post with text + image
- Verifies successful posting
- Returns post ID or error details

## Test Content

The test scripts use a sample blog post about AI and automation:

```
Title: "Test: Automated Social Media with AI"
Content: Discussion of AI-powered social media management
```

This generates a relevant test message that demonstrates the system's capabilities without posting real blog content.

## Interpreting Results

### Success ✅

If the test succeeds, you'll see:
```
✅ Configuration validated
✅ Extracted message: [message text]
✅ Enhanced message: [enhanced text]
✅ Generated image: [image URL]
✅ Successfully posted to [Platform]!
🎉 TEST COMPLETED SUCCESSFULLY!
```

Your post will appear on the platform immediately.

### Failure ❌

If the test fails, check:

1. **Configuration errors:**
   - Verify all required API keys are set in GitHub Secrets
   - Check that keys are valid and not expired

2. **API errors:**
   - Review error messages in the logs
   - Check API rate limits
   - Verify API permissions

3. **Image generation issues:**
   - System will fall back to text-only posting
   - Check `XAI_API_KEY` is valid
   - Verify Grok API is accessible

## Cost Per Test

Each test run costs approximately:
- **Claude API**: ~$0.001 (one message extraction)
- **Grok API**: ~$0.07 (one image generation)
- **Total**: ~$0.071 per test

Very affordable for thorough testing!

## Best Practices

### Before Going Live

1. **Run test workflows** to verify all integrations work
2. **Check the posted content** on each platform
3. **Verify images display correctly** 
4. **Test error handling** by temporarily removing credentials

### Periodic Testing

Run test workflows:
- After updating API credentials
- After making code changes
- Monthly to ensure APIs are still working
- Before adding a new blog post

### What NOT to Test

These workflows are for API testing only. They **do not** test:
- Database operations (use `python main.py --status` for that)
- Scheduling logic (use `python main.py --fetch-posts` for that)
- RSS feed parsing (use `python main.py --fetch-posts` for that)

## Troubleshooting

### "X API credentials not configured"

Add the missing secrets to your GitHub repository:
1. Go to Settings → Secrets and variables → Actions
2. Add the required secrets
3. Re-run the workflow

### "Image generation failed"

This is usually fine - the post will still be created without an image. Check:
- `XAI_API_KEY` is set correctly
- Grok API has sufficient credits
- Network connectivity is stable

### "Failed to post to [Platform]"

Common issues:
- **LinkedIn**: Access token expired (need to refresh)
- **X**: Rate limit exceeded (wait 15 minutes)
- **Both**: Invalid credentials or revoked access

## Advanced: Customizing Tests

You can modify the test scripts to use your own content:

```python
# In test_x_post.py or test_linkedin_post.py
test_blog_title = "Your Custom Title"
test_blog_content = """
Your custom blog content here...
"""
```

Commit and push the changes, then run the workflow again.

## Next Steps

After successful testing:
1. ✅ Confirm all platforms work correctly
2. ✅ Verify images are generated and posted
3. ✅ Check post formatting looks good
4. ✅ Enable automated scheduling workflows
5. ✅ Let the system run automatically!

## Support

If tests continue to fail after checking the above:
1. Review the complete workflow logs in GitHub Actions
2. Run tests locally with detailed error output
3. Check API status pages for outages
4. Review the setup guide for credential configuration

