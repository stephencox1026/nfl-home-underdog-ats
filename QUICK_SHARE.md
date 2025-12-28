# Quick Share Setup - Fix Ngrok Error

## The Issue
Ngrok v3 requires authentication. You need to set up a free account.

## Quick Fix (2 minutes)

### Step 1: Get Your Auth Token
1. Go to: https://dashboard.ngrok.com/signup
2. Sign up for a free account (takes 30 seconds)
3. After signing up, go to: https://dashboard.ngrok.com/get-started/your-authtoken
4. Copy your authtoken (looks like: `2abc123def456ghi789jkl012mno345pq_6r7s8t9u0v1w2x3y4z5`)

### Step 2: Configure Ngrok
Run this command (replace YOUR_TOKEN with your actual token):

```bash
cd "/Users/stephencox/Desktop/Cursor Projects/Project 2"
./ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Step 3: Share!
Run:
```bash
python simple_share.py
```

You'll get a URL like `https://abc123.ngrok.io/mobile_website.html` to share!

## Alternative: Manual Method

If you prefer to do it manually:

1. **Start the server:**
   ```bash
   cd "/Users/stephencox/Desktop/Cursor Projects/Project 2"
   python -m http.server 8000 --directory outputs
   ```

2. **In another terminal, start ngrok:**
   ```bash
   cd "/Users/stephencox/Desktop/Cursor Projects/Project 2"
   ./ngrok http 8000
   ```

3. **Get the URL:**
   - Visit: http://127.0.0.1:4040
   - Copy the "Forwarding" URL (starts with https://)
   - Add `/mobile_website.html` to the end
   - Share that URL!

## Still Having Issues?

The error is likely because ngrok needs authentication. The free account setup takes 2 minutes and gives you:
- Public URLs that work from anywhere
- No credit card required
- Free tier is perfect for sharing

