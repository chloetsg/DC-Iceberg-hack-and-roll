# CAPTCHA Challenge - Web Deployment Guide

This guide explains how to deploy the CAPTCHA Challenge application as a web service on Vercel.

## Overview

The application has been converted from a desktop Tkinter app to a web-based application using:
- **Backend**: Flask (Python web framework)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Vercel (serverless platform)

## Project Structure

```
DC-Iceberg-hack-and-roll/
├── app.py                  # Flask backend API
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css      # Styles
│   └── js/
│       └── script.js      # Frontend logic
├── captcha_generator.py   # CAPTCHA generation logic
├── validator.py           # OCR validation logic
├── reco_main.py          # Recognition main module
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
└── .gitignore            # Git ignore rules
```

## Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Flask Server

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Deploy to Vercel

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Deploy

From the project directory:

```bash
vercel
```

Follow the prompts:
- **Set up and deploy**: Yes
- **Which scope**: Select your account
- **Link to existing project**: No
- **Project name**: dc-iceberg-captcha (or your choice)
- **Directory**: ./ (current directory)
- **Override settings**: No

### 4. Deploy to Production

```bash
vercel --prod
```

## Configuration Notes

### Vercel Limitations

1. **No Cursor Effects**: The desktop version uses AutoHotkey executables for cursor teleporting/jittering. This cannot be replicated in a web browser for security reasons. The web version notes this in the console but doesn't implement the cursor effects.

2. **Video Challenge**: The desktop version's final video challenge (hand gesture recognition) requires webcam access. This has been removed from the web version.

3. **File Size**: Vercel has deployment size limits. The EasyOCR models may be large. Consider using Vercel's Edge Functions or optimize model loading.

## Environment Variables

If needed, you can set environment variables in Vercel:

1. Go to your project in Vercel dashboard
2. Settings → Environment Variables
3. Add variables as needed

## API Endpoints

### GET `/`
Returns the main HTML page

### GET `/api/generate-captcha`
Generates a new CAPTCHA challenge

**Response**:
```json
{
  "success": true,
  "session_id": "123",
  "captcha_image": "data:image/png;base64,...",
  "captcha_text": "abc123"
}
```

### POST `/api/validate-captcha`
Validates user's handwritten CAPTCHA

**Request**:
```json
{
  "session_id": "123",
  "drawing": "data:image/png;base64,..."
}
```

**Response**:
```json
{
  "success": true,
  "validated": true,
  "expected": "abc123"
}
```

## Troubleshooting

### Build Fails
- Check that all Python dependencies are in `requirements.txt`
- Ensure Python version compatibility (use Python 3.9+)

### Large Deployment Size
- Consider using `opencv-python-headless` instead of full OpenCV
- Optimize EasyOCR model loading

### Slow Cold Starts
- Vercel serverless functions have cold start times
- Consider using Vercel's Edge Functions for faster response

## Alternative Deployment Options

### Heroku
1. Create `Procfile`:
   ```
   web: gunicorn app:app
   ```
2. Deploy with Heroku CLI

### Railway
1. Connect GitHub repository
2. Railway auto-detects Python and deploys

### Google Cloud Run
1. Create Dockerfile
2. Deploy containerized application

## Differences from Desktop Version

| Feature | Desktop | Web |
|---------|---------|-----|
| Cursor Effects | ✅ AutoHotkey | ❌ Browser security restrictions |
| Video Challenge | ✅ Webcam + MediaPipe | ❌ Removed (can be added with WebRTC) |
| CAPTCHA Validation | ✅ | ✅ |
| Drawing Canvas | ✅ Tkinter | ✅ HTML Canvas |
| Real-time | ✅ | ✅ |

## Future Enhancements

1. **Add WebRTC** for video challenge
2. **Implement sessions** with Redis for production
3. **Add rate limiting** to prevent abuse
4. **Optimize model loading** for faster responses
5. **Add progress indicators** for better UX

## Support

For issues or questions, please open an issue on GitHub.
