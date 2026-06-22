import argparse
import importlib
import sys


def run_tk_ui():
    import customtkinter as ctk
    from tkinter import messagebox
    import shutdown_core

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    def format_duration(seconds):
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours and minutes:
            return f"{hours}h {minutes}m"
        if hours:
            return f"{hours}h"
        return f"{minutes}m"

    def set_status(message, color=None):
        status_label.configure(text=message)
        if color:
            status_label.configure(text_color=color)

    def set_busy(message=None):
        if message:
            busy_label.configure(text=message)
            busy_frame.grid()
            busy_bar.start()
            root.update_idletasks()
        else:
            busy_bar.stop()
            busy_frame.grid_remove()
            root.update_idletasks()

    def set_active_timer(target_time="--:--", seconds=0, test_mode=True):
        target_label.configure(text=target_time)
        if seconds > 0:
            remaining_label.configure(text=f"{format_duration(seconds)} remaining")
            mode_label.configure(
                text="Test mode: no shutdown will run." if test_mode else "Live shutdown is armed.",
                text_color=("#8aa0b8" if test_mode else "#f59e0b"),
            )
        else:
            remaining_label.configure(text="No active timer")
            mode_label.configure(text="Choose a time and schedule when ready.", text_color="#8aa0b8")

    def refresh_stats():
        for row in stats_frame.winfo_children():
            row.destroy()

        stats = shutdown_core.get_stats(5)
        if not stats:
            ctk.CTkLabel(stats_frame, text="No activity yet.", text_color="#8aa0b8").pack(anchor="w")
            return

        for item in stats:
            seconds = item.get("scheduled_seconds") or 0
            mode = "Test" if item.get("event_type") == "scheduled_test" else "Shutdown"
            state = "Done" if item.get("performed") else "Pending"
            ts = (item.get("ts") or "").replace("T", " ")[:16]
            row = ctk.CTkFrame(stats_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=mode, width=80, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=format_duration(seconds), width=70, text_color="#8aa0b8").pack(side="left")
            ctk.CTkLabel(row, text=ts, anchor="w", text_color="#8aa0b8").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(
                row,
                text=state,
                width=70,
                anchor="e",
                text_color=("#22c55e" if item.get("performed") else "#f59e0b"),
            ).pack(side="right")

    def schedule_shutdown():
        set_busy("Scheduling timer...")
        root.after(50, perform_schedule_shutdown)

    def perform_schedule_shutdown():
        try:
            hour = int(hour_var.get())
            minute = int(minute_var.get())
            test_mode = test_var.get()

            def on_scheduled(seconds, target_time):
                root.after(0, lambda: set_active_timer(target_time, seconds, test_mode))
                root.after(0, lambda: set_status(f"Scheduled for {target_time}", "#2dd4bf"))
                root.after(0, lambda: set_busy(None))
                root.after(0, refresh_stats)

            def on_performed(kind):
                root.after(0, lambda: set_status(f"Performed: {kind}", "#2dd4bf"))
                root.after(0, lambda: set_active_timer())
                root.after(0, refresh_stats)

            shutdown_core.schedule_shutdown_at(
                hour,
                minute,
                test_mode,
                on_scheduled=on_scheduled,
                on_performed=on_performed,
            )

        except ValueError:
            set_busy(None)
            messagebox.showerror("Error", "Select a valid time.")

    def cancel_shutdown():
        set_busy("Canceling timer...")
        root.after(50, perform_cancel_shutdown)

    def perform_cancel_shutdown():
        ok = shutdown_core.cancel_shutdown()
        if ok:
            set_active_timer()
            set_status("Cancel requested", "#2dd4bf")
        else:
            set_status("Cancel failed", "#ef4444")
        refresh_stats()
        set_busy(None)

    root = ctk.CTk()
    root.title("AutoShutdown")
    root.geometry("680x500")
    root.minsize(620, 460)

    shell = ctk.CTkFrame(root, fg_color="transparent")
    shell.pack(fill="both", expand=True, padx=18, pady=18)
    shell.grid_columnconfigure(1, weight=1)
    shell.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(shell, text="AutoShutdown", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(shell, text="Schedule one shutdown timer for this device.", text_color="#8aa0b8").grid(row=0, column=1, sticky="e")

    control_frame = ctk.CTkFrame(shell, corner_radius=8)
    control_frame.grid(row=1, column=0, sticky="nsew", pady=(18, 0), padx=(0, 14))
    control_frame.grid_columnconfigure((0, 1), weight=1)

    ctk.CTkLabel(control_frame, text="Shutdown Time", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 14))

    ctk.CTkLabel(control_frame, text="Hour", text_color="#8aa0b8").grid(row=1, column=0, sticky="w", padx=(18, 8))
    ctk.CTkLabel(control_frame, text="Minute", text_color="#8aa0b8").grid(row=1, column=1, sticky="w", padx=(8, 18))
    hour_var = ctk.StringVar(value="22")
    hour_combo = ctk.CTkComboBox(control_frame, values=[f"{i:02d}" for i in range(24)], variable=hour_var, state="readonly", height=40)
    hour_combo.grid(row=2, column=0, sticky="ew", padx=(18, 8), pady=(6, 16))
    minute_var = ctk.StringVar(value="00")
    minute_combo = ctk.CTkComboBox(control_frame, values=[f"{i:02d}" for i in range(60)], variable=minute_var, state="readonly", height=40)
    minute_combo.grid(row=2, column=1, sticky="ew", padx=(8, 18), pady=(6, 16))

    test_var = ctk.BooleanVar(value=True)
    test_switch = ctk.CTkSwitch(
        control_frame,
        text="Test mode",
        variable=test_var,
        onvalue=True,
        offvalue=False
    )
    test_switch.grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 18))

    schedule_btn = ctk.CTkButton(control_frame, text="Schedule Shutdown", command=schedule_shutdown, height=42, font=ctk.CTkFont(weight="bold"))
    schedule_btn.grid(row=4, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 10))

    cancel_btn = ctk.CTkButton(control_frame, text="Cancel Timer", command=cancel_shutdown, height=40, fg_color="#ef4444", hover_color="#dc2626")
    cancel_btn.grid(row=5, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 18))

    status_frame = ctk.CTkFrame(shell, corner_radius=8)
    status_frame.grid(row=1, column=1, sticky="nsew", pady=(18, 0))
    status_frame.grid_columnconfigure(0, weight=1)
    status_frame.grid_rowconfigure(5, weight=1)

    ctk.CTkLabel(status_frame, text="Current Timer", text_color="#8aa0b8").grid(row=0, column=0, sticky="w", padx=18, pady=(18, 0))
    target_label = ctk.CTkLabel(status_frame, text="--:--", font=ctk.CTkFont(size=54, weight="bold"))
    target_label.grid(row=1, column=0, sticky="w", padx=18)
    remaining_label = ctk.CTkLabel(status_frame, text="No active timer", font=ctk.CTkFont(size=18, weight="bold"))
    remaining_label.grid(row=1, column=0, sticky="e", padx=18)
    mode_label = ctk.CTkLabel(status_frame, text="Choose a time and schedule when ready.", text_color="#8aa0b8")
    mode_label.grid(row=2, column=0, sticky="new", padx=18, pady=(0, 10))
    status_label = ctk.CTkLabel(status_frame, text="Ready", text_color="#2dd4bf")
    status_label.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 16))

    busy_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
    busy_frame.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 16))
    busy_frame.grid_columnconfigure(0, weight=1)
    busy_label = ctk.CTkLabel(busy_frame, text="Working...", text_color="#8aa0b8")
    busy_label.grid(row=0, column=0, sticky="w")
    busy_bar = ctk.CTkProgressBar(busy_frame, mode="indeterminate")
    busy_bar.grid(row=1, column=0, sticky="ew", pady=(6, 0))
    busy_frame.grid_remove()

    stats_card = ctk.CTkFrame(status_frame, corner_radius=8)
    stats_card.grid(row=5, column=0, sticky="nsew", padx=18, pady=(0, 18))
    stats_card.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(stats_card, text="Recent Activity", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=14, pady=(12, 8))
    stats_frame = ctk.CTkFrame(stats_card, fg_color="transparent")
    stats_frame.pack(fill="both", expand=True, padx=14, pady=(0, 12))

    try:
        root.iconbitmap("shutdown.ico")
    except:
        pass

    refresh_stats()
    root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoShutdown launcher")
    parser.add_argument("--gui", choices=["qml", "tk"], default=None, help="Force the UI backend")
    parser.add_argument("--debug", action="store_true", help="Print debug information")
    args = parser.parse_args()

    if args.debug:
        print(f"Python executable: {sys.executable}")
        print(f"Requested UI: {args.gui}")
        print(f"PySide6 installed: {importlib.util.find_spec('PySide6') is not None}")

    if args.gui == "qml":
        print("Starting QML UI...")
        try:
            from gui.main_gui import run_qt_ui
            run_qt_ui()
        except Exception as exc:
            print(f"Failed to launch QML UI: {exc}")
            print("Falling back to Tk UI...")
            run_tk_ui()
    elif args.gui == "tk":
        print("Starting Tk UI...")
        run_tk_ui()
    else:
        try:
            spec = importlib.util.find_spec("PySide6")
            if spec is not None:
                print("Auto-detected PySide6, starting QML UI...")
                from gui.main_gui import run_qt_ui
                run_qt_ui()
            else:
                print("PySide6 not found, starting Tk UI...")
                run_tk_ui()
        except Exception as exc:
            print(f"Unexpected UI error: {exc}")
            run_tk_ui()
