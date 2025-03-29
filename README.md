# Facial Recognition Attendance System

## Overview
This is a **Facial Recognition Attendance System** built using **Python**, **OpenCV**, and **face_recognition**. It allows users to:
- Register their face with a name and registration number.
- Mark attendance automatically using facial recognition.
- Check access by recognizing a face and opening a door (via an ESP32-controlled system).
- Send attendance reports via email.

## Features
✅ **Facial Recognition** – Uses `face_recognition` to identify users.
✅ **Dark Mode GUI** – Uses `tkinter` with a dark-themed interface.
✅ **ESP32 Integration** – Sends HTTP requests to an ESP32 to control a door.
✅ **Email Reports** – Sends attendance logs via email.
✅ **Data Persistence** – Saves registered faces and attendance records.

## Installation
### 1. Clone the Repository
```bash
git clone[https://github.com/Mandictra/Face_recognition.git]
cd Face_recognition
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
**Required Libraries:**
- `opencv-python`
- `face-recognition`
- `pandas`
- `requests`
- `pillow`
- `dotenv`

### 3. Configure Environment Variables
Create a **.env** file in the project directory:
```env
RECIPIENT_EMAIL=youremail@example.com
EMAIL_SENDER=recipient@example.com
EMAIL_PASSWORD=app password
```

### 4. Run the Application
```bash
python Esp32face.py
```

## Usage
1. **Register a Face:** Enter your name and registration number, then click `Register Face`.
2. **Mark Attendance:** Click `Mark Attendance` while facing the camera.
3. **Check Access:** Click `Check Access` to verify and unlock the door.
4. **Send Report:** Click `Send Attendance Report` to email the daily attendance log.
5. **Exit:** Click `Exit` to close the application.

## ESP32 API
Ensure your ESP32 has a web server running and update the `ESP32_IP` in `Esp32face.py`.
From the main.cpp get the ip address of your esp32
- `http://193.0.0.106` – checks the esp32.

## Contribution
Feel free to fork this project and submit pull requests for improvements.

## License
MIT License

