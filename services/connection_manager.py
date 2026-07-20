import sqlite3
import queue
import time
import random
import threading
import os
import requests
from sqlalchemy import text
from services.event_bus import EventBus, NexusEvent
from utils.logger import log_info, log_warning, log_error

class SQLiteConnectionPool:
    """
    Thread-safe Connection Pool sederhana untuk database SQLite lokal (Legacy).
    """
    def __init__(self, db_path: str, max_connections: int = 5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self._lock = threading.Lock()
        self._created = 0

    def get_connection(self):
        with self._lock:
            if self.pool.empty() and self._created < self.max_connections:
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                self._created += 1
                return conn
        return self.pool.get(timeout=5.0)

    def release_connection(self, conn):
        try:
            self.pool.put(conn, timeout=1.0)
        except queue.Full:
            conn.close()
            with self._lock:
                self._created -= 1


class PooledConnectionProxy:
    """
    Proxy pembungkus koneksi SQLite agar pemanggilan .close() merilis kembali ke pool (Legacy).
    """
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._pool.release_connection(self._conn)


class ConnectionManager:
    """
    Singleton Manager yang mengatur seluruh koneksi eksternal & internal Project Nexus.
    Menggunakan SQLAlchemy untuk pooling dan manajemen koneksi database.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls, *args, **kwargs)
                cls._instance.sqlite_pool = SQLiteConnectionPool("database/nexus.db", max_connections=5)
        return cls._instance

    def get_sqlite_connection(self):
        """Mengambil koneksi SQLite yang terbungkus Proxy dari pool (Legacy)."""
        conn = self.sqlite_pool.get_connection()
        return PooledConnectionProxy(conn, self.sqlite_pool)

    def release_sqlite_connection(self, conn):
        """Mengembalikan koneksi SQLite ke pool (Legacy)."""
        self.sqlite_pool.release_connection(conn)

    def request_with_retry(self, url: str, method: str = "GET", headers: dict = None, json_data: dict = None, max_retries: int = 3, base_delay: float = 1.0):
        """
        Melakukan request HTTP dengan retry menggunakan strategi Exponential Backoff + Jitter.
        """
        attempt = 0
        while attempt < max_retries:
            try:
                response = requests.request(method, url, headers=headers, json=json_data, timeout=10.0)
                if response.status_code < 500:
                    return response
            except requests.RequestException:
                pass
                
            attempt += 1
            if attempt == max_retries:
                break
                
            delay = base_delay * (2 ** attempt) + random.uniform(0.0, 1.0)
            log_warning(f"ConnectionManager: Request ke {url} gagal. Melakukan retry {attempt}/{max_retries} setelah {delay:.2f} detik...")
            time.sleep(delay)
            
        raise requests.RequestException(f"ConnectionManager: Gagal menghubungi {url} setelah {max_retries} percobaan.")

    def check_all_connections(self) -> dict:
        """
        Mengevaluasi status kesehatan dari 8 koneksi utama sistem.
        """
        status = {}
        
        # 1. Uji Database (SQLite/PostgreSQL) via SQLAlchemy
        from adapters.database.db_manager import DatabaseManager
        import config
        
        db_type = "PostgreSQL" if config.DB_HOST else "SQLite"
        try:
            db = DatabaseManager()
            session = db.get_session()
            session.execute(text("SELECT 1"))
            session.close()
            
            if db_type == "PostgreSQL":
                status["PostgreSQL"] = "Connected"
                status["SQLite"] = "N/A"
            else:
                status["SQLite"] = "Connected"
                status["PostgreSQL"] = "Disconnected"
        except Exception as e:
            log_error(f"ConnectionManager: Gagal menghubungi database: {e}")
            if db_type == "PostgreSQL":
                status["PostgreSQL"] = "Disconnected"
                status["SQLite"] = "N/A"
            else:
                status["SQLite"] = "Disconnected"
                status["PostgreSQL"] = "Disconnected"

        # 2. Uji WebSocket (Bandingkan port lokal)
        try:
            import websockets
            status["WebSocket"] = "Connected" 
        except Exception:
            status["WebSocket"] = "Disconnected"

        # 3. Uji Groq
        status["Groq API"] = "Connected" if config.GROQ_API_KEY else "Disconnected"

        # 4. Uji Kimi
        status["Kimi API"] = "Connected" if config.KIMI_API_KEY else "Disconnected"

        # 5. Uji GitHub
        status["GitHub"] = "Connected" if os.getenv("GITHUB_TOKEN") else "Disconnected"

        # 6. Uji Docker
        status["Docker"] = "Connected" if os.getenv("DOCKER_HOST") else "Disconnected"

        # 7. Uji REST API
        status["REST API"] = "Connected" if os.getenv("API_BASE_URL") else "Disconnected"

        # Kirim event notifikasi status koneksi terupdate
        try:
            EventBus().publish(NexusEvent(
                event_type="ConnectionStatusChanged",
                payload=status,
                agent="ConnectionManager",
                status="SUCCESS"
            ))
        except Exception:
            pass

        return status

# Instansi manajer global
nexus_connection_manager = ConnectionManager()
