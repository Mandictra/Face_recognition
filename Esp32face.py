import os
from dotenv import load_dotenv
import cv2
import face_recognition
import numpy as np
import pickle
import pandas as pd
import requests
from datetime import datetime
import tkinter as tk
from tkinter import Label, Button, Entry, StringVar, messagebox, ttk
from PIL import Image, ImageTk
from send_email import send_attendance_report

load_dotenv()

ESP32_IP = "http://193.0.0.104/"

class FacialRecognitionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Facial Recognition System")
        self.root.geometry("900x700")
        self.root.configure(bg="#2E2E2E")  # Dark background
        
        self.video_label = Label(self.root, bg="#2E2E2E")
        self.video_label.pack()

        self.name_var = StringVar()
        self.reg_var = StringVar()

        Label(self.root, text="Name:", fg="white", bg="#2E2E2E").pack()
        Entry(self.root, textvariable=self.name_var, bg="#555555", fg="white", insertbackground="white").pack()

        Label(self.root, text="Registration Number:", fg="white", bg="#2E2E2E").pack()
        Entry(self.root, textvariable=self.reg_var, bg="#555555", fg="white", insertbackground="white").pack()

        btn_style = {"bg": "#444444", "fg": "white", "activebackground": "#666666", "activeforeground": "white"}

        self.capture_button = Button(self.root, text="Register Face", command=self.register_face, **btn_style)
        self.capture_button.pack()

        self.attendance_button = Button(self.root, text="Mark Attendance", command=self.mark_attendance, **btn_style)
        self.attendance_button.pack()

        # Added Check Access Button
        self.access_button = Button(self.root, text="Check Access", command=self.check_access, **btn_style)
        self.access_button.pack()

        self.email_button = Button(self.root, text="Send Attendance Report", command=self.send_report, **btn_style)
        self.email_button.pack()

        self.exit_button = Button(self.root, text="Exit", command=self.root.quit, **btn_style)
        self.exit_button.pack()

        self.cap = cv2.VideoCapture(0)
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_database_file = "face_database.dat"
        self.attendance_file = "attendance.csv"
        self.load_known_faces()
        self.update_video()

    def send_report(self):
        if not self.recipient_email:
            messagebox.showerror("Error", "Recipient email not set in .env file.")
            return
        send_attendance_report(self.attendance_file, self.recipient_email)

    def load_known_faces(self):
        if os.path.exists(self.face_database_file):
            with open(self.face_database_file, "rb") as f:
                data = pickle.load(f)
                self.known_face_encodings = data["encodings"]
                self.known_face_names = data["names"]

    def save_face_database(self):
        data = {"encodings": self.known_face_encodings, "names": self.known_face_names}
        with open(self.face_database_file, "wb") as f:
            pickle.dump(data, f)

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.root.after(10, self.update_video)

    def check_access(self):
        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture frame.")
            return

        face_encodings = face_recognition.face_encodings(frame)
        if len(face_encodings) != 1:
            messagebox.showerror("Error", "Ensure only one face is visible.")
            return

        matches = face_recognition.compare_faces(self.known_face_encodings, face_encodings[0])
        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encodings[0])
        best_match_index = np.argmin(face_distances) if face_distances.size else None

        if best_match_index is not None and matches[best_match_index]:
            unique_id = self.known_face_names[best_match_index]
            name, reg_number = unique_id.split("_")
            
            messagebox.showinfo("Success", f"Access granted for {name}.")
            
            try:
                response = requests.get(f"{ESP32_IP}/control?action=open_door")
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Door opened!")
                else:
                    messagebox.showerror("Error", "Failed to open the door.")
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Connection failed: {e}")
        else:
            messagebox.showerror("Error", "Face not recognized.")

    def register_face(self):
        name = self.name_var.get().strip()
        reg_number = self.reg_var.get().strip()

        if not name or not reg_number:
            messagebox.showerror("Error", "Please enter both name and registration number.")
            return

        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture frame.")
            return

        face_locations = face_recognition.face_locations(frame)
        if len(face_locations) != 1:
            messagebox.showerror("Error", "Ensure only one face is visible.")
            return

        face_encoding = face_recognition.face_encodings(frame, face_locations)[0]

        if any(face_recognition.compare_faces(self.known_face_encodings, face_encoding)):
            messagebox.showerror("Error", "You are already registered.")
            return

        self.known_face_encodings.append(face_encoding)
        self.known_face_names.append(f"{name}_{reg_number}")
        self.save_face_database()

        messagebox.showinfo("Success", f"Face for {name} registered.")

    def log_attendance(self, name, reg_number):
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M:%S")

        if not os.path.exists(self.attendance_file):
            df = pd.DataFrame(columns=["Name", "RegNumber", "Date", "Time"])
        else:
            df = pd.read_csv(self.attendance_file)

        new_entry = pd.DataFrame([[name, reg_number, date_str, time_str]], columns=["Name", "RegNumber", "Date", "Time"])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(self.attendance_file, index=False)

    def mark_attendance(self):
        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture frame.")
            return

        face_encodings = face_recognition.face_encodings(frame)
        if len(face_encodings) != 1:
            messagebox.showerror("Error", "Ensure only one face is visible.")
            return

        matches = face_recognition.compare_faces(self.known_face_encodings, face_encodings[0])
        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encodings[0])
        best_match_index = np.argmin(face_distances) if face_distances.size else None

        if best_match_index is not None and matches[best_match_index]:
            unique_id = self.known_face_names[best_match_index]
            name, reg_number = unique_id.split("_")
            self.log_attendance(name, reg_number)
            messagebox.showinfo("Success", f"Attendance marked for {name}.")
        else:
            messagebox.showerror("Error", "Face not recognized.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FacialRecognitionUI(root)
    root.mainloop()
