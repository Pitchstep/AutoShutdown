import customtkinter as ctk
from tkinter import messagebox
import os
import time
import threading

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

def version():
    return "1.00"

def schedule_shutdown():
    try:
        hour = int(hour_var.get())
        minute = int(minute_var.get())
        test_mode = test_var.get()

        now = time.localtime()
        current_hour, current_minute, current_second = now.tm_hour, now.tm_min, now.tm_sec

        target_seconds = hour * 3600 + minute * 60
        current_seconds = current_hour * 3600 + current_minute * 60 + current_second

        if target_seconds <= current_seconds:
            seconds_to_wait = 86400 - current_seconds + target_seconds  # 24h
        else:
            seconds_to_wait = target_seconds - current_seconds

        hours_left = seconds_to_wait // 3600
        mins_left = (seconds_to_wait % 3600) // 60

        messagebox.showinfo(
            "Done",
            f"Shutdown has been scheduled to happen in {hours_left} hours & {mins_left} minute(s).\n{'Test mode is enabled.' if test_mode else ''}"
        )

        threading.Thread(
            target=wait_and_shutdown,
            args=(seconds_to_wait, test_mode),
            daemon=True
        ).start()

    except ValueError:
        messagebox.showerror("Error", "Select a valid time.")

# ────────────────────────────────────────────────
def wait_and_shutdown(seconds, test_mode):
    time.sleep(seconds)
    if test_mode:
        root.after(0, lambda: messagebox.showinfo(
            "TEST MODE",
            "TEST MODE: Shutdown would have occurred now!\n(No real action taken)"
        ))
    else:
        try:
            os.system("shutdown /s /t 0")
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", f"Shutdown failed:\n{e}"))

# ────────────────────────────────────────────────
def cancel_shutdown():
    try:
        os.system("shutdown /a")
        messagebox.showinfo("Canceled", "Shutdown canceled (if scheduled).")
    except:
        messagebox.showinfo("Info", "No shutdown was pending or cancel failed.")

# ────────────────────────────────────────────────

root = ctk.CTk()
root.title(f"AutoShutdown")
root.geometry("360x320")
root.resizable(False, False)

ctk.CTkLabel(root, text="AutoShutdown", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))

time_frame = ctk.CTkFrame(root)
time_frame.pack(pady=10, padx=20, fill="x")

ctk.CTkLabel(time_frame, text="Hour:").grid(row=0, column=0, padx=(0,10), pady=8, sticky="e")
hour_var = ctk.StringVar(value="00")
hour_combo = ctk.CTkComboBox(time_frame, values=[f"{i:02d}" for i in range(24)], variable=hour_var, width=80, state="readonly")
hour_combo.grid(row=0, column=1, pady=8)

ctk.CTkLabel(time_frame, text="Minute:").grid(row=1, column=0, padx=(0,10), pady=8, sticky="e")
minute_var = ctk.StringVar(value="00")
minute_combo = ctk.CTkComboBox(time_frame, values=[f"{i:02d}" for i in range(60)], variable=minute_var, width=80, state="readonly")
minute_combo.grid(row=1, column=1, pady=8)


test_var = ctk.BooleanVar(value=True)
test_switch = ctk.CTkSwitch(
    root,
    text="Test Mode",
    variable=test_var,
    onvalue=True,
    offvalue=False
)
test_switch.pack(pady=15)


btn_frame = ctk.CTkFrame(root, fg_color="transparent")
btn_frame.pack(pady=10)

schedule_btn = ctk.CTkButton(btn_frame, text="Schedule", command=schedule_shutdown, width=140)
schedule_btn.grid(row=0, column=0, padx=10)

cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=cancel_shutdown, width=140, fg_color="#C44536", hover_color="#A6372A")
cancel_btn.grid(row=0, column=1, padx=10)

ctk.CTkLabel(root, text=f"v{version()} | Developed by Pitchstep", text_color="gray", font=ctk.CTkFont(size=11)).pack(pady=(10,20))

try:
    root.iconbitmap("shutdown.ico")
except:
    pass

root.mainloop()