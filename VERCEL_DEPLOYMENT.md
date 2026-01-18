# Vercel Deployment Guide (250MB Limit Workaround)

## Problem
Vercel has a 250MB deployment size limit, but EasyOCR + PyTorch = ~3GB. This won't work!

## Solution: Split Architecture

Deploy in two parts:
1. **Frontend + Light Backend** → Vercel (free)
2. **OCR Microservice** → Railway/Render (free tier)

---

## Architecture

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Browser   │─────▶│  Vercel          │─────▶│  Railway/Render │
│  (User)     │      │  (Frontend+API)  │      │  (OCR Service)  │
└─────────────┘      └──────────────────┘      └─────────────────┘
                            │                           │
                            │  Generates CAPTCHA        │
                            │  Serves HTML/CSS/JS       │
                            │                           │
                            └──────────────────────────▶│
                                    Validates            │
                                    Handwriting          │
```

---

## Part 1: Deploy OCR Microservice (Railway)

### Why Railway?
- ✅ No size limits
- ✅ Free tier: 500 hours/month
- ✅ Supports large dependencies
- ✅ Easy deployment

### Steps:

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   ```bash
   # In your project directory
   railway login
   railway init
   ```

3. **Create Procfile**
   ```bash
   echo "web: gunicorn ocr_microservice:app" > Procfile
   ```

4. **Deploy**
   ```bash
   # Use the OCR service requirements
   cp requirements-ocr-service.txt requirements.txt

   # Deploy
   railway up
   ```

5. **Get Your Service URL**
   - Railway will give you a URL like: `https://your-app.railway.app`
   - Save this URL for the next step

---

## Part 2: Deploy Frontend on Vercel

### Steps:

1. **Update app_vercel.py with OCR Service URL**

   Edit `app_vercel.py`, find the `validate_with_external_api` function and update:

   ```python
   response = requests.post(
       'https://your-app.railway.app/validate',  # ← Your Railway URL
       json={
           'image': drawing_data,
           'expected': expected_text
       },
       timeout=10
   )
   ```

2. **Switch to Lightweight Requirements**
   ```bash
   cp requirements-vercel.txt requirements.txt
   ```

3. **Update vercel.json**
   ```bash
   cp vercel-config.json vercel.json
   ```

4. **Deploy to Vercel**
   ```bash
   vercel login
   vercel
   ```

5. **Set Environment Variable** (Optional)
   In Vercel dashboard → Settings → Environment Variables:
   ```
   OCR_SERVICE_URL=https://your-app.railway.app
   ```

---

## Alternative Option: Google Cloud Vision

If you want everything on Vercel, use Google Cloud Vision API:

### Setup:

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com
   - Enable Cloud Vision API
   - Create service account key (JSON file)

2. **Add to Vercel**
   - Base64 encode your service account JSON:
     ```bash
     cat service-account.json | base64
     ```
   - Add as Vercel environment variable:
     ```
     GOOGLE_APPLICATION_CREDENTIALS_BASE64=[your base64 string]
     ```

3. **Update requirements-vercel.txt**
   ```
   Flask==3.0.0
   Flask-CORS==4.0.0
   Pillow==10.1.0
   google-cloud-vision==3.4.5
   gunicorn==21.2.0
   ```

4. **Uncomment Google Vision code** in `app_vercel.py`

### Pricing:
- Free: 1,000 requests/month
- After: $1.50 per 1,000 requests

---

## Deployment Comparison

| Platform | Size Limit | Best For | Cost |
|----------|------------|----------|------|
| **Vercel** | 250MB | Frontend, Light APIs | Free |
| **Railway** | None | Heavy backends, ML | Free (500hrs/mo) |
| **Render** | None | Full-stack apps | Free (750hrs/mo) |
| **Google Cloud** | N/A | OCR as service | Pay-per-use |

---

## Recommended Setup

### For Hackathon/Demo:
```
Frontend + CAPTCHA Generation → Vercel
OCR Validation → Railway
```

### For Production:
```
Option 1: Vercel + Google Cloud Vision (scalable, pay-per-use)
Option 2: All on Railway (simpler, single deployment)
Option 3: Vercel + dedicated server (full control)
```

---

## Testing Locally

### Test OCR Microservice:
```bash
python ocr_microservice.py
# Runs on http://localhost:8080
```

### Test Vercel App:
```bash
python app_vercel.py
# Runs on http://localhost:5000
```

### Test Full Flow:
1. Start OCR service: `python ocr_microservice.py`
2. Update `app_vercel.py` with `http://localhost:8080`
3. Start frontend: `python app_vercel.py`
4. Open http://localhost:5000

---

## Environment Variables

### Vercel:
```
OCR_SERVICE_URL=https://your-ocr-service.railway.app
# or
GOOGLE_APPLICATION_CREDENTIALS_BASE64=[base64 encoded JSON]
```

### Railway (OCR Service):
```
PORT=8080
FLASK_ENV=production
```

---

## Troubleshooting

### "Deployment size exceeded"
✅ Make sure you're using `requirements-vercel.txt` (NOT the full `requirements.txt`)

### "OCR service not responding"
✅ Check Railway logs: `railway logs`
✅ Verify the URL is correct in `app_vercel.py`

### "Cold start timeout"
✅ Railway/Render free tiers sleep after inactivity
✅ First request may be slow (~30 seconds)
✅ Consider Railway Pro ($5/mo) for always-on

---

## Files Reference

| File | Purpose | Deploy To |
|------|---------|-----------|
| `app_vercel.py` | Lightweight Flask app | Vercel |
| `ocr_microservice.py` | Heavy OCR service | Railway |
| `requirements-vercel.txt` | Light dependencies | Vercel |
| `requirements-ocr-service.txt` | Full dependencies | Railway |
| `vercel-config.json` | Vercel config | Vercel |
| `Procfile` | Railway/Render config | Railway |

---

## Quick Start Commands

```bash
# Deploy OCR Service to Railway
cp requirements-ocr-service.txt requirements.txt
railway up

# Deploy Frontend to Vercel
cp requirements-vercel.txt requirements.txt
cp vercel-config.json vercel.json
vercel --prod

# Done! 🎉
```

---

## Support

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Google Cloud Vision: https://cloud.google.com/vision/docs
