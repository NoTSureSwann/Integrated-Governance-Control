import os
import sqlite3
from telemetry import TelemetryClient
from utils.logger import log_info, log_warning

def init_database():
    db_dir = "database"
    db_path = os.path.join(db_dir, "nexus_telemetry.db")
    
    log_info(f"Menginisialisasi database SQLite di: {db_path}")
    
    # Memanggil TelemetryClient untuk membuat direktori dan tabel secara otomatis
    client = TelemetryClient(db_path=db_path)
    
    if os.path.exists(db_path):
        log_info("Database SQLite berhasil diinisialisasi secara fisik!")
        # Verifikasi struktur tabel
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
                table_exists = cursor.fetchone()
                if table_exists:
                    log_info("Verifikasi Sukses: Tabel 'metrics' telah aktif.")
                else:
                    log_warning("Verifikasi Gagal: Tabel 'metrics' tidak ditemukan di database.")
        except Exception as e:
            log_warning(f"Error saat memverifikasi tabel database: {e}")
    else:
        log_warning("Gagal membuat berkas database di path tujuan.")

if __name__ == "__main__":
    init_database()
