from PySide6.QtWidgets import QStackedWidget, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from gui.pages.dashboard_page import DashboardPage
from gui.pages.chat_page import ChatPage
from gui.pages.settings_page import SettingsPage
from gui.pages.memory_page import MemoryPage
from gui.pages.research_page import ResearchPage
from gui.pages.knowledge_page import KnowledgePage
from gui.pages.english_page import EnglishPage
from gui.pages.plugins_page import PluginsPage
from gui.pages.datasets_page import DatasetsPage
from gui.pages.eda_page import EDAPage
from gui.pages.training_analysis_page import TrainingAnalysisPage

class PageRouter(QStackedWidget):
    """
    Mengelola pergantian halaman pada Center Workspace.
    """
    def __init__(self):
        super().__init__()
        self._pages = {}
        self._init_pages()
        
    def _init_pages(self):
        # Inisialisasi halaman-halaman utama
        self.add_page("dashboard", DashboardPage())
        self.add_page("chat", ChatPage())
        self.add_page("settings", SettingsPage())
        self.add_page("memory", MemoryPage())
        self.add_page("research", ResearchPage())
        self.add_page("knowledge", KnowledgePage())
        self.add_page("english", EnglishPage())
        self.add_page("plugins", PluginsPage())
        
        # New Data Engine Pages
        self.add_page("datasets", DatasetsPage())
        self.add_page("eda", EDAPage())
        self.add_page("training", TrainingAnalysisPage())
        
        # Halaman placeholder untuk yang belum diimplementasikan
        placeholders = [
            "experiments", 
            "repository", "logs"
        ]
        for route in placeholders:
            self.add_page(route, self._create_placeholder(route))
            
    def add_page(self, route_id: str, widget: QWidget):
        self._pages[route_id] = widget
        self.addWidget(widget)
        
    def switch_to(self, route_id: str):
        if route_id in self._pages:
            self.setCurrentWidget(self._pages[route_id])
            
    def _create_placeholder(self, route_id: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        lbl = QLabel(f"Page '{route_id.capitalize()}' is under construction.")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setObjectName("placeholder_label")
        layout.addWidget(lbl)
        return widget
