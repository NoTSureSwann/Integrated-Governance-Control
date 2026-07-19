import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QFormLayout, QFrame
from PySide6.QtCore import Qt
import qtawesome as qta
import config

class SettingsPage(QWidget):
    """
    Halaman Pengaturan untuk konfigurasi API Key, Pilihan Model, dan Mode Simulasi.
    """
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load_current_settings()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header Page
        lbl_title = QLabel("⚙️ System Settings & Router")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(lbl_title)
        
        # Form Container
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #252526; border-radius: 6px; border: 1px solid #333333;")
        form_layout = QFormLayout(form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)
        
        # Form Fields
        self.txt_groq_key = QLineEdit()
        self.txt_groq_key.setEchoMode(QLineEdit.Password)
        self.txt_groq_key.setPlaceholderText("Masukkan Groq API Key...")
        
        self.txt_groq_model = QLineEdit()
        self.txt_groq_model.setPlaceholderText("llama-3.3-70b-versatile")
        
        self.txt_kimi_key = QLineEdit()
        self.txt_kimi_key.setEchoMode(QLineEdit.Password)
        self.txt_kimi_key.setPlaceholderText("Masukkan Kimi API Key...")
        
        self.txt_kimi_model = QLineEdit()
        self.txt_kimi_model.setPlaceholderText("kimi-k2")
        
        self.txt_kimi_url = QLineEdit()
        self.txt_kimi_url.setPlaceholderText("https://api.moonshot.cn/v1")
        
        self.chk_mock = QCheckBox(" Aktifkan Mock Mode (Simulasi offline tanpa hit API)")
        self.chk_mock.setStyleSheet("color: #CCCCCC; font-size: 13px;")
        
        # Add to form layout
        form_layout.addRow(QLabel("<b>GROQ SETTINGS</b>"))
        form_layout.addRow("Groq API Key:", self.txt_groq_key)
        form_layout.addRow("Groq Model:", self.txt_groq_model)
        
        form_layout.addRow(QLabel("<br><b>KIMI SETTINGS</b>"))
        form_layout.addRow("Kimi API Key:", self.txt_kimi_key)
        form_layout.addRow("Kimi Model:", self.txt_kimi_model)
        form_layout.addRow("Kimi Base URL:", self.txt_kimi_url)
        
        form_layout.addRow(QLabel("<br><b>ROUTER MODE</b>"))
        form_layout.addRow("", self.chk_mock)
        
        layout.addWidget(form_frame)
        
        # Control Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton(" Save Configurations")
        self.btn_save.setIcon(qta.icon("fa5s.save", color="white"))
        self.btn_save.setFixedHeight(35)
        self.btn_save.clicked.connect(self._save_settings)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
    def _load_current_settings(self):
        """Memuat data saat ini dari config ke dalam Input Field."""
        self.txt_groq_key.setText(config.GROQ_API_KEY)
        self.txt_groq_model.setText(config.GROQ_MODEL)
        self.txt_kimi_key.setText(config.KIMI_API_KEY)
        self.txt_kimi_model.setText(config.KIMI_MODEL)
        self.txt_kimi_url.setText(config.KIMI_BASE_URL)
        self.chk_mock.setChecked(config.MOCK_MODE)
        
    def _save_settings(self):
        # 1. Update variabel di Memori
        config.GROQ_API_KEY = self.txt_groq_key.text().strip()
        config.GROQ_MODEL = self.txt_groq_model.text().strip() or "llama-3.3-70b-versatile"
        config.KIMI_API_KEY = self.txt_kimi_key.text().strip()
        config.KIMI_MODEL = self.txt_kimi_model.text().strip() or "kimi-k2"
        config.KIMI_BASE_URL = self.txt_kimi_url.text().strip() or "https://api.moonshot.cn/v1"
        config.MOCK_MODE = self.chk_mock.isChecked()
        
        # 2. Tulis secara fisik ke file `.env`
        self._write_to_env({
            "GROQ_API_KEY": config.GROQ_API_KEY,
            "GROQ_MODEL": config.GROQ_MODEL,
            "KIMI_API_KEY": config.KIMI_API_KEY,
            "KIMI_MODEL": config.KIMI_MODEL,
            "KIMI_BASE_URL": config.KIMI_BASE_URL,
            "MOCK_MODE": str(config.MOCK_MODE)
        })
        
        # 3. Validasi & Berikan Feedback di Status Bar Jendela Utama
        main_win = self.window()
        if hasattr(main_win, 'status_bar') and hasattr(main_win, 'toolbar'):
            errors = config.validate_config()
            if errors and not config.MOCK_MODE:
                main_win.status_bar.showMessage("Peringatan: API Key belum lengkap untuk mode LIVE!", 5000)
            else:
                main_win.status_bar.showMessage("Pengaturan berhasil disimpan dan diaktifkan!", 4000)
                
            # Trigger refresh status Toolbar atas secara instan
            main_win.toolbar.refresh_status()

    def _write_to_env(self, data: dict):
        env_path = ".env"
        lines = []
        
        # Baca berkas .env lama jika ada
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
        # Parse data .env menjadi dictionary
        env_dict = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env_dict[key.strip()] = val.strip()
                
        # Perbarui dengan data baru
        for key, val in data.items():
            env_dict[key] = val
            
        # Tulis kembali berkas .env secara rapi
        with open(env_path, "w", encoding="utf-8") as f:
            for key, val in env_dict.items():
                f.write(f"{key}={val}\n")
