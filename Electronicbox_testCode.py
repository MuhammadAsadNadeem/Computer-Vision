import tkinter as tk
import threading
import time
import serial
import serial.tools.list_ports
from tkinter import messagebox

# Globals
serial_connection = None
stop_event = threading.Event()
signal_count = 0
start_time = None
stop_time = None

def is_usb_connected():
    """Check for USB serial port presence."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.description:
            return port.device
    return None

def initialize_serial_connection():
    global serial_connection
    port = is_usb_connected()
    if port:
        try:
            serial_connection = serial.Serial(
                port=port,
                baudrate=9600,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            print(f"Connected to {port}")
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", f"Could not open serial port: {e}")
            serial_connection = None
    else:
        messagebox.showwarning("USB Not Found", "No USB serial device found.")

def send_signal_every_second():
    global signal_count
    while not stop_event.is_set():
        try:
            if serial_connection and serial_connection.is_open:
                serial_connection.write(b'Go\r')
                signal_count += 1
                print(f"Sent: Go | Count: {signal_count}")
        except Exception as e:
            print(f"Error sending signal: {e}")
        time.sleep(1)

def start_signal():
    global signal_count, start_time
    signal_count = 0
    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    status_label.config(text=f"Started at: {start_time}")
    stop_event.clear()
    threading.Thread(target=send_signal_every_second, daemon=True).start()

def stop_signal():
    global stop_time
    stop_event.set()
    stop_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    status_label.config(
        text=f"Stopped at: {stop_time} | Total signals sent: {signal_count}"
    )
    print(f"Stopped at: {stop_time}, Total signals: {signal_count}")

def on_closing():
    stop_signal()
    if serial_connection and serial_connection.is_open:
        serial_connection.close()
    root.destroy()

# GUI Setup
root = tk.Tk()
root.title("Signal Generator")

connect_button = tk.Button(root, text="Connect USB", command=initialize_serial_connection)
connect_button.pack(pady=5)

start_button = tk.Button(root, text="Start", command=start_signal)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop", command=stop_signal)
stop_button.pack(pady=5)

status_label = tk.Label(root, text="Status: Not started")
status_label.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
