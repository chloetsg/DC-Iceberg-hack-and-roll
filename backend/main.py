from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from captcha_generator import generate_captcha
from reco_main import validate_writing
from PIL import Image
import base64
from io import BytesIO
import tempfile
import os
import secrets

app = FastAPI()

# Add session middleware for security
app.add_middleware(
    SessionMiddleware, 
    secret_key=secrets.token_urlsafe(32)
)

# CORS - allows frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your Vercel URL in production: ["https://your-app.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "CAPTCHA API is running", "status": "ok"}

@app.get("/api/generate-captcha")
async def get_captcha(request: Request):
    """Generate and return CAPTCHA image"""
    try:
        # Use your existing generate_captcha function
        captcha_text, location, captcha_img = generate_captcha()
        
        # Store captcha text in session (secure - user can't see it)
        request.session['captcha_text'] = captcha_text
        
        # Convert PIL image to base64 string
        buffered = BytesIO()
        captcha_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "success": True,
            "image": f"data:image/png;base64,{img_str}"
        }
    except Exception as e:
        print(f"Error generating captcha: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/validate-drawing")
async def validate_drawing(
    request: Request,
    file: UploadFile = File(...)
):
    """Validate the user's drawing using EasyOCR"""
    try:
        # Get captcha text from session
        captcha_text = request.session.get('captcha_text')
        if not captcha_text:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Session expired. Please generate a new CAPTCHA."}
            )
        
        print(f"Validating against: {captcha_text}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Validate using your existing function
        success = validate_writing(tmp_path, captcha_text)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return {
            "success": success,
            "message": "Validation passed!" if success else "Validation failed. Please try again."
        }
        
    except Exception as e:
        print(f"Error validating: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/health")
async def health():
    """Health check endpoint for Render"""
    return {"status": "healthy"}

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)