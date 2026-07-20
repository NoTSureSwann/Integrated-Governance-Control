import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
import config
from utils.logger import log_info, log_error

Base = declarative_base()

# --- SQLAlchemy ORM Models ---

class Conversation(Base):
    __tablename__ = 'conversations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())

class Knowledge(Base):
    __tablename__ = 'knowledge'
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), nullable=False, unique=True)
    value = Column(Text, nullable=False)
    source = Column(String(255))
    category = Column(String(100))
    timestamp = Column(DateTime, default=func.now())

class Research(Base):
    __tablename__ = 'research'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    files_referenced = Column(Text)
    timestamp = Column(DateTime, default=func.now())

class LongTerm(Base):
    __tablename__ = 'long_term'
    id = Column(Integer, primary_key=True, autoincrement=True)
    concept = Column(String(255), nullable=False, unique=True)
    detail = Column(Text, nullable=False)
    importance_score = Column(Integer, default=5)
    timestamp = Column(DateTime, default=func.now())

class EnglishProgress(Base):
    __tablename__ = 'english_progress'
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(10), nullable=False)
    vocab_score = Column(Integer, default=50)
    grammar_score = Column(Integer, default=50)
    writing_score = Column(Integer, default=50)
    timestamp = Column(DateTime, default=func.now())

class GithubIndex(Base):
    __tablename__ = 'github_index'
    id = Column(Integer, primary_key=True, autoincrement=True)
    repo_url = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)
    content = Column(Text)
    hash = Column(String(100))
    indexed_at = Column(DateTime, default=func.now())

class DatasetMetadata(Base):
    __tablename__ = 'dataset_metadata'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_name = Column(String(255), nullable=False, unique=True)
    author = Column(String(100))
    license = Column(String(50))
    version = Column(String(20), default="1.0.0")
    language = Column(String(20))
    description = Column(Text)
    source = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class DatabaseManager:
    """
    Layer 10: DATABASE ENGINE
    Mengelola inisialisasi, engine pooling, dan session untuk SQLite & PostgreSQL via SQLAlchemy.
    """
    def __init__(self, db_path="database/nexus.db"):
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        self._init_db()

    def _init_db(self):
        # Tentukan Connection String
        if config.DB_HOST and config.DB_NAME and config.DB_USER:
            # Mode Produksi (PostgreSQL)
            url = f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
            log_info("DatabaseManager: Menggunakan PostgreSQL (Produksi).")
        else:
            # Mode Pengembangan (SQLite)
            db_dir = os.path.dirname(os.path.abspath(self.db_path))
            os.makedirs(db_dir, exist_ok=True)
            url = f"sqlite:///{self.db_path}"
            log_info(f"DatabaseManager: Menggunakan SQLite (Pengembangan) di '{self.db_path}'.")

        try:
            # Buat engine
            self.engine = create_engine(url, pool_pre_ping=True)
            # Buat semua tabel
            Base.metadata.create_all(self.engine)
            # Inisialisasi session factory
            self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
            log_info("DatabaseManager: Koneksi database berhasil diinisialisasi via SQLAlchemy.")
        except Exception as e:
            log_error(f"DatabaseManager: Gagal menginisialisasi database: {e}")

    def get_session(self):
        """Mengambil session database baru untuk operasi ORM."""
        if not self.SessionLocal:
            raise RuntimeError("DatabaseManager: Session factory belum diinisialisasi.")
        return self.SessionLocal()

    def get_connection(self):
        """
        Mengambil raw connection untuk kompatibilitas DB-API.
        Penting untuk modul legacy yang menggunakan cursor manual.
        """
        if not self.engine:
            raise RuntimeError("DatabaseManager: Database engine belum aktif.")
        return self.engine.raw_connection()
