# tray.py

import pystray
from pystray import MenuItem as item, Menu
from PIL import Image
import os
from monitor import start_monitoring, stop_monitoring

is_running = False

def on_toggle(icon, menu_item):
    global is_running
    if is_running:
        stop_monitoring()
        is_running = False
        icon.menu = build_menu()
    else:
        start_monitoring()
        is_running = True
        icon.menu = build_menu()

def on_quit(icon, item):
    stop_monitoring()
    icon.stop()

def build_menu():
    toggle_text = "Stop Monitoring" if is_running else "Start Monitoring"
    return Menu(
        item(toggle_text, on_toggle),
        item("Quit", on_quit)
    )

def run_tray():
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "icons", "catdams.ico")
        image = Image.open(icon_path)

        icon = pystray.Icon("CATDAMS Sentinel", image, "CATDAMS Sentinel", build_menu())
        print("Tray is launching...")
        icon.run()
    except Exception as e:
        print(f"Error starting tray icon: {e}")
