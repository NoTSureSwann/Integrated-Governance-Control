import sys
import os
import asyncio
from PySide6.QtWidgets import QApplication
import qasync

# Memastikan Python bisa membaca module dari root direktori
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.main_window import MainWindow
from utils.logger import log_info
from services.websocket_server import WebSocketServer
from services.websocket_client import nexus_ws_client

def load_stylesheet(app: QApplication, theme_name: str = "dark"):
    """Fungsi untuk memuat berkas QSS Tema."""
    theme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gui", "themes", f"{theme_name}.qss")
    if os.path.exists(theme_path):
        with open(theme_path, "r") as f:
            app.setStyleSheet(f.read())
        log_info(f"Berhasil memuat tema: {theme_name}")
    else:
        log_info(f"Peringatan: Berkas tema {theme_path} tidak ditemukan.")

async def main():
    """Fungsi utama asinkron"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        
    # Memuat gaya/tema
    load_stylesheet(app, "dark")
    
    # Jalankan WebSocket Server lokal
    ws_server = WebSocketServer()
    asyncio.create_task(ws_server.start())
    
    # Jalankan WebSocket Client
    asyncio.create_task(nexus_ws_client.start())
    
    # Inisialisasi jendela utama
    main_window = MainWindow()
    main_window.show()
    
    log_info("Project Nexus GUI (PySide6) Berhasil Diluncurkan.")
    
    # Biarkan loop asinkron berjalan
    await asyncio.Event().wait()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Menggunakan qasync untuk menangani fungsi asinkron (API AI, dll)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        log_info("Aplikasi dihentikan oleh pengguna.")
    finally:
        loop.close()
