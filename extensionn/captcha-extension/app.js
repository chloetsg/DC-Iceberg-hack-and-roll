/**
 * CaptchaApp - Main application logic for the CAPTCHA Challenge
 * This is the JavaScript equivalent of the Python main.py
 */

class CaptchaApp {
  constructor() {
    // State variables (equivalent to Python's self.xxx)
    this.captchaText = null;
    this.location = null;
    this.captchaImage = null;
    this.drawing = false;
    this.lastX = 0;
    this.lastY = 0;
    this.canvas = null;
    this.ctx = null;
    this.cursorEffectInterval = null;

    // Bind methods to maintain 'this' context
    this.startDraw = this.startDraw.bind(this);
    this.draw = this.draw.bind(this);
    this.stopDraw = this.stopDraw.bind(this);

    // Initialize keyboard shortcuts
    this.initKeyboardShortcuts();
  }

  /**
   * Initialize keyboard shortcuts (like Ctrl+B bypass)
   */
  initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey && e.key === 'b') {
        e.preventDefault();
        this.bypassCaptcha();
      }
    });
  }

  /**
   * Generate a random CAPTCHA text
   * Replace this with your actual captcha_generator.py logic
   */
  generateCaptcha() {
    // Simple random text generator - replace with your actual logic
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let captcha = '';
    const length = 5 + Math.floor(Math.random() * 3); // 5-7 characters
    
    for (let i = 0; i < length; i++) {
      captcha += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    this.captchaText = captcha;
    this.location = 'some_location'; // Set if needed
    
    return {
      text: captcha,
      location: this.location,
      image: this.createCaptchaImage(captcha)
    };
  }

  /**
   * Create a CAPTCHA image using Canvas
   * This replaces the PIL-based image generation
   */
  createCaptchaImage(text) {
    const canvas = document.createElement('canvas');
    canvas.width = 300;
    canvas.height = 100;
    const ctx = canvas.getContext('2d');

    // Background with noise
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Add noise dots
    for (let i = 0; i < 100; i++) {
      ctx.fillStyle = `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 0.3)`;
      ctx.fillRect(Math.random() * canvas.width, Math.random() * canvas.height, 2, 2);
    }

    // Add noise lines
    for (let i = 0; i < 5; i++) {
      ctx.strokeStyle = `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 0.3)`;
      ctx.beginPath();
      ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
      ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
      ctx.stroke();
    }

    // Draw text with distortion
    ctx.font = 'bold 40px Arial';
    ctx.fillStyle = '#333';
    
    // Draw each character with slight rotation and offset
    let x = 30;
    for (const char of text) {
      ctx.save();
      ctx.translate(x, 60 + (Math.random() - 0.5) * 10);
      ctx.rotate((Math.random() - 0.5) * 0.3);
      ctx.fillText(char, 0, 0);
      ctx.restore();
      x += 35 + (Math.random() - 0.5) * 10;
    }

    return canvas.toDataURL('image/png');
  }

  /**
   * Show the main CAPTCHA screen
   * Equivalent to show_captcha_screen() in Python
   */
  showCaptchaScreen() {
    const container = document.getElementById('app-container');
    
    // Generate new CAPTCHA
    const captcha = this.generateCaptcha();

    container.innerHTML = `
      <div class="main-frame">
        <h1 class="title">CAPTCHA Challenge</h1>
        
        <div class="instructions-frame">
          <h3 class="instructions-title">Instructions:</h3>
          <p>1. Look at the CAPTCHA text displayed in the image below</p>
          <p>2. Click 'Start Drawing' to open the canvas</p>
          <p>3. Write the CAPTCHA text on the black canvas</p>
          <p>4. Click 'Submit Answer' to validate your writing</p>
        </div>

        <h2 class="captcha-label">Your CAPTCHA:</h2>
        <div class="captcha-display">
          <img src="${captcha.image}" alt="CAPTCHA" class="captcha-image">
        </div>

        <button id="start-btn" class="btn btn-primary">Start Drawing</button>
      </div>
    `;

    // Attach event listener
    document.getElementById('start-btn').addEventListener('click', () => this.openCanvas());
  }

  /**
   * Open the drawing canvas
   * Equivalent to open_canvas() in Python
   */
  openCanvas() {
    const container = document.getElementById('app-container');
    const captchaImage = this.createCaptchaImage(this.captchaText);

    container.innerHTML = `
      <div class="main-frame">
        <div class="captcha-section">
          <h3 class="reference-title">Reference CAPTCHA:</h3>
          <img src="${captchaImage}" alt="CAPTCHA" class="captcha-image-small">
        </div>

        <h2 class="draw-title">Draw the CAPTCHA text here:</h2>
        
        <canvas id="drawing-canvas" width="500" height="250"></canvas>

        <div class="button-frame">
          <button id="clear-btn" class="btn btn-secondary">Clear</button>
          <button id="submit-btn" class="btn btn-primary">Submit Answer</button>
        </div>
      </div>
    `;

    // Setup canvas
    this.canvas = document.getElementById('drawing-canvas');
    this.ctx = this.canvas.getContext('2d');
    
    // Set canvas background to black
    this.ctx.fillStyle = 'black';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Setup drawing style
    this.ctx.strokeStyle = 'white';
    this.ctx.lineWidth = 5;
    this.ctx.lineCap = 'round';
    this.ctx.lineJoin = 'round';

    // Bind canvas events
    this.canvas.addEventListener('mousedown', this.startDraw);
    this.canvas.addEventListener('mousemove', this.draw);
    this.canvas.addEventListener('mouseup', this.stopDraw);
    this.canvas.addEventListener('mouseout', this.stopDraw);

    // Touch support for mobile
    this.canvas.addEventListener('touchstart', (e) => {
      e.preventDefault();
      const touch = e.touches[0];
      const rect = this.canvas.getBoundingClientRect();
      this.startDraw({
        offsetX: touch.clientX - rect.left,
        offsetY: touch.clientY - rect.top
      });
    });

    this.canvas.addEventListener('touchmove', (e) => {
      e.preventDefault();
      const touch = e.touches[0];
      const rect = this.canvas.getBoundingClientRect();
      this.draw({
        offsetX: touch.clientX - rect.left,
        offsetY: touch.clientY - rect.top
      });
    });

    this.canvas.addEventListener('touchend', this.stopDraw);

    // Bind button events
    document.getElementById('clear-btn').addEventListener('click', () => this.clearCanvas());
    document.getElementById('submit-btn').addEventListener('click', () => this.submitAnswer());

    // Start cursor effect (if you want to implement it)
    setTimeout(() => this.startCursorEffect(), 500);
  }

  /**
   * Start drawing on canvas
   */
  startDraw(e) {
    this.drawing = true;
    this.lastX = e.offsetX;
    this.lastY = e.offsetY;
  }

  /**
   * Draw on canvas
   */
  draw(e) {
    if (!this.drawing) return;

    this.ctx.beginPath();
    this.ctx.moveTo(this.lastX, this.lastY);
    this.ctx.lineTo(e.offsetX, e.offsetY);
    this.ctx.stroke();

    this.lastX = e.offsetX;
    this.lastY = e.offsetY;
  }

  /**
   * Stop drawing
   */
  stopDraw() {
    this.drawing = false;
  }

  /**
   * Clear the canvas
   */
  clearCanvas() {
    this.ctx.fillStyle = 'black';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  /**
   * Get canvas image data for validation
   */
  getCanvasImageData() {
    return this.canvas.toDataURL('image/png');
  }

  /**
   * Submit the drawing for validation
   * Equivalent to submit_answer() in Python
   */
  async submitAnswer() {
    // Stop cursor effect
    this.stopCursorEffect();

    try {
      console.log(`Validating against captcha text: ${this.captchaText}`);

      // Get canvas image data
      const imageData = this.getCanvasImageData();

      // Check if canvas is empty (mostly black)
      const isEmpty = this.isCanvasEmpty();
      if (isEmpty) {
        this.showMessage('warning', 'Empty Canvas', 'Please draw something before submitting!');
        return;
      }

      // Show loading
      this.showMessage('info', 'Validating...', 'Please wait while we validate your handwriting...');

      // Validate the drawing
      // Replace this with your actual validation logic (e.g., API call to a server running reco_main.py)
      const success = await this.validateWriting(imageData, this.captchaText);

      console.log(`Validation result: ${success}`);

      if (success) {
        this.showMessage('success', 'Success!', 'CAPTCHA Passed!\n\nStarting final challenge...');
        
        // Trigger next challenge (equivalent to perform_67())
        const result = await this.perform67();

        if (result) {
          this.showMessage('success', '🎊 Congratulations! 🎊', 'You completed all challenges!');
        }

        // Return to start screen after a delay
        setTimeout(() => this.showCaptchaScreen(), 2000);
      } else {
        this.showMessage('error', 'Failed', 'Validation failed. Please try again.\n\nMake sure to write clearly!');
        // Restart cursor effect
        this.startCursorEffect();
      }

    } catch (error) {
      this.showMessage('error', 'Error', `Error processing image: ${error.message}`);
      console.error('Error details:', error);
    }
  }

  /**
   * Check if canvas is empty (mostly black)
   */
  isCanvasEmpty() {
    const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
    const data = imageData.data;
    let whitePixels = 0;

    for (let i = 0; i < data.length; i += 4) {
      // Check if pixel is white-ish (drawn)
      if (data[i] > 200 && data[i + 1] > 200 && data[i + 2] > 200) {
        whitePixels++;
      }
    }

    // If less than 0.1% white pixels, consider it empty
    return whitePixels < (this.canvas.width * this.canvas.height * 0.001);
  }

  /**
   * Validate the handwriting against expected text
   * Replace this with your actual validation logic
   * 
   * OPTIONS:
   * 1. Use Tesseract.js for OCR in the browser
   * 2. Send to a backend server running your Python validation
   * 3. Use a cloud OCR API (Google Vision, AWS Textract, etc.)
   */
  async validateWriting(imageData, expectedText) {
    // OPTION 1: Simple placeholder - always returns true after delay
    // Replace with actual implementation
    
    return new Promise((resolve) => {
      setTimeout(() => {
        // Placeholder: randomly pass/fail for testing
        // Replace with actual OCR validation
        const success = Math.random() > 0.3; // 70% success rate for testing
        resolve(success);
      }, 1500);
    });

    // OPTION 2: Use Tesseract.js (uncomment and add tesseract.js to your extension)
    /*
    const Tesseract = window.Tesseract;
    const result = await Tesseract.recognize(imageData, 'eng');
    const recognizedText = result.data.text.trim().toUpperCase().replace(/\s/g, '');
    return recognizedText === expectedText.toUpperCase();
    */

    // OPTION 3: Send to backend API
    /*
    const response = await fetch('YOUR_API_ENDPOINT/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image: imageData,
        expected: expectedText
      })
    });
    const result = await response.json();
    return result.success;
    */
  }

  /**
   * Perform the "67" challenge
   * Equivalent to perform_67() in Python
   * 
   * NOTE: The original uses webcam and hand gestures via OpenCV
   * For a Chrome extension, you could:
   * 1. Use the MediaPipe Hands library in JavaScript
   * 2. Use a simpler challenge type
   */
  async perform67() {
    return new Promise((resolve) => {
      // Placeholder: Show a simple challenge
      // Replace with actual gesture detection using MediaPipe if needed
      
      const container = document.getElementById('app-container');
      container.innerHTML = `
        <div class="main-frame challenge-67">
          <h1>🎯 Final Challenge</h1>
          <p>Make a "67" gesture with your hand!</p>
          <p class="hint">(This is a placeholder - implement MediaPipe for actual gesture detection)</p>
          <button id="complete-btn" class="btn btn-primary">Complete Challenge</button>
          <button id="skip-btn" class="btn btn-secondary">Skip</button>
        </div>
      `;

      document.getElementById('complete-btn').addEventListener('click', () => resolve(true));
      document.getElementById('skip-btn').addEventListener('click', () => resolve(false));
    });
  }

  /**
   * Bypass CAPTCHA (Ctrl+B)
   */
  bypassCaptcha() {
    this.stopCursorEffect();
    console.log('CAPTCHA bypassed via Ctrl+B');
    
    this.perform67().then((result) => {
      if (result) {
        this.showMessage('success', '🎊 Congratulations! 🎊', 'You completed all challenges!');
      }
      setTimeout(() => this.showCaptchaScreen(), 2000);
    });
  }

  /**
   * Start cursor effect
   * NOTE: Chrome extensions cannot control the system cursor like the Python version
   * This is a visual-only effect within the extension popup
   */
  startCursorEffect() {
    console.log('Starting cursor effect (visual only in extension)');
    
    // Create cursor effect overlay if it doesn't exist
    if (!document.getElementById('cursor-effect')) {
      const overlay = document.createElement('div');
      overlay.id = 'cursor-effect';
      overlay.style.cssText = `
        position: fixed;
        width: 20px;
        height: 20px;
        background: rgba(102, 126, 234, 0.5);
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        display: none;
      `;
      document.body.appendChild(overlay);
    }

    const effect = document.getElementById('cursor-effect');
    effect.style.display = 'block';

    // Teleport the visual effect randomly
    this.cursorEffectInterval = setInterval(() => {
      const x = Math.random() * (window.innerWidth - 20);
      const y = Math.random() * (window.innerHeight - 20);
      effect.style.left = `${x}px`;
      effect.style.top = `${y}px`;
    }, 1500);
  }

  /**
   * Stop cursor effect
   */
  stopCursorEffect() {
    if (this.cursorEffectInterval) {
      clearInterval(this.cursorEffectInterval);
      this.cursorEffectInterval = null;
    }
    
    const effect = document.getElementById('cursor-effect');
    if (effect) {
      effect.style.display = 'none';
    }
    
    console.log('Cursor effect stopped');
  }

  /**
   * Show a message to the user
   * Equivalent to messagebox.showinfo/showerror/showwarning
   */
  showMessage(type, title, message) {
    // Remove existing message
    const existing = document.getElementById('message-modal');
    if (existing) existing.remove();

    const colors = {
      success: '#28a745',
      error: '#dc3545',
      warning: '#ffc107',
      info: '#667eea'
    };

    const modal = document.createElement('div');
    modal.id = 'message-modal';
    modal.innerHTML = `
      <div class="modal-overlay">
        <div class="modal-content">
          <div class="modal-header" style="background: ${colors[type]}">
            <h3>${title}</h3>
          </div>
          <div class="modal-body">
            <p>${message.replace(/\n/g, '<br>')}</p>
          </div>
          <div class="modal-footer">
            <button class="btn btn-primary modal-close">OK</button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Close on button click or overlay click
    modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
    modal.querySelector('.modal-overlay').addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay')) {
        modal.remove();
      }
    });

    // Auto-close info messages after 2 seconds
    if (type === 'info') {
      setTimeout(() => {
        if (document.getElementById('message-modal')) {
          modal.remove();
        }
      }, 2000);
    }
  }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new CaptchaApp();
  app.showCaptchaScreen();
  
  // Make app accessible globally for debugging
  window.captchaApp = app;
});
