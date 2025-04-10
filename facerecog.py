import os
import cv2
import face_recognition
import numpy as np
import pickle
import pandas as pd
from datetime import datetime
import tkinter as tk
from tkinter import Label, Button, Entry, StringVar, messagebox, Toplevel, Listbox, Scrollbar, Frame
from PIL import Image, ImageTk
from send_email import send_attendance_report  # Import the email module

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

        # Create frame for buttons
        button_frame = Frame(self.root, bg="#2E2E2E")
        button_frame.pack(pady=10)

        btn_style = {"bg": "#444444", "fg": "white", "activebackground": "#666666", "activeforeground": "white", "width": 15}

        # First row of buttons
        row1_frame = Frame(button_frame, bg="#2E2E2E")
        row1_frame.pack()

        self.capture_button = Button(row1_frame, text="Register Face", command=self.register_face, **btn_style)
        self.capture_button.pack(side=tk.LEFT, padx=5)

        self.attendance_button = Button(row1_frame, text="Mark Attendance", command=self.mark_attendance, **btn_style)
        self.attendance_button.pack(side=tk.LEFT, padx=5)

        # Second row of buttons
        row2_frame = Frame(button_frame, bg="#2E2E2E")
        row2_frame.pack(pady=5)

        self.email_button = Button(row2_frame, text="Send Report", command=self.send_report, **btn_style)
        self.email_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = Button(row2_frame, text="Clear Attendance", command=self.clear_attendance, **btn_style)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Third row of buttons
        row3_frame = Frame(button_frame, bg="#2E2E2E")
        row3_frame.pack(pady=5)

        self.manage_button = Button(row3_frame, text="Manage Faces", command=self.manage_faces, **btn_style)
        self.manage_button.pack(side=tk.LEFT, padx=5)

        self.exit_button = Button(row3_frame, text="Exit", command=self.root.quit, **btn_style)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        self.cap = cv2.VideoCapture(0)
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_database_file = "face_database.dat"
        self.attendance_file = "attendance.csv"
        self.load_known_faces()
        self.update_video()
    
    def clear_attendance(self):
        """Manual method to clear attendance records"""
        if not os.path.exists(self.attendance_file):
            messagebox.showinfo("Info", "No attendance records to clear.")
            return
        
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear all attendance records?")
        if confirm:
            try:
                os.remove(self.attendance_file)
                messagebox.showinfo("Success", "Attendance records cleared.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear attendance: {str(e)}")
    
    def manage_faces(self):
        """Open a window to manage registered faces"""
        manage_window = Toplevel(self.root)
        manage_window.title("Manage Registered Faces")
        manage_window.geometry("400x300")
        manage_window.configure(bg="#2E2E2E")
        
        scrollbar = Scrollbar(manage_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.faces_listbox = Listbox(manage_window, yscrollcommand=scrollbar.set, bg="#555555", fg="white")
        self.faces_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.faces_listbox.yview)
        
        # Populate the listbox
        for name in self.known_face_names:
            self.faces_listbox.insert(tk.END, name)
        
        delete_button = Button(manage_window, text="Delete Selected", command=self.delete_selected_face, 
                             bg="#444444", fg="white", activebackground="#666666", activeforeground="white")
        delete_button.pack()
    
    def delete_selected_face(self):
        """Delete the selected face from the database"""
        selection = self.faces_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "No face selected.")
            return
        
        index = selection[0]
        face_name = self.faces_listbox.get(index)
        
        # Remove from lists
        del self.known_face_names[index]
        del self.known_face_encodings[index]
        
        # Save the updated database
        self.save_face_database()
        
        # Update the listbox
        self.faces_listbox.delete(index)
        
        messagebox.showinfo("Success", f"Deleted {face_name} from database.")
    
    def send_report(self):
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        if not self.recipient_email:
            messagebox.showerror("Error", "Recipient email not set in .env file.")
            return
        send_attendance_report(self.attendance_file, self.recipient_email)  # Calls function from send_email.py
    
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
    
    def is_duplicate_face(self, face_encoding):
        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
        return any(matches)
    
    def has_already_marked_attendance(self, name, reg_number):
        date_str = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(self.attendance_file):
            df = pd.read_csv(self.attendance_file)
            return not df[(df["Name"] == name) & (df["RegNumber"] == reg_number) & (df["Date"] == date_str)].empty
        return False
    
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
        
        if self.is_duplicate_face(face_encoding):
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
            
            if self.has_already_marked_attendance(name, reg_number):
                messagebox.showerror("Error", f"{name} has already been marked present today.")
                return
            
            self.log_attendance(name, reg_number)
            messagebox.showinfo("Success", f"Attendance marked for {name}.")
        else:
            messagebox.showerror("Error", "Face not recognized.")
    
    def run(self):
        self.root.mainloop()
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = FacialRecognitionUI(root)
    app.run()