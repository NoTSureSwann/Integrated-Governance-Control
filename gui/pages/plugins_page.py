import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox
from PySide6.QtCore import Qt
import qtawesome as qta

class ConnectorConfigDialog(QDialog):
    """
    Dialog popup konfigurasi parameter konektor secara dinamis.
    """
    def __init__(self, connector_name: str, parent=None):
        super().__init__(parent)
        self.connector_name = connector_name
        self.setWindowTitle(f"Configure {connector_name}")
        self.setMinimumWidth(380)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.inputs = {}
        
        # Sediakan input fields yang berbeda berdasarkan jenis konektor
        if self.connector_name == "GitHub":
            self.inputs["GITHUB_TOKEN"] = QLineEdit()
            self.inputs["GITHUB_TOKEN"].setEchoMode(QLineEdit.Password)
            self.inputs["GITHUB_USERNAME"] = QLineEdit()
            form_layout.addRow("Personal Access Token:", self.inputs["GITHUB_TOKEN"])
            form_layout.addRow("Default Username:", self.inputs["GITHUB_USERNAME"])
            
        elif self.connector_name in ("PostgreSQL", "SQLite"):
            self.inputs["DB_HOST"] = QLineEdit()
            self.inputs["DB_HOST"].setPlaceholderText("localhost")
            self.inputs["DB_PORT"] = QLineEdit()
            self.inputs["DB_PORT"].setPlaceholderText("5432" if self.connector_name == "PostgreSQL" else "N/A")
            self.inputs["DB_NAME"] = QLineEdit()
            self.inputs["DB_USER"] = QLineEdit()
            self.inputs["DB_PASS"] = QLineEdit()
            self.inputs["DB_PASS"].setEchoMode(QLineEdit.Password)
            
            form_layout.addRow("Database Host:", self.inputs["DB_HOST"])
            form_layout.addRow("Database Port:", self.inputs["DB_PORT"])
            form_layout.addRow("Database Name:", self.inputs["DB_NAME"])
            form_layout.addRow("Username:", self.inputs["DB_USER"])
            form_layout.addRow("Password:", self.inputs["DB_PASS"])
            
        elif self.connector_name in ("ChromaDB", "FAISS", "Neo4j"):
            self.inputs["VECTOR_DB_URL"] = QLineEdit()
            self.inputs["VECTOR_DB_URL"].setPlaceholderText("http://localhost:8000")
            self.inputs["VECTOR_DB_API_KEY"] = QLineEdit()
            self.inputs["VECTOR_DB_API_KEY"].setEchoMode(QLineEdit.Password)
            form_layout.addRow("Server URL / Path:", self.inputs["VECTOR_DB_URL"])
            form_layout.addRow("API Key / Password:", self.inputs["VECTOR_DB_API_KEY"])
            
        elif self.connector_name == "Docker":
            self.inputs["DOCKER_HOST"] = QLineEdit()
            self.inputs["DOCKER_HOST"].setPlaceholderText("unix:///var/run/docker.sock")
            form_layout.addRow("Docker Host / Socket:", self.inputs["DOCKER_HOST"])
            
        else: # REST API
            self.inputs["API_BASE_URL"] = QLineEdit()
            self.inputs["API_BASE_URL"].setPlaceholderText("https://api.external-service.com")
            self.inputs["API_HEADER_KEY"] = QLineEdit()
            form_layout.addRow("API Endpoint URL:", self.inputs["API_BASE_URL"])
            form_layout.addRow("Authorization Header Key:", self.inputs["API_HEADER_KEY"])
            
        layout.addLayout(form_layout)
        
        # Load existing env values if present
        for key, field in self.inputs.items():
            field.setText(os.getenv(key, ""))
            
        # OK / Cancel
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_config_data(self) -> dict:
        return {key: field.text().strip() for key, field in self.inputs.items()}


class ConnectorCard(QFrame):
    """
    Kartu Visualisasi Modul Konektor.
    """
    def __init__(self, name: str, desc: str, icon_name: str):
        super().__init__()
        self.connector_name = name
        self.setStyleSheet(
            "background-color: #252526; border-radius: 6px; border: 1px solid #333333;"
        )
        self.setContentsMargins(15, 15, 15, 15)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header Row (Icon + Name)
        header = QHBoxLayout()
        header.setSpacing(10)
        
        self.lbl_icon = QLabel()
        self.lbl_icon.setPixmap(qta.icon(icon_name, color="#007ACC").pixmap(32, 32))
        header.addWidget(self.lbl_icon)
        
        self.lbl_name = QLabel(name)
        self.lbl_name.setStyleSheet("font-size: 15px; font-weight: bold; color: #FFFFFF;")
        header.addWidget(self.lbl_name)
        header.addStretch()
        
        # Status Badge
        self.lbl_status = QLabel("Inactive")
        self.lbl_status.setStyleSheet("background-color: #3E3E3E; color: #AAAAAA; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        header.addWidget(self.lbl_status)
        
        layout.addLayout(header)
        
        # Description
        self.lbl_desc = QLabel(desc)
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #888888; font-size: 12px; min-height: 40px;")
        layout.addWidget(self.lbl_desc)
        
        # Action Row
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        self.btn_configure = QPushButton(" Configure")
        self.btn_configure.setIcon(qta.icon("fa5s.wrench", color="white"))
        self.btn_configure.setStyleSheet("background-color: #3C3C3C; color: #DDDDDD;")
        action_layout.addWidget(self.btn_configure)
        layout.addLayout(action_layout)
        
    def set_status(self, is_active: bool):
        if is_active:
            self.lbl_status.setText("Active")
            self.lbl_status.setStyleSheet("background-color: #1B5E20; color: #00C250; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;")
        else:
            self.lbl_status.setText("Inactive")
            self.lbl_status.setStyleSheet("background-color: #3E3E3E; color: #AAAAAA; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;")


class PluginsPage(QWidget):
    """
    Halaman Plugin & Connector Manager.
    Menyusun 8 kartu konektor dalam susunan grid layout.
    """
    def __init__(self):
        super().__init__()
        self._init_ui()
        self.update_connector_statuses()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header Page
        lbl_title = QLabel("🔌 Plugin & Connector Store")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(lbl_title)
        
        # Grid Layout
        grid = QGridLayout()
        grid.setSpacing(15)
        
        self.connectors_info = [
            ("GitHub", "Membaca dan mengekstrak knowledge dari repositori publik.", "fa5b.github"),
            ("SQLite", "Konektor database SQLite lokal untuk penyimpanan riwayat memori.", "fa5s.database"),
            ("PostgreSQL", "Konektor eksternal untuk menyimpan memori ke server PostgreSQL.", "fa5s.server"),
            ("ChromaDB", "Konektor vector database untuk pencarian semantik (RAG).", "fa5s.project-diagram"),
            ("FAISS", "Pustaka pencarian semantik berkas lokal berbasis index FAISS.", "fa5s.map-signs"),
            ("Neo4j", "Database grafis untuk menyusun peta hubungan konsep (Knowledge Graph).", "fa5s.project-diagram"),
            ("Docker", "Connector terisolasi untuk eksekusi kode program di dalam kontainer.", "fa5b.docker"),
            ("REST API", "Melakukan integrasi dengan API external menggunakan protokol REST.", "fa5s.network-wired")
        ]
        
        self.cards = {}
        for idx, (name, desc, icon) in enumerate(self.connectors_info):
            card = ConnectorCard(name, desc, icon)
            # Hubungkan tombol configure ke fungsi popup
            card.btn_configure.clicked.connect(lambda checked=False, n=name: self._configure_connector(n))
            
            row = idx // 3
            col = idx % 3
            grid.addWidget(card, row, col)
            self.cards[name] = card
            
        layout.addLayout(grid)
        layout.addStretch()
        
    def update_connector_statuses(self):
        """Memeriksa variabel lingkungan untuk menyalakan/mematikan status kartu konektor."""
        # 1. GitHub status
        has_github = bool(os.getenv("GITHUB_TOKEN"))
        self.cards["GitHub"].set_status(has_github)
        
        # 2. SQLite status (selalu active karena database bawaan aktif)
        self.cards["SQLite"].set_status(True)
        
        # 3. PostgreSQL status
        has_postgres = bool(os.getenv("DB_HOST"))
        self.cards["PostgreSQL"].set_status(has_postgres)
        
        # 4. Vector DB status
        has_vector = bool(os.getenv("VECTOR_DB_URL"))
        self.cards["ChromaDB"].set_status(has_vector)
        self.cards["FAISS"].set_status(has_vector)
        self.cards["Neo4j"].set_status(has_vector)
        
        # 5. Docker status
        has_docker = bool(os.getenv("DOCKER_HOST"))
        self.cards["Docker"].set_status(has_docker)
        
        # 6. REST API status
        has_rest = bool(os.getenv("API_BASE_URL"))
        self.cards["REST API"].set_status(has_rest)

    def _configure_connector(self, name: str):
        dialog = ConnectorConfigDialog(name, self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_config_data()
            
            # Simpan data baru ke .env
            self._write_to_env(data)
            
            # Muat ulang variabel lingkungan di Python
            for k, v in data.items():
                os.environ[k] = v
                
            self.update_connector_statuses()
            
            main_win = self.window()
            if hasattr(main_win, 'status_bar'):
                main_win.status_bar.showMessage(f"Konektor '{name}' berhasil dikonfigurasi!", 4000)

    def _write_to_env(self, data: dict):
        env_path = ".env"
        lines = []
        
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
        env_dict = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env_dict[key.strip()] = val.strip()
                
        for key, val in data.items():
            env_dict[key] = val
            
        with open(env_path, "w", encoding="utf-8") as f:
            for key, val in env_dict.items():
                f.write(f"{key}={val}\n")
