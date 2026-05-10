# 🔑 ENVIRONMENT SETUP

## .env File Template

Create a file called `.env` in your project directory with these variables:

```
# Flask Secret Key (for sessions)
SECRET_KEY=your_random_secret_key_here_make_it_long_and_random

# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here
```

## How to Get These Credentials

### 1. Google OAuth (For Sign-In with Google)

**Steps:**
1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable Google+ API
4. Go to "Credentials" → Create "OAuth 2.0 Client ID"
5. Choose "Web application"
6. Add authorized redirect URIs:
   - `http://localhost:5000/login/google/authorized`
   - `http://localhost:5000/` (if deploying, add your domain)
7. Copy Client ID and Client Secret

**Example:**
```
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdef123456
```

### 2. Gemini API Key (For AI Responses)

**Steps:**
1. Go to https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Select your project (or create new)
4. Copy the API key

**Example:**
```
GEMINI_API_KEY=AIzaSyDx_example_key_here_abcdef123456
```

### 3. Secret Key (For Flask Sessions)

**Generate a random secret:**
```bash
# Option 1: In Python terminal
python -c "import secrets; print(secrets.token_hex(32))"

# Option 2: Use any random string (minimum 32 characters recommended)
your_long_random_string_here_make_it_16_chars_minimum
```

**Example:**
```
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4
```

---

## Complete .env Example

```
# Flask Configuration
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4

# Google OAuth
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-1234567890abcdefg

# Gemini AI
GEMINI_API_KEY=AIzaSyDx1234567890abcdefghijklmn
```

---

## Testing Your Setup

After creating `.env`, test if everything loads:

```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ Env loaded'); print(f'Google ID: {os.getenv(\"GOOGLE_CLIENT_ID\")[:10]}...')"
```

---

## Deployment Notes

When deploying to production (not localhost):

1. Change redirect URI in Google OAuth settings to your domain
2. Update `.env` file with production URLs
3. Use strong SECRET_KEY
4. Never commit `.env` file to git
5. Use environment variables from hosting platform instead

---

## Troubleshooting

**Issue:** `ModuleNotFoundError: No module named 'dotenv'`
- **Solution:** `pip install python-dotenv`

**Issue:** `.env` file not loading
- **Solution:** Make sure `.env` is in the same directory as `app.py`

**Issue:** Google login not working
- **Solution:** Check that redirect URI in Google Console matches app URL

**Issue:** Gemini not responding
- **Solution:** Verify GEMINI_API_KEY is correct and has credits

---

## Required Environment Variables Summary

| Variable | Purpose | Where to Get |
|----------|---------|-------------|
| SECRET_KEY | Session security | Generate random string |
| GOOGLE_CLIENT_ID | Google OAuth ID | Google Console |
| GOOGLE_CLIENT_SECRET | Google OAuth secret | Google Console |
| GEMINI_API_KEY | AI responses | Google AI Studio |

Once `.env` is set up, run:
```bash
python.exe app.py
```

That's it! Your Justin AI app is ready to use.
