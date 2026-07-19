import qtawesome as qta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Signal, Qt

class Sidebar(QWidget):
    """
    Komponen Sidebar untuk navigasi utama Project Nexus.
    """
    # Signal yang dipancarkan ketika rute berubah
    route_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)
        
        # Logo/Title
        title = QLabel("PROJECT NEXUS")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #007ACC; padding-left: 10px;")
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Menu Items
        self.menus = {
            "dashboard": ("Dashboard", "fa5s.chart-pie"),
            "chat": ("Chat", "fa5s.comments"),
            "research": ("Research", "fa5s.microscope"),
            "english": ("English Trainer", "fa5s.language"),
            "knowledge": ("Knowledge", "fa5s.book"),
            "memory": ("Memory", "fa5s.brain"),
            "experiments": ("Experiments", "fa5s.flask"),
            "datasets": ("Datasets", "fa5s.database"),
            "eda": ("Exploratory Data", "fa5s.chart-bar"),
            "training": ("Training Analysis", "fa5s.chart-line"),
            "repository": ("Repository", "fa5b.github"),
            "plugins": ("Plugins", "fa5s.plug"),
            "settings": ("Settings", "fa5s.cog"),
            "logs": ("Logs", "fa5s.terminal")
        }
        
        self.buttons = {}
        for route_id, (label, icon_name) in self.menus.items():
            btn = QPushButton(f"  {label}")
            btn.setIcon(qta.icon(icon_name, color="white"))
            btn.setCheckable(True)
            # Menghubungkan fungsi klik dengan signal
            btn.clicked.connect(lambda checked, r=route_id: self._on_menu_clicked(r))
            
            self.buttons[route_id] = btn
            layout.addWidget(btn)
            
        # Spacer at bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
    def _on_menu_clicked(self, route_id: str):
        """Handler saat tombol menu diklik. Memastikan gaya radio-button."""
        for r_id, btn in self.buttons.items():
            if r_id != route_id:
                btn.setChecked(False)
            else:
                btn.setChecked(True)
                
        self.route_changed.emit(route_id)
        
    def set_active(self, route_id: str):
        """Set menu aktif secara programatik."""
        if route_id in self.buttons:
            self._on_menu_clicked(route_id)
