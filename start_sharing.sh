#!/bin/bash

# Start sharing script for NFL Analysis

cd "$(dirname "$0")"

echo "=========================================="
echo "Starting NFL Analysis Sharing..."
echo "=========================================="

# Generate website if needed
if [ ! -f "outputs/mobile_website.html" ]; then
    echo "Generating website..."
    python3 generate_website.py
fi

# Start local server in background
echo "Starting local server on port 8000..."
python3 -m http.server 8000 --directory outputs > /dev/null 2>&1 &
SERVER_PID=$!
sleep 2

# Start ngrok
echo "Starting ngrok tunnel..."
./ngrok http 8000 > /dev/null 2>&1 &
NGROK_PID=$!
sleep 5

# Get public URL
echo ""
echo "=========================================="
echo "SHARING READY!"
echo "=========================================="
echo ""

# Try to get URL from ngrok API
URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); tunnels=data.get('tunnels',[]); print(tunnels[0]['public_url'] if tunnels else '')" 2>/dev/null)

if [ -n "$URL" ]; then
    SHARE_URL="${URL}/mobile_website.html"
    echo "Share this URL with your friends:"
    echo ""
    echo "  $SHARE_URL"
    echo ""
    echo "They can open it on their phones, tablets, or computers!"
else
    echo "Ngrok is starting..."
    echo "Visit http://127.0.0.1:4040 to see your public URL"
    echo "Look for the 'Forwarding' URL and add '/mobile_website.html'"
fi

echo ""
echo "Press Ctrl+C to stop sharing..."
echo "=========================================="

# Wait for interrupt
trap "kill $SERVER_PID $NGROK_PID 2>/dev/null; exit" INT TERM
wait

