import qtawesome as qta
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PySide6.QtCore import Qt

class TopToolbar(QWidget):
    """
    Komponen Top Toolbar untuk metrik dan quick actions.
    """
    def __init__(self, theme_manager=None):
        super().__init__()
        self.setObjectName("toolbar")
        self.theme_manager = theme_manager
        self.setFixedHeight(50)
        self._init_ui()
        
    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(15)
        
        # System Status Indicators
        self.lbl_model = self._create_status_label("fa5s.robot", "Model: Loading...")
        self.lbl_agent = self._create_status_label("fa5s.user-tie", "Agent: Idle")
        self.lbl_api = self._create_status_label("fa5s.wifi", "API: Checking...")
        self.lbl_cpu = self._create_status_label("fa5s.microchip", "CPU: 0%")
        self.lbl_ram = self._create_status_label("fa5s.memory", "RAM: 0%")
        
        self.refresh_status()
        
        layout.addWidget(self.lbl_model)
        layout.addWidget(self.lbl_agent)
        layout.addWidget(self.lbl_api)
        layout.addWidget(self.lbl_cpu)
        layout.addWidget(self.lbl_ram)
        
        layout.addStretch()
        
        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Knowledge/Memory...")
        self.search_bar.setFixedWidth(250)
        layout.addWidget(self.search_bar)
        
        # Quick Action Button
        self.btn_quick = QPushButton(" Quick Action")
        self.btn_quick.setIcon(qta.icon("fa5s.bolt", color="white"))
        layout.addWidget(self.btn_quick)
        
        # Theme Toggle Button
        self.btn_theme_toggle = QPushButton(" Toggle Theme")
        self.btn_theme_toggle.setIcon(qta.icon("fa5s.adjust", color="white"))
        if self.theme_manager:
            self.btn_theme_toggle.clicked.connect(self.theme_manager.toggle_theme)
        layout.addWidget(self.btn_theme_toggle)
        
    def _create_status_label(self, icon_name: str, text: str) -> QLabel:
        lbl = QLabel(text)
        # Akan ditangani oleh Qtawesome di update selanjutnya, atau menggunakan text
        # Untuk kesederhanaan, render text langsung dulu.
        return lbl
        
    def update_metrics(self, cpu: float, ram: float, agent: str):
        """Fungsi untuk dipanggil oleh Observability Service"""
        self.lbl_cpu.setText(f"CPU: {cpu:.1f}%")
        self.lbl_ram.setText(f"RAM: {ram:.1f}%")
        self.lbl_agent.setText(f"Agent: {agent}")

    def refresh_status(self):
        """Membaca konfigurasi global dan memperbarui status Toolbar."""
        import config
        # Active model display
        model_name = config.GROQ_MODEL
        if len(model_name) > 15:
            model_name = model_name[:12] + "..."
        self.lbl_model.setText(f"Model: {model_name}")
        
        # API Connection / Mock Display
        if config.MOCK_MODE:
            self.lbl_api.setText("API: Mock Mode")
            self.lbl_api.setStyleSheet("color: #FFB703; font-weight: bold;")
        else:
            errors = config.validate_config()
            if errors:
                self.lbl_api.setText("API: Invalid Keys")
                self.lbl_api.setStyleSheet("color: #FF4B4B; font-weight: bold;")
            else:
                self.lbl_api.setText("API: Live Connected")
                self.lbl_api.setStyleSheet("color: #00C250; font-weight: bold;")
