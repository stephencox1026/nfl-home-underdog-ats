# Share NFL Analysis with Friends

## Quick Start (Easiest Method)

1. **Install ngrok** (one-time setup):
   ```bash
   # Option 1: Homebrew (recommended)
   brew install ngrok/ngrok/ngrok
   
   # Option 2: Manual download
   # Visit https://ngrok.com/download
   # Download for macOS, unzip, and move to /usr/local/bin/
   ```

2. **Run the sharing script**:
   ```bash
   python share_with_friends.py
   ```

3. **Share the URL** that appears with your friends!

## What Your Friends Will See

- Mobile-friendly website
- All seasons with stats
- Expandable game tables
- Richard Sondgroth ad for 2024 season
- Works on phones, tablets, and computers

## How It Works

1. The script starts a local web server on your computer
2. Ngrok creates a secure tunnel to make it accessible from the internet
3. You get a public URL (like `https://abc123.ngrok.io`)
4. Share that URL with friends - they can access it from anywhere!

## Troubleshooting

### "ngrok: command not found"
- Install ngrok using Homebrew: `brew install ngrok/ngrok/ngrok`
- Or download from https://ngrok.com/download

### Friends can't access the URL
- Make sure the script is still running
- Check that ngrok is running (visit http://127.0.0.1:4040)
- The URL changes each time you restart ngrok (unless you have a paid account)

### Want a permanent URL?
- Sign up for a free ngrok account at https://dashboard.ngrok.com
- Get a static domain (free tier available)
- Or upload to free hosting: Netlify, Vercel, or GitHub Pages

## Alternative: Upload to Free Hosting

If you want a permanent link that doesn't require your computer to be on:

1. Generate the website:
   ```bash
   python generate_website.py
   ```

2. Upload `outputs/mobile_website.html` to:
   - **Netlify**: https://app.netlify.com/drop (drag and drop)
   - **Vercel**: Use their web interface or CLI
   - **GitHub Pages**: Push to a GitHub repo and enable Pages

