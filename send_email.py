import os
import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage
from tkinter import messagebox

def send_attendance_report(attendance_file, recipient_email):
    if not os.path.exists(attendance_file):
        messagebox.showerror("Error", "No attendance records to send.")
        return

    df = pd.read_csv(attendance_file)
    attendance_excel = "attendance.xlsx"
    df.to_excel(attendance_excel, index=False)

    email_sender = "omsohhorn@gmail.com"  # Change this
    email_password = "hbcn lfpk rzpq qmie"   # Use an app password for security

    subject = "Daily Attendance Report"
    body = "Please find the attached attendance report."

    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = recipient_email
    em["Subject"] = subject
    em.set_content(body)

    with open(attendance_excel, "rb") as attachment:
        em.add_attachment(attachment.read(), maintype="application", subtype="octet-stream", filename=attendance_excel)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_sender, email_password)
            server.send_message(em)
        messagebox.showinfo("Success", "Attendance report sent successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {e}")
