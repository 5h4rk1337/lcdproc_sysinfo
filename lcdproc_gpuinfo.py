#!/bin/python3

import socket
import GPUtil
import time
from datetime import datetime

HOST = 'localhost'
PORT = 13666

lcd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lcd_socket.connect((HOST, PORT))

def send_command(command):
    """Sendet einen Befehl an den LCDproc-Server."""
    lcd_socket.sendall((command + "\n").encode("utf-8"))

def setup_screen():
    """Richtet den LCD-Bildschirm und die Widgets für GPU-Auslastung, VRAM, Zeit und Datum ein."""
    send_command("hello")
    send_command("client_set name {PythonLCD}")

    send_command("screen_add sysinfo")
    send_command("screen_set sysinfo name {System Info}")
    send_command("screen_set sysinfo heartbeat off")

    send_command("widget_add sysinfo time_label string")
    send_command("widget_set sysinfo time_label 1 1 {00:00:00}")

    send_command("widget_add sysinfo date_label string")
    send_command("widget_set sysinfo date_label 11 1 {01.01.2023}")

    send_command("widget_add sysinfo gpu_label string")
    send_command("widget_set sysinfo gpu_label 1 2 {GPU}")

    send_command("widget_add sysinfo gpu_usage hbar")
    send_command("widget_set sysinfo gpu_usage 1 3 0")

    send_command("widget_add sysinfo vram_label string")
    send_command("widget_set sysinfo vram_label 1 4 {VRAM}")

    send_command("widget_add sysinfo vram_usage hbar")
    send_command("widget_set sysinfo vram_usage 1 5 0")

def update_screen():
    """Aktualisiert die GPU- und VRAM-Auslastung sowie Zeit und Datum."""
    gpus = GPUtil.getGPUs()
    if not gpus:
        return  # Keine GPU gefunden

    gpu = gpus[0]  # Nimm die erste GPU
    gpu_percent = int(gpu.load * 100)  # GPU-Auslastung in Prozent
    vram_used = gpu.memoryUsed  # Genutzter VRAM in MB
    vram_total = gpu.memoryTotal  # Gesamter VRAM in MB
    vram_percent = int((vram_used / vram_total) * 100)  # VRAM-Auslastung in Prozent

    gpu_display = f"{gpu_percent:2}%"
    # vram_display = f"{vram_percent:2}% {vram_used:.0f}MB/{vram_total:.0f}MB"
    vram_display = f"{vram_percent:2}%"

    send_command(f"widget_set sysinfo gpu_label 1 2 {{GPU:  {gpu_display}}}")
    send_command(f"widget_set sysinfo gpu_usage 1 3 {int(gpu_percent * 1.59)}")

    send_command(f"widget_set sysinfo vram_label 1 4 {{VRAM: {vram_display}}}")
    send_command(f"widget_set sysinfo vram_usage 1 5 {int(vram_percent * 1.59)}")

    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d.%m.%Y")

    send_command(f"widget_set sysinfo time_label 1 1 {{{current_time}}}")
    send_command(f"widget_set sysinfo date_label 11 1 {{{current_date}}}")

try:
    setup_screen()
    while True:
        update_screen()
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    send_command("screen_del sysinfo")
    lcd_socket.close()
