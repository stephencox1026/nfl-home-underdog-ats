# Mobile Website for NFL Analysis

A mobile-friendly website version of the NFL Home Underdog Analysis that you can share with friends.

## Quick Start

1. **Generate the website:**
   ```bash
   python generate_website.py
   ```

2. **Start the local server:**
   ```bash
   python serve_website.py
   ```

3. **View on your computer:**
   - Open: http://localhost:8000/mobile_website.html

## Sharing with Friends

### Option 1: Same WiFi Network (Easiest)
1. Find your local IP address:
   - Mac/Linux: Run `ifconfig` and look for your IP (usually starts with 192.168.x.x)
   - Windows: Run `ipconfig` and look for IPv4 Address
   
2. Start the server: `python serve_website.py`
3. Share this URL with friends on the same WiFi:
   ```
   http://YOUR_IP:8000/mobile_website.html
   ```
   Replace `YOUR_IP` with your actual IP address.

### Option 2: Using ngrok (Share from anywhere)
1. Install ngrok: https://ngrok.com/download
2. Start the server: `python serve_website.py`
3. In a new terminal, run: `ngrok http 8000`
4. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)
5. Share: `https://abc123.ngrok.io/mobile_website.html`

### Option 3: Upload to Free Hosting
1. Generate the website: `python generate_website.py`
2. Upload `outputs/mobile_website.html` to:
   - **Netlify**: Drag and drop the file at https://app.netlify.com/drop
   - **Vercel**: Use their CLI or web interface
   - **GitHub Pages**: Push to a GitHub repo and enable Pages
   - **Surge.sh**: `surge outputs/mobile_website.html`

## Features

- ✅ Mobile-responsive design
- ✅ All seasons displayed
- ✅ Expandable game tables
- ✅ Color-coded results (green for covers, red for losses)
- ✅ Richard Sondgroth ad for 2024 season
- ✅ Works on all devices (phone, tablet, desktop)

## Files

- `generate_website.py` - Generates the HTML website from CSV data
- `serve_website.py` - Simple local HTTP server
- `outputs/mobile_website.html` - The generated website (created after running generate_website.py)

