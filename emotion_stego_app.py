
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
import matplotlib.pyplot as plt
from deepface import DeepFace

# Global variables
cover_image_path = ""
secret_image_path = ""
secret_height = 0
secret_width = 0

def select_cover_image():
    global cover_image_path
    cover_image_path = filedialog.askopenfilename(title="Select Cover Image")
    if cover_image_path:
        messagebox.showinfo("Selected", "Cover image selected!")

def select_secret_image():
    global secret_image_path
    secret_image_path = filedialog.askopenfilename(title="Select Secret Image")
    if secret_image_path:
        messagebox.showinfo("Selected", "Secret image selected!")

def hide_image():
    global secret_height, secret_width

    if cover_image_path == "" or secret_image_path == "":
        messagebox.showerror("Error", "Please select both images first.")
        return

    # Load images
    cover = cv2.imread(cover_image_path)
    secret = cv2.imread(secret_image_path)

    if cover is None:
        messagebox.showerror("Error", "Cover image could not be loaded.")
        return
    if secret is None:
        messagebox.showerror("Error", "Secret image could not be loaded.")
        return

    # Resize secret image to fit next to cover image
    secret = cv2.resize(secret, (cover.shape[1], cover.shape[0]))
    secret_height, secret_width = secret.shape[:2]

    # Concatenate side by side
    stego = np.hstack((cover, secret))

    # Save stego image
    cv2.imwrite("stego_image.png", stego)
    messagebox.showinfo("Success", "Images combined side by side and saved as 'stego_image.png'.")

def unlock_image():
    # Open webcam
    cap = cv2.VideoCapture(0)
    messagebox.showinfo("Info", "Look at the camera with a happy face to unlock!")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        messagebox.showerror("Error", "Error capturing webcam image")
        return

    try:
        # Emotion detection
        analysis = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)
        dominant_emotion = analysis[0]['dominant_emotion'] if isinstance(analysis, list) else analysis['dominant_emotion']
        print(f"Emotion detected: {dominant_emotion}")
        messagebox.showinfo("Emotion Detected", f"Emotion detected: {dominant_emotion}")
    except Exception as e:
        print(f"Detection Error: {e}")
        messagebox.showerror("Error", "Emotion detection failed.")
        return

    if dominant_emotion.lower() == "happy":
        stego = cv2.imread("stego_image.png")
        if stego is None:
            messagebox.showerror("Error", "Stego image not found.")
            return

        messagebox.showinfo("Success", "Emotion matched! Displaying hidden image...")

        # Split cover and secret side-by-side from stego image
        half_width = stego.shape[1] // 2
        cover = stego[:, :half_width]
        secret = stego[:, half_width:]

        # Show both images side-by-side
        fig, axs = plt.subplots(1, 2)
        axs[0].imshow(cv2.cvtColor(cover, cv2.COLOR_BGR2RGB))
        axs[0].set_title("Cover Image")
        axs[0].axis("off")

        axs[1].imshow(cv2.cvtColor(secret, cv2.COLOR_BGR2RGB))
        axs[1].set_title("Hidden Image")
        axs[1].axis("off")

        plt.tight_layout()
        plt.show()

    else:
        messagebox.showerror("Error", f"Emotion didn't match. You showed: {dominant_emotion}")

# GUI setup
root = tk.Tk()
root.title("Emotion-Locked Steganography")
root.geometry("400x300")

tk.Button(root, text="Select Cover Image", command=select_cover_image, bg="black", fg="white", width=30).pack(pady=10)
tk.Button(root, text="Select Secret Image", command=select_secret_image, bg="black", fg="white", width=30).pack(pady=10)
tk.Button(root, text="Hide & Save Stego Image", command=hide_image, bg="green", fg="white", width=30).pack(pady=10)
tk.Button(root, text="Unlock Hidden Image (Emotion Match)", command=unlock_image, bg="red", fg="white", width=30).pack(pady=10)

root.mainloop()


