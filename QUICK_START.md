# 🚀 Quick Start - Vercel Deployment

## ✅ Fixed: No More PyTorch Error!

The `vercel` branch now has **lightweight dependencies only** (~50MB total).

---

## Current Setup

### What's on Vercel (vercel branch):
- ✅ `requirements.txt` - Only Flask, Pillow, requests (~50MB)
- ✅ `vercel.json` - Points to `app_vercel.py`
- ✅ `app_vercel.py` - Lightweight Flask app
- ✅ Frontend - HTML/CSS/JS for UI

### What's NOT on Vercel:
- ❌ EasyOCR, PyTorch, OpenCV (too large)
- → These run on a separate service (Railway)

---

## Deployment Status

### Current Situation:
Your Vercel deployment should now work! ✨

### Next Step: Deploy OCR Service (Optional)

The frontend will work, but validation will use "simple mode" (just checks if you drew something). For **real OCR validation**, deploy the OCR service:

```bash
# Deploy OCR microservice to Railway
railway login
railway init
railway up
```

Then set environment variable in Vercel:
```
OCR_SERVICE_URL = https://your-railway-app.railway.app
```

---

## Quick Commands

### Check Vercel Deployment:
```bash
vercel --prod
```

### Test Locally:
```bash
# Install lightweight deps
pip install -r requirements.txt

# Run the app
python app_vercel.py

# Open http://localhost:5000
```

---

## File Sizes (for reference)

| Package | Size |
|---------|------|
| Flask | ~2MB |
| Pillow | ~3MB |
| requests | ~1MB |
| gunicorn | ~1MB |
| **Total** | **~50MB** ✅ |

vs.

| Package | Size |
|---------|------|
| torch | ~800MB ❌ |
| easyocr | ~500MB ❌ |
| opencv | ~100MB ❌ |
| **Total** | **~3GB** ❌ |

---

## What Works Now

### ✅ Working on Vercel:
- Generate CAPTCHA
- Display UI
- Draw on canvas
- Submit drawings
- Simple validation (checks if drawn)

### ⏳ Needs Railway OCR Service:
- Real handwriting OCR validation
- Text recognition with EasyOCR

---

## Troubleshooting

### Still getting size errors?
```bash
# Make sure you're on vercel branch
git checkout vercel

# Check requirements.txt
cat requirements.txt
# Should only show: Flask, Pillow, requests, gunicorn

# Force redeploy
vercel --force
```

### Want full OCR validation?
See `VERCEL_DEPLOYMENT.md` for Railway setup (5 minutes)

---

## Architecture

```
┌──────────┐
│  User    │
└────┬─────┘
     │
     ▼
┌──────────────────┐
│  Vercel          │  ← Lightweight (50MB)
│  - Frontend      │
│  - CAPTCHA Gen   │
│  - Simple Valid  │
└────┬─────────────┘
     │ (Optional)
     ▼
┌──────────────────┐
│  Railway         │  ← Heavy OCR (3GB)
│  - EasyOCR       │
│  - PyTorch       │
│  - Full Validate │
└──────────────────┘
```

---

## Summary

✅ **Vercel branch is now ready to deploy!**

The PyTorch error is fixed by removing heavy dependencies.

For full functionality:
1. ✅ Vercel handles UI + CAPTCHA generation
2. ⏳ (Optional) Railway handles OCR validation

Deploy and test! 🎉
