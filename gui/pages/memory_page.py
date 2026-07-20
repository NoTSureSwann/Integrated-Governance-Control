from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QLabel, QMessageBox
from PySide6.QtCore import Qt
import qtawesome as qta
from adapters.database.memory_adapter import MemoryRepositoryAdapter

class MemoryPage(QWidget):
    """
    Halaman Visualizer Memori Utama untuk menelusuri memori asisten AI
    (Conversations, Knowledge, Research, dan Long Term).
    """
    def __init__(self):
        super().__init__()
        self.memory = MemoryRepositoryAdapter()
        self._init_ui()
        self._seed_mock_data_if_empty()
        self.load_all_memories()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header Page
        header_layout = QHBoxLayout()
        lbl_title = QLabel("🧠 Nexus Memory Explorer")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        
        # Refresh Button
        self.btn_refresh = QPushButton(" Refresh")
        self.btn_refresh.setIcon(qta.icon("fa5s.sync", color="white"))
        self.btn_refresh.clicked.connect(self.load_all_memories)
        header_layout.addWidget(self.btn_refresh)
        
        # Clear Button
        self.btn_clear = QPushButton(" Clear All Memory")
        self.btn_clear.setIcon(qta.icon("fa5s.trash-alt", color="white"))
        self.btn_clear.setStyleSheet("background-color: #D32F2F;")
        self.btn_clear.clicked.connect(self._clear_all_memory_prompt)
        header_layout.addWidget(self.btn_clear)
        
        layout.addLayout(header_layout)
        
        # QTabWidget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #333333; background: #252526; border-radius: 4px; }"
            "QTabBar::tab { background: #2D2D2D; color: #888888; padding: 10px 15px; border: 1px solid #333333; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }"
            "QTabBar::tab:selected { background: #252526; color: #FFFFFF; border-bottom: 2px solid #007ACC; }"
        )
        
        # 1. Tab Conversations
        self.table_conv = self._create_styled_table(["Role", "Message Content", "Timestamp"])
        self.tabs.addTab(self.table_conv, "Conversation Memory")
        
        # 2. Tab Knowledge
        self.table_know = self._create_styled_table(["Concept Key", "Definition / Value", "Source", "Category", "Timestamp"])
        self.tabs.addTab(self.table_know, "Knowledge Memory")
        
        # 3. Tab Research
        self.table_res = self._create_styled_table(["Task ID", "Research Summary", "Files Referenced", "Timestamp"])
        self.tabs.addTab(self.table_res, "Research Memory")
        
        # 4. Tab Long Term
        self.table_lt = self._create_styled_table(["Concept", "Core Detail", "Importance Score", "Timestamp"])
        self.tabs.addTab(self.table_lt, "Long Term Memory")
        
        layout.addWidget(self.tabs)
        
    def _create_styled_table(self, headers: list) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # Menyesuaikan kolom konten agar text wrap lebih rapi
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents) if len(headers) > 2 else None
        
        table.setStyleSheet(
            "QTableWidget { background-color: #252526; gridline-color: #333333; border: none; }"
            "QHeaderView::section { background-color: #2D2D30; color: #CCCCCC; border: 1px solid #333333; padding: 6px; }"
            "QTableWidget::item { color: #CCCCCC; padding: 5px; }"
        )
        return table
        
    def _seed_mock_data_if_empty(self):
        """Menyisipkan data contoh visual (seeding) jika database baru dibuat (kosong)."""
        history = self.memory.get_conversation_history()
        if not history:
            # Seed Conversations
            self.memory.save_message("user", "Bagaimana konsep arsitektur modular Project Nexus?")
            self.memory.save_message("assistant", "Project Nexus dibangun menggunakan 22 layer modular. Layer 1-2 membagi UI dan Supervisor routing, sementara modul backend bekerja secara asinkron.")
            
            # Seed Knowledge
            self.memory.save_knowledge("In-Memory Optimization", "Metode pemetaan cache tabel telemetri secara penuh di dalam memori RAM untuk akses O(1).", "Research Paper", "Database")
            self.memory.save_knowledge("Consensus Process", "Validasi consensus silang antara Groq dan Kimi ketika menemukan kontradiksi data.", "SIGMA OS Spec", "Decision Engine")
            
            # Seed Research
            self.memory.save_research("Task-01", "Evaluasi efisiensi RAM pada polling visualizer PySide6", "gui/widgets/line_chart.py")
            
            # Seed Long Term
            self.memory.save_long_term("Human Approval Rule", "Melarang otomatisasi destruktif tanpa adanya prompt otorisasi manual dari User.", 10)
            self.memory.save_long_term("Accurate Coding Priority", "Memprioritaskan akurasi sintaksis daripada kecepatan eksekusi kode Groq.", 8)

    def load_all_memories(self):
        """Memuat data dari SQLite ke masing-masing tabel widget."""
        # 1. Load Conversations
        convs = self.memory.get_conversation_history()
        self.table_conv.setRowCount(len(convs))
        for idx, r in enumerate(convs):
            self.table_conv.setItem(idx, 0, QTableWidgetItem(r[0].upper() if r[0] else ""))
            self.table_conv.setItem(idx, 1, QTableWidgetItem(r[1] if r[1] else ""))
            self.table_conv.setItem(idx, 2, QTableWidgetItem(r[2].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[2], 'strftime') else str(r[2]) if r[2] is not None else ""))
            
        # 2. Load Knowledge
        knows = self.memory.get_all_knowledge()
        self.table_know.setRowCount(len(knows))
        for idx, r in enumerate(knows):
            # key, value, source, category, timestamp
            self.table_know.setItem(idx, 0, QTableWidgetItem(r[0] if r[0] else ""))
            self.table_know.setItem(idx, 1, QTableWidgetItem(r[1] if r[1] else ""))
            self.table_know.setItem(idx, 2, QTableWidgetItem(r[2] if r[2] else ""))
            self.table_know.setItem(idx, 3, QTableWidgetItem(r[3] if r[3] else ""))
            self.table_know.setItem(idx, 4, QTableWidgetItem(r[4].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[4], 'strftime') else str(r[4]) if r[4] is not None else ""))
            
        # 3. Load Research
        res = self.memory.get_all_research()
        self.table_res.setRowCount(len(res))
        for idx, r in enumerate(res):
            self.table_res.setItem(idx, 0, QTableWidgetItem(r[0] if r[0] else ""))
            self.table_res.setItem(idx, 1, QTableWidgetItem(r[1] if r[1] else ""))
            self.table_res.setItem(idx, 2, QTableWidgetItem(r[2] if r[2] else ""))
            self.table_res.setItem(idx, 3, QTableWidgetItem(r[3].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[3], 'strftime') else str(r[3]) if r[3] is not None else ""))
            
        # 4. Load Long Term
        lts = self.memory.get_all_long_term()
        self.table_lt.setRowCount(len(lts))
        for idx, r in enumerate(lts):
            self.table_lt.setItem(idx, 0, QTableWidgetItem(r[0] if r[0] else ""))
            self.table_lt.setItem(idx, 1, QTableWidgetItem(r[1] if r[1] else ""))
            self.table_lt.setItem(idx, 2, QTableWidgetItem(str(r[2]) if r[2] is not None else ""))
            self.table_lt.setItem(idx, 3, QTableWidgetItem(r[3].strftime("%Y-%m-%d %H:%M:%S") if hasattr(r[3], 'strftime') else str(r[3]) if r[3] is not None else ""))

    def _clear_all_memory_prompt(self):
        reply = QMessageBox.question(
            self, "Clear Memory", 
            "Apakah Anda yakin ingin menghapus seluruh database memori?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.memory.clear_all_memory()
            self.load_all_memories()
            main_win = self.window()
            if hasattr(main_win, 'status_bar'):
                main_win.status_bar.showMessage("Database memori berhasil dikosongkan secara permanen.", 4000)
