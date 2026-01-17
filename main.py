import tkinter as tk
from tkinter import messagebox, Canvas
from PIL import Image, ImageTk
import subprocess
import os
from captcha_generator import generate_captcha
from reco_main import validate_writing
from video import perform_67
import cv2
import numpy as np

class CaptchaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CAPTCHA Challenge")
        self.root.geometry("900x700")
        self.root.configure(bg="#667eea")

        # Variables
        self.captcha_text = None
        self.location = None
        self.captcha_image = None
        self.cursor_process = None
        self.drawing = False
        self.last_x = 0
        self.last_y = 0

        # Initialize the main screen
        self.show_captcha_screen()

    def show_captcha_screen(self):
        """Display the CAPTCHA and instructions"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Generate CAPTCHA
        self.captcha_text, self.location, captcha_pil = generate_captcha()

        # Main frame
        main_frame = tk.Frame(self.root, bg="white", padx=30, pady=30)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Title
        title = tk.Label(main_frame, text="CAPTCHA Challenge",
                        font=("Arial", 24, "bold"), bg="white", fg="#333")
        title.pack(pady=10)

        # Instructions
        instructions_frame = tk.Frame(main_frame, bg="#f8f9fa", padx=15, pady=15)
        instructions_frame.pack(pady=15, fill=tk.X)

        inst_title = tk.Label(instructions_frame, text="Instructions:",
                             font=("Arial", 14, "bold"), bg="#f8f9fa", fg="#667eea")
        inst_title.pack(anchor="w")

        instructions = [
            "1. Look at the CAPTCHA text displayed in the image below",
            "2. Click 'Start Drawing' to open the canvas",
            "3. Write the CAPTCHA text on the black canvas",
            "4. Click 'Submit Answer' to validate your writing"
        ]

        for inst in instructions:
            label = tk.Label(instructions_frame, text=inst,
                           font=("Arial", 10), bg="#f8f9fa", fg="#333")
            label.pack(anchor="w", pady=2)

        # CAPTCHA display
        captcha_label = tk.Label(main_frame, text="Your CAPTCHA:",
                                font=("Arial", 16, "bold"), bg="white", fg="#333")
        captcha_label.pack(pady=10)

        # Convert PIL image to PhotoImage
        # Resize to fit within reasonable bounds - leave room for button
        max_width = 700
        max_height = 250  # Restrict height to ensure button is visible
        
        # Calculate ratio to fit both width and height constraints
        width_ratio = max_width / captcha_pil.width if captcha_pil.width > max_width else 1
        height_ratio = max_height / captcha_pil.height if captcha_pil.height > max_height else 1
        ratio = min(width_ratio, height_ratio)
        
        if ratio < 1:
            new_size = (int(captcha_pil.width * ratio), int(captcha_pil.height * ratio))
            captcha_pil = captcha_pil.resize(new_size, Image.Resampling.LANCZOS)

        self.captcha_photo = ImageTk.PhotoImage(captcha_pil)
        img_label = tk.Label(main_frame, image=self.captcha_photo,
                            bg="white", relief=tk.SOLID, borderwidth=3)
        img_label.pack(pady=10)

        # Start button
        start_btn = tk.Button(main_frame, text="Start Drawing",
                             font=("Arial", 14, "bold"), bg="#667eea", fg="white",
                             padx=30, pady=10, command=self.open_canvas,
                             relief=tk.RAISED, cursor="hand2")
        start_btn.pack(pady=0)

    def open_canvas(self):
        """Open the drawing canvas and start cursor effect"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main frame
        main_frame = tk.Frame(self.root, bg="white", padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Title
        title = tk.Label(main_frame, text="Draw the CAPTCHA text here:",
                        font=("Arial", 18, "bold"), bg="white", fg="#764ba2")
        title.pack(pady=10)

        # Canvas for drawing
        self.canvas = Canvas(main_frame, width=700, height=400,
                            bg="black", cursor="crosshair",
                            relief=tk.SOLID, borderwidth=3)
        self.canvas.pack(pady=10)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

        # Control buttons frame
        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(pady=15)

        clear_btn = tk.Button(btn_frame, text="Clear",
                             font=("Arial", 12, "bold"), bg="#667eea", fg="white",
                             padx=20, pady=8, command=self.clear_canvas,
                             relief=tk.RAISED, cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=10)

        submit_btn = tk.Button(btn_frame, text="Submit Answer",
                              font=("Arial", 12, "bold"), bg="#764ba2", fg="white",
                              padx=20, pady=8, command=self.submit_answer,
                              relief=tk.RAISED, cursor="hand2")
        submit_btn.pack(side=tk.LEFT, padx=10)

        # Start teleporting cursor effect
        self.start_cursor_effect()

    def start_cursor_effect(self):
        """Start the teleporting cursor executable"""
        cursor_exe_path = r'cursor\teleporting_cursor.exe'
        if os.path.exists(cursor_exe_path):
            try:
                self.cursor_process = subprocess.Popen([cursor_exe_path])
                print("Cursor effect started")
            except Exception as e:
                print(f"Failed to start cursor effect: {e}")
        else:
            print("Cursor executable not found, continuing without effect")

    def stop_cursor_effect(self):
        """Stop the teleporting cursor effect"""
        if self.cursor_process:
            try:
                self.cursor_process.terminate()
                self.cursor_process = None
                print("Cursor effect stopped")
            except Exception as e:
                print(f"Failed to stop cursor effect: {e}")

    def start_draw(self, event):
        """Start drawing on canvas"""
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y

    def draw(self, event):
        """Draw on canvas"""
        if self.drawing:
            self.canvas.create_line(self.last_x, self.last_y,
                                   event.x, event.y,
                                   fill="white", width=5,
                                   capstyle=tk.ROUND, smooth=True)
            self.last_x = event.x
            self.last_y = event.y

    def stop_draw(self, event):
        """Stop drawing"""
        self.drawing = False

    def clear_canvas(self):
        """Clear the canvas"""
        self.canvas.delete("all")

    def submit_answer(self):
        """Submit the drawing for validation"""
        # Stop cursor effect
        self.stop_cursor_effect()

        # Save canvas as image
        try:
            # Get canvas dimensions
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()

            # Create a blank image matching canvas size
            canvas_image = np.zeros((height, width, 3), dtype=np.uint8)

            # Get all canvas items and draw them on the numpy array
            for item in self.canvas.find_all():
                coords = self.canvas.coords(item)
                if len(coords) >= 4:
                    # Draw line
                    x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
                    cv2.line(canvas_image, (x1, y1), (x2, y2), (255, 255, 255), 5)

            # Save the image
            cv2.imwrite('my_drawing.png', canvas_image)

            # Validate the drawing
            success = validate_writing('my_drawing.png', self.captcha_text)

            if success:
                messagebox.showinfo("Success!", "Validation Passed!\n\nProceeding to final stage...")
                self.show_final_stage()
            else:
                messagebox.showerror("Failed", "Validation failed. Please try again.")

        except Exception as e:
            messagebox.showerror("Error", f"Error processing image: {str(e)}")
            print(f"Error details: {e}")

    def show_final_stage(self):
        """Show the final stage screen"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main frame
        main_frame = tk.Frame(self.root, bg="white", padx=40, pady=40)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        # Success icon
        success_label = tk.Label(main_frame, text="🎉",
                                font=("Arial", 80), bg="white")
        success_label.pack(pady=10)

        # Title
        title = tk.Label(main_frame, text="Congratulations!",
                        font=("Arial", 28, "bold"), bg="white", fg="#f5576c")
        title.pack(pady=10)

        subtitle = tk.Label(main_frame, text="You've passed the CAPTCHA challenge!",
                           font=("Arial", 14), bg="white", fg="#666")
        subtitle.pack(pady=5)

        # Instructions frame
        inst_frame = tk.Frame(main_frame, bg="#f8f9fa", padx=20, pady=20)
        inst_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        inst_title = tk.Label(inst_frame, text="Final Challenge: The 67 Hand Gesture",
                             font=("Arial", 16, "bold"), bg="#f8f9fa", fg="#f5576c")
        inst_title.pack(pady=10)

        instructions = [
            "1. Click the 'Start Final Challenge' button below",
            "2. Your webcam will activate - make sure you allow camera access",
            "3. Place both hands flat in front of the camera with palms facing up",
            "4. Alternate raising your left and right hands to create a '67' gesture",
            "5. Complete 2 full cycles to finish the challenge"
        ]

        for inst in instructions:
            label = tk.Label(inst_frame, text=inst,
                           font=("Arial", 11), bg="#f8f9fa", fg="#333",
                           justify=tk.LEFT)
            label.pack(anchor="w", pady=3, padx=10)

        # Note
        note_frame = tk.Frame(main_frame, bg="#fff3cd", padx=15, pady=15)
        note_frame.pack(pady=15, fill=tk.X)

        note = tk.Label(note_frame,
                       text="Note: A separate OpenCV window will open for hand gesture detection.\nFollow the on-screen instructions. Press ESC to exit.",
                       font=("Arial", 10), bg="#fff3cd", fg="#856404",
                       justify=tk.LEFT)
        note.pack()

        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg="white")
        btn_frame.pack(pady=20)

        start_btn = tk.Button(btn_frame, text="Start Final Challenge",
                             font=("Arial", 14, "bold"), bg="#f5576c", fg="white",
                             padx=30, pady=12, command=self.start_final_challenge,
                             relief=tk.RAISED, cursor="hand2")
        start_btn.pack(side=tk.LEFT, padx=10)

        restart_btn = tk.Button(btn_frame, text="Start Over",
                               font=("Arial", 14, "bold"), bg="#667eea", fg="white",
                               padx=30, pady=12, command=self.show_captcha_screen,
                               relief=tk.RAISED, cursor="hand2")
        restart_btn.pack(side=tk.LEFT, padx=10)

    def start_final_challenge(self):
        """Trigger the video.py perform_67 function"""
        try:
            # Show info message
            messagebox.showinfo("Starting Challenge",
                              "The webcam window will open now.\nComplete the 67 hand gesture challenge!")

            # Run the perform_67 function
            result = perform_67()

            if result:
                messagebox.showinfo("🎊 Success! 🎊",
                                  "Challenge Completed!\n\nYou are amazing!")
            else:
                messagebox.showwarning("Challenge Ended",
                                      "Challenge was closed.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    root = tk.Tk()
    app = CaptchaApp(root)

    # Handle window closing
    def on_closing():
        if app.cursor_process:
            app.stop_cursor_effect()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
