#!/bin/python3

import socket
import psutil
import time
from datetime import datetime

HOST = 'localhost'
PORT = 13666

lcd_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lcd_socket.connect((HOST, PORT))

def send_command(command):
    "Sendet einen Befehl an den LCDproc-Server und gibt Debug-Informationen aus."
    #print(f"Sending: {command}")
    lcd_socket.sendall((command + "\n").encode("utf-8"))

def setup_screen():
    "Richtet den LCD-Bildschirm und die horizontalen Balken für CPU und RAM sowie Zeit und Datum ein."
    send_command("hello")
    send_command("client_set name {PythonLCD}")

    # Bildschirm hinzufügen
    send_command("screen_add sysinfo")
    send_command("screen_set sysinfo name {System Info}")
    send_command("screen_set sysinfo heartbeat off")  # Herzschlag deaktivieren
    
    # Uhrzeit-Widget hinzufügen (linke Seite der ersten Zeile)
    send_command("widget_add sysinfo time_label string")
    send_command("widget_set sysinfo time_label 1 1 {00:00:00}")  # Platzhalter für Uhrzeit
    
    # Datum-Widget hinzufügen (rechte Seite der ersten Zeile)
    send_command("widget_add sysinfo date_label string")
    send_command("widget_set sysinfo date_label 11 1 {01.01.2023}")  # Platzhalter für Datum

    # Text-Widget für CPU-Beschriftung hinzufügen (eine Zeile über dem Balken)
    send_command("widget_add sysinfo cpu_label string")
    send_command("widget_set sysinfo cpu_label 1 2 {CPU}")  # CPU-Beschriftung über dem CPU-Balken
    
    # CPU-Auslastung als horizontalen Balken hinzufügen
    send_command("widget_add sysinfo cpu_usage hbar")
    send_command("widget_set sysinfo cpu_usage 1 3 0")  # Anfangsposition und Wert für CPU-Auslastung
    
    # Text-Widget für RAM-Beschriftung hinzufügen (eine Zeile über dem Balken)
    send_command("widget_add sysinfo ram_label string")
    send_command("widget_set sysinfo ram_label 1 4 {RAM}")  # RAM-Beschriftung über dem RAM-Balken
    
    # RAM-Auslastung als horizontalen Balken hinzufügen
    send_command("widget_add sysinfo ram_usage hbar")
    send_command("widget_set sysinfo ram_usage 1 5 0")  # Anfangsposition und Wert für RAM-Auslastung

def update_screen():
    "Aktualisiert die horizontalen Balken für CPU- und RAM-Auslastung sowie die Zeit und das Datum."
    # Holen der aktuellen CPU- und RAM-Auslastung als Ganzzahlen
    cpu_percent = int(psutil.cpu_percent())  # Rundet auf die nächste ganze Zahl
    ram_percent = int(psutil.virtual_memory().percent)  # Rundet auf die nächste ganze Zahl
    
    # Ermittlung der RAM-Nutzung in GB und der maximalen RAM-Kapazität
    # ram_used_gb = psutil.virtual_memory().used / (1024 ** 3)  # Umrechnung von Bytes auf GB
    # ram_total_gb = psutil.virtual_memory().total / (1024 ** 3)  # Umrechnung von Bytes auf GB
    
    # Formatierung der Prozentsätze und der RAM-Nutzung in GB
    cpu_display = f"{cpu_percent:2}%"  # z.B. ' 9%' oder '45%'
    # ram_display = f"{ram_percent:2}% {ram_used_gb:3.1f}GB/{ram_total_gb:3.1f}GB" #Display kann nicht alle Zeichen darstellen.
    ram_display = f"{ram_percent:2}% "
    
    # CPU-Balken aktualisieren
    send_command(f"widget_set sysinfo cpu_label 1 2 {{CPU: {cpu_display}}}")
    send_command(f"widget_set sysinfo cpu_usage 1 3 {cpu_percent}")
    
    # RAM-Balken aktualisieren
    send_command(f"widget_set sysinfo ram_label 1 4 {{RAM: {ram_display}}}")
    send_command(f"widget_set sysinfo ram_usage 1 5 {ram_percent}")
    
    # Aktuelle Zeit und Datum holen
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%d.%m.%Y")
    
    # Uhrzeit-Widget aktualisieren
    send_command(f"widget_set sysinfo time_label 1 1 {{{current_time}}}")
    
    # Datum-Widget aktualisieren (rechte Seite der Zeile)
    send_command(f"widget_set sysinfo date_label 11 1 {{{current_date}}}")

try:
    setup_screen()
    while True:
        update_screen()
        time.sleep(1)  # Aktualisierung jede Sekunde
except KeyboardInterrupt:
    pass
finally:
    # Bildschirm entfernen und Verbindung schließen
    send_command("screen_del sysinfo")
    lcd_socket.close()

