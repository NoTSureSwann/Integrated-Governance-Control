import sqlite3
import datetime
import os
import threading
from utils.logger import log_warning

class TelemetryClient:
    """
    Layer 16: OBSERVABILITY ENGINE
    Singleton Client untuk merekam metrik telemetry agent ke dalam SQLite database.
    Mendukung tracking CPU, RAM, GPU, Response Time, dan API Latency secara real-time.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path="database/nexus_telemetry.db"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TelemetryClient, cls).__new__(cls)
                cls._instance._init_db(db_path)
            return cls._instance

    def _init_db(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        agent_name TEXT NOT NULL,
                        model_name TEXT NOT NULL,
                        task_name TEXT,
                        response_time_ms REAL,
                        token_usage INTEGER,
                        cpu_usage REAL,
                        ram_usage REAL,
                        gpu_usage REAL,
                        api_latency REAL,
                        error_count INTEGER,
                        retry_count INTEGER,
                        success_rate REAL,
                        confidence_score REAL,
                        user_satisfaction REAL,
                        experiment_score REAL
                    )
                ''')
                conn.commit()
        except Exception as e:
            log_warning(f"Gagal menginisialisasi database telemetry: {e}")

    def log_event(self,
                  agent_name: str,
                  model_name: str,
                  task_name: str = "",
                  response_time_ms: float = 0.0,
                  token_usage: int = 0,
                  cpu_usage: float = 0.0,
                  ram_usage: float = 0.0,
                  gpu_usage: float = 0.0,
                  api_latency: float = 0.0,
                  error_count: int = 0,
                  retry_count: int = 0,
                  success_rate: float = 1.0,
                  confidence_score: float = 0.0,
                  user_satisfaction: float = 0.0,
                  experiment_score: float = 0.0):
        timestamp = datetime.datetime.now().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO metrics (
                        timestamp, agent_name, model_name, task_name, response_time_ms,
                        token_usage, cpu_usage, ram_usage, gpu_usage, api_latency,
                        error_count, retry_count, success_rate, confidence_score,
                        user_satisfaction, experiment_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (timestamp, agent_name, model_name, task_name, response_time_ms,
                      token_usage, cpu_usage, ram_usage, gpu_usage, api_latency,
                      error_count, retry_count, success_rate, confidence_score,
                      user_satisfaction, experiment_score))
                conn.commit()
        except Exception as e:
            log_warning(f"Gagal menyimpan telemetry event: {e}")
