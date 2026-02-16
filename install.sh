#!/bin/bash

echo "========================================"
echo "Installing Django Project Generator"
echo "========================================"
echo ""

echo "Installing package globally..."
pip install -e .

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Set up your API key:"
echo "   mkdir -p ~/.nfxinit"
echo "   cp .env.example ~/.nfxinit/.env"
echo "   nano ~/.nfxinit/.env"
echo ""
echo "2. Run from anywhere:"
echo "   NFXinit"
echo ""
echo "========================================"
