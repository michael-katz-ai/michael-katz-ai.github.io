#!/bin/bash
# Simple script to serve the website locally

echo "Starting local web server..."
echo "Open your browser to: http://localhost:8000/publications.html"
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m http.server 8000
