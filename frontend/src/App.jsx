import { useState, useRef, useEffect } from 'react';

// API URL - update this with your backend URL when deploying
const API_URL = 'http://localhost:8000';

export default function App() {
  const [stage, setStage] = useState('captcha'); // 'captcha', 'drawing', 'final'
  const [captchaImage, setCaptchaImage] = useState('');
  const [isDrawing, setIsDrawing] = useState(false);
  const [loading, setLoading] = useState(false);
  const canvasRef = useRef(null);
  const videoRef = useRef(null);

  // Generate CAPTCHA on mount
  useEffect(() => {
    generateCaptcha();
  }, []);

  const generateCaptcha = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/generate-captcha`, {
        credentials: 'include' // Important for sessions!
      });
      const data = await response.json();
      
      if (data.success) {
        setCaptchaImage(data.image);
      } else {
        alert('Error generating CAPTCHA: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error generating CAPTCHA:', error);
      alert('Failed to connect to server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const startDrawing = (e) => {
    setIsDrawing(true);
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    ctx.beginPath();
    ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
  };

  const draw = (e) => {
    if (!isDrawing) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 5;
    ctx.lineCap = 'round';
    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  };

  const submitDrawing = async () => {
    const canvas = canvasRef.current;
    setLoading(true);
    
    // Convert canvas to blob
    canvas.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append('file', blob, 'drawing.png');
      
      try {
        const response = await fetch(`${API_URL}/api/validate-drawing`, {
          method: 'POST',
          body: formData,
          credentials: 'include' // Important for sessions!
        });
        
        const data = await response.json();
        
        if (data.success) {
          alert('Validation Passed! Proceeding to final stage...');
          setStage('final');
        } else {
          alert(data.message || 'Validation failed. Please try again.');
        }
      } catch (error) {
        console.error('Error validating drawing:', error);
        alert('Error validating drawing. Please try again.');
      } finally {
        setLoading(false);
      }
    });
  };

  const startVideoChallenge = async () => {
  try {
    // Get webcam access
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { width: 640, height: 480 } 
    });
    
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
    }

    // Create WebSocket connection
    const ws = new WebSocket('ws://localhost:8000/ws/hand-gesture');
    
    // Canvas for capturing frames
    const canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext('2d');
    
    // State for displaying results
    let statusText = 'Initializing...';
    let statusColor = 'gray';
    let cycleCount = 0;
    let isSuccess = false;
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      
      // Send frames at 10 FPS
      const frameInterval = setInterval(() => {
        if (videoRef.current && videoRef.current.readyState === 4) {
          // Draw video frame to canvas
          ctx.drawImage(videoRef.current, 0, 0, 640, 480);
          
          // Convert to base64
          const frameData = canvas.toDataURL('image/jpeg', 0.8);
          
          // Send to backend
          ws.send(JSON.stringify({ frame: frameData }));
        }
      }, 100); // 10 FPS
      
      // Store interval ID to clear later
      ws.frameInterval = frameInterval;
    };
    
    ws.onmessage = (event) => {
      const result = JSON.parse(event.data);
      
      statusText = result.text || 'Processing...';
      statusColor = result.color || 'gray';
      cycleCount = result.cycle_count || 0;
      
      // Update UI (you can add a state variable to display this)
      console.log(`Status: ${statusText}, Cycles: ${cycleCount}`);
      
      if (result.success && !isSuccess) {
        isSuccess = true;
        
        // Show success after 3 seconds
        setTimeout(() => {
          ws.close();
          clearInterval(ws.frameInterval);
          stream.getTracks().forEach(track => track.stop());
          alert('🎊 Challenge Completed! 🎊\n\nYou are amazing!');
          setStage('captcha');
          generateCaptcha();
        }, 3000);
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      alert('Connection error. Make sure the backend is running.');
    };
    
    ws.onclose = () => {
      console.log('WebSocket closed');
      if (ws.frameInterval) {
        clearInterval(ws.frameInterval);
      }
    };
    
  } catch (error) {
    console.error('Error accessing webcam:', error);
    alert('Please allow camera access to continue');
  }
};

  // CAPTCHA Screen
  if (stage === 'captcha') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-2xl p-8 max-w-2xl w-full">
          <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
            CAPTCHA Challenge
          </h1>
          
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-purple-600 mb-3">Instructions:</h2>
            <ol className="space-y-2 text-sm text-gray-700">
              <li>1. Look at the CAPTCHA text displayed in the image below</li>
              <li>2. Click 'Start Drawing' to open the canvas</li>
              <li>3. Write the CAPTCHA text on the black canvas</li>
              <li>4. Click 'Submit Answer' to validate your writing</li>
            </ol>
          </div>
          
          <div className="text-center mb-6">
            <h3 className="text-xl font-semibold mb-4">Your CAPTCHA:</h3>
            {loading ? (
              <div className="animate-pulse bg-gray-200 h-48 rounded-lg flex items-center justify-center">
                <p className="text-gray-500">Loading CAPTCHA...</p>
              </div>
            ) : captchaImage ? (
              <img 
                src={captchaImage} 
                alt="CAPTCHA" 
                className="mx-auto border-4 border-gray-300 rounded-lg shadow-md max-w-full"
              />
            ) : (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                Failed to load CAPTCHA. Please refresh.
              </div>
            )}
          </div>
          
          <div className="flex gap-4">
            <button
              onClick={generateCaptcha}
              disabled={loading}
              className="flex-1 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white font-bold py-3 px-6 rounded-lg transition duration-200"
            >
              {loading ? 'Loading...' : 'Refresh CAPTCHA'}
            </button>
            <button
              onClick={() => setStage('drawing')}
              disabled={!captchaImage || loading}
              className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white font-bold py-3 px-6 rounded-lg transition duration-200 transform hover:scale-105"
            >
              Start Drawing
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Drawing Screen
  if (stage === 'drawing') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-500 to-indigo-600 p-4">
        <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-2xl p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* CAPTCHA Reference */}
            <div className="lg:col-span-1">
              <h3 className="text-lg font-semibold mb-3 text-purple-600">Reference CAPTCHA:</h3>
              <img 
                src={captchaImage} 
                alt="CAPTCHA Reference" 
                className="w-full border-2 border-gray-300 rounded-lg"
              />
              <button
                onClick={() => setStage('captcha')}
                className="w-full mt-4 bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded-lg transition duration-200"
              >
                ← Back
              </button>
            </div>
            
            {/* Drawing Canvas */}
            <div className="lg:col-span-2">
              <h2 className="text-2xl font-bold mb-4 text-gray-800">
                Draw the CAPTCHA text here:
              </h2>
              
              <canvas
                ref={canvasRef}
                width={700}
                height={400}
                onMouseDown={startDrawing}
                onMouseMove={draw}
                onMouseUp={stopDrawing}
                onMouseLeave={stopDrawing}
                className="border-4 border-gray-800 rounded-lg cursor-crosshair bg-black w-full"
                style={{ touchAction: 'none' }}
              />
              
              <div className="flex gap-4 mt-6">
                <button
                  onClick={clearCanvas}
                  disabled={loading}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white font-bold py-3 px-6 rounded-lg transition duration-200"
                >
                  Clear
                </button>
                <button
                  onClick={submitDrawing}
                  disabled={loading}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-bold py-3 px-6 rounded-lg transition duration-200"
                >
                  {loading ? 'Validating...' : 'Submit Answer'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Final Challenge Screen
  if (stage === 'final') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-2xl p-8 max-w-2xl w-full">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🎉</div>
            <h1 className="text-4xl font-bold text-pink-600 mb-2">Congratulations!</h1>
            <p className="text-gray-600">You've passed the CAPTCHA challenge!</p>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-pink-600 mb-4">
              Final Challenge: The 67 Hand Gesture
            </h2>
            <ol className="space-y-2 text-sm text-gray-700">
              <li>1. Click 'Start Final Challenge' below</li>
              <li>2. Allow camera access when prompted</li>
              <li>3. Place both hands flat with palms facing up</li>
              <li>4. Alternate raising left and right hands</li>
              <li>5. Complete 2 full cycles to finish</li>
            </ol>
          </div>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-yellow-800">
              Note: Your webcam will be used for hand gesture detection. This requires additional backend implementation with MediaPipe or similar.
            </p>
          </div>
          
          {videoRef.current?.srcObject ? (
            <div className="mb-6">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                className="w-full rounded-lg border-4 border-gray-300"
              />
            </div>
          ) : null}
          
          <div className="flex gap-4">
            <button
              onClick={startVideoChallenge}
              className="flex-1 bg-pink-600 hover:bg-pink-700 text-white font-bold py-3 px-6 rounded-lg transition duration-200"
            >
              Start Final Challenge
            </button>
            <button
              onClick={() => {
                setStage('captcha');
                generateCaptcha();
              }}
              className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-lg transition duration-200"
            >
              Start Over
            </button>
          </div>
        </div>
      </div>
    );
  }
}