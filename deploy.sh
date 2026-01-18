#!/bin/bash

# CAPTCHA Challenge Deployment Script

echo "🚀 CAPTCHA Challenge Deployment"
echo "================================"
echo ""

# Function to deploy OCR service
deploy_ocr() {
    echo "📦 Deploying OCR Microservice to Railway..."
    echo ""

    # Backup and use OCR requirements
    cp requirements.txt requirements.backup.txt 2>/dev/null || true
    cp requirements-ocr-service.txt requirements.txt

    echo "✓ Using heavy dependencies for OCR service"
    echo ""
    echo "Run these commands:"
    echo "  railway login"
    echo "  railway up"
    echo ""
    echo "Save your Railway URL (e.g., https://your-app.railway.app)"
    echo ""
}

# Function to deploy frontend
deploy_frontend() {
    echo "🌐 Deploying Frontend to Vercel..."
    echo ""

    # Use lightweight requirements
    cp requirements-vercel.txt requirements.txt
    cp vercel-config.json vercel.json

    echo "✓ Using lightweight dependencies for Vercel"
    echo ""
    echo "Run these commands:"
    echo "  vercel login"
    echo "  vercel"
    echo ""
    echo "Set environment variable in Vercel dashboard:"
    echo "  OCR_SERVICE_URL = https://your-app.railway.app"
    echo ""
}

# Main menu
echo "Choose deployment option:"
echo ""
echo "1) Deploy OCR Service (Railway) - Do this first!"
echo "2) Deploy Frontend (Vercel)"
echo "3) Deploy both (guided)"
echo "4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        deploy_ocr
        ;;
    2)
        deploy_frontend
        ;;
    3)
        echo ""
        echo "Step 1/2: Deploy OCR Service"
        echo "----------------------------"
        deploy_ocr
        read -p "Press Enter after Railway deployment is complete..."
        echo ""
        echo "Step 2/2: Deploy Frontend"
        echo "------------------------"
        deploy_frontend
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✨ Deployment setup complete!"
echo ""
echo "📚 For detailed instructions, see:"
echo "   - VERCEL_DEPLOYMENT.md"
echo "   - DEPLOYMENT.md"
