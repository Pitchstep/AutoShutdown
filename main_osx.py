# VERSION FOR MAC (!!)
import customtkinter as ctk
from tkinter import messagebox
import os
import time
import threading
import subprocess
import platform
import sys

# Ensure we're only running on macOS
if platform.system() != "Darwin":
    print("This is only for macOS!")
    sys.exit(1)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")


def version():
    return "1.00_Mac"


def schedule_shutdown():
    try:
        hour = int(hour_var.get())
        minute = int(minute_var.get())
        test_mode = test_var.get()

        now = time.localtime()
        current_seconds = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
        target_seconds = hour * 3600 + minute * 60

        if target_seconds <= current_seconds:
            seconds_to_wait = 86400 - current_seconds + target_seconds
        else:
            seconds_to_wait = target_seconds - current_seconds

        hours_left = seconds_to_wait // 3600
        mins_left = (seconds_to_wait % 3600) // 60

        messagebox.showinfo(
            "Scheduled",
            f"Shutdown scheduled in {hours_left} hours and {mins_left} minute(s).\n"
            f"{'(Test mode enabled – no real shutdown)' if test_mode else ''}"
        )

        threading.Thread(
            target=wait_and_shutdown,
            args=(seconds_to_wait, test_mode),
            daemon=True
        ).start()

    except ValueError:
        messagebox.showerror("Error", "Please select a valid hour and minute.")


def wait_and_shutdown(seconds_to_wait, test_mode):
    time.sleep(seconds_to_wait)

    if test_mode:
        root.after(0, lambda: messagebox.showinfo(
            "TEST MODE",
            "TEST MODE: Shutdown would have happened now!\n(No action taken)"
        ))
    else:
        try:
            subprocess.run([
                "osascript", "-e",
                'tell application "System Events" to shut down'
            ], check=True)
        except Exception as e:
            root.after(0, lambda: messagebox.showerror(
                "Shutdown Failed",
                f"Could not shut down the device:\n{str(e)}\n\n"
                "Make sure you have permission or try running the app with admin rights."
            ))


def cancel_shutdown():
    messagebox.showinfo(
        "Cancel",
        "On macOS there is no direct way to cancel a scheduled shutdown.\n\n"
        "To prevent shutdown:\n"
        "• Close this application now (or Cmd+Q to force-quit)\n"
        "• Or wait for the scheduled time and cancel the shutdown prompt if it appears."
    )

root = ctk.CTk()
root.title("AutoShutdown)")
root.geometry("380x340")
root.resizable(False, False)

ctk.CTkLabel(root, text="AutoShutdown", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 10))

# Time selection frame
time_frame = ctk.CTkFrame(root)
time_frame.pack(pady=15, padx=30, fill="x")

ctk.CTkLabel(time_frame, text="Shut down at:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, columnspan=3, pady=(0, 10))

ctk.CTkLabel(time_frame, text="Hour:").grid(row=1, column=0, padx=(0, 8), sticky="e")
hour_var = ctk.StringVar(value="00")
hour_combo = ctk.CTkComboBox(
    time_frame,
    values=[f"{i:02d}" for i in range(24)],
    variable=hour_var,
    width=90,
    state="readonly"
)
hour_combo.grid(row=1, column=1, padx=5)

ctk.CTkLabel(time_frame, text="Minute:").grid(row=1, column=2, padx=(20, 8), sticky="e")
minute_var = ctk.StringVar(value="00")
minute_combo = ctk.CTkComboBox(
    time_frame,
    values=[f"{i:02d}" for i in range(60)],
    variable=minute_var,
    width=90,
    state="readonly"
)
minute_combo.grid(row=1, column=3, padx=5)

# Test mode switch
test_var = ctk.BooleanVar(value=True)
test_switch = ctk.CTkSwitch(
    root,
    text="Test Mode",
    variable=test_var,
    onvalue=True,
    offvalue=False,
    font=ctk.CTkFont(size=13)
)
test_switch.pack(pady=25)

# Buttons
btn_frame = ctk.CTkFrame(root, fg_color="transparent")
btn_frame.pack(pady=10)

schedule_btn = ctk.CTkButton(
    btn_frame,
    text="Schedule Shutdown",
    command=schedule_shutdown,
    width=160,
    height=40,
    font=ctk.CTkFont(size=14, weight="bold")
)
schedule_btn.grid(row=0, column=0, padx=12)

cancel_btn = ctk.CTkButton(
    btn_frame,
    text="Cancel / Info",
    command=cancel_shutdown,
    width=160,
    height=40,
    fg_color="#C44536",
    hover_color="#A6372A",
    font=ctk.CTkFont(size=14, weight="bold")
)
cancel_btn.grid(row=0, column=1, padx=12)

ctk.CTkLabel(
    root,
    text=f"v{version()} | Developed by Pitchstep",
    text_color="gray",
    font=ctk.CTkFont(size=11)
).pack(pady=(20, 20))

root.mainloop()