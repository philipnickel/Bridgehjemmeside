#!/bin/bash
# Local documentation development server

echo "🚀 Starting MkDocs development server..."
echo "📖 Documentation will be available at: http://127.0.0.1:8000"
echo "💡 The server will auto-reload when you edit files"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Navigate to the docs directory
cd "$(dirname "$0")/.."

# Install dependencies if needed
if ! command -v mkdocs &> /dev/null; then
    echo "Installing MkDocs dependencies..."
    pip install -r docs-requirements.txt
fi

# Add the bridge_club_management directory to PYTHONPATH
export PYTHONPATH="$PYTHONPATH:$(pwd)/../bridge_club_management"

# Start the development server
mkdocs serve