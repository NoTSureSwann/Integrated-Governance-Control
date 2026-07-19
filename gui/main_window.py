from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt

from gui.widgets.sidebar import Sidebar
from gui.widgets.toolbar import TopToolbar
from gui.widgets.bottom_panel import BottomPanel
from gui.widgets.right_panel import RightPanel
from gui.router.page_router import PageRouter
from gui.theme import ThemeManager
from services.hook_manager import qt_hook_auth_bridge

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Nexus - AI Operating System")
        self.setMinimumSize(1200, 800)
        
        self._init_ui()
        self._connect_signals()
        
    def _init_ui(self):
        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Sidebar (Left)
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Splitter untuk memisahkan Workspace Utama dan Right Panel
        self.main_horizontal_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_horizontal_splitter)
        
        # Container Tengah (Toolbar + Center Workspace + Bottom Console)
        self.center_container = QWidget()
        center_layout = QVBoxLayout(self.center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        # Theme Manager
        self.theme_manager = ThemeManager()
        self.theme_manager.apply_theme()
        
        # Toolbar (Top)
        self.toolbar = TopToolbar(self.theme_manager)
        center_layout.addWidget(self.toolbar)
        
        # Splitter Vertikal untuk Center Workspace dan Bottom Panel
        self.center_vertical_splitter = QSplitter(Qt.Vertical)
        center_layout.addWidget(self.center_vertical_splitter)
        
        # Router (Center Workspace)
        self.router = PageRouter()
        self.center_vertical_splitter.addWidget(self.router)
        
        # Bottom Panel (Console)
        self.bottom_panel = BottomPanel()
        self.center_vertical_splitter.addWidget(self.bottom_panel)
        
        # Rasio awal Splitter Vertikal (70% workspace, 30% console)
        self.center_vertical_splitter.setSizes([700, 200])
        
        self.main_horizontal_splitter.addWidget(self.center_container)
        
        # 3. Right Panel (Activity/Tasks)
        self.right_panel = RightPanel()
        self.main_horizontal_splitter.addWidget(self.right_panel)
        
        # Rasio awal Splitter Horizontal
        self.main_horizontal_splitter.setSizes([900, 280])
        
        # Set default halaman ke Dashboard
        self.sidebar.set_active("dashboard")
        
        # Status Bar (Sprint 1 Requirement)
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Project Nexus OS | System Ready | SQLite DB: Active")
        
    def _connect_signals(self):
        # Hubungkan sinyal dari Sidebar ke Router
        self.sidebar.route_changed.connect(self.router.switch_to)
        
        # Hubungkan sinyal otorisasi Hook
        qt_hook_auth_bridge.auth_requested.connect(self._show_hook_auth_dialog)

    def _show_hook_auth_dialog(self, lifecycle: str, hook_name: str, event, result_list: list):
        """Membuka dialog persetujuan pengguna di thread utama Qt (Thread-safe)."""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Hook Authorization Request",
            f"Hook '{hook_name}' pada lifecycle '{lifecycle}' meminta otorisasi untuk mengakses/mengubah data.\n\n"
            "Izinkan eksekusi hook ini?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        result_list[0] = (reply == QMessageBox.Yes)
        # Buka pemblokiran thread latar belakang
        event.set()
