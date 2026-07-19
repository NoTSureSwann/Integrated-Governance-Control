from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QSplitter, QDialog, QFormLayout, QDialogButtonBox, QMessageBox
from PySide6.QtCore import Qt
import qtawesome as qta
from memory.memory_manager import MemoryManager

class AddConceptDialog(QDialog):
    """
    Dialog Popup Form untuk menambahkan konsep baru ke basis pengetahuan.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Concept")
        self.setMinimumWidth(400)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        self.txt_key = QLineEdit()
        self.txt_key.setPlaceholderText("Contoh: RAG Optimization")
        
        self.txt_value = QTextEdit()
        self.txt_value.setPlaceholderText("Definisi atau penjelasan mendalam konsep...")
        self.txt_value.setMaximumHeight(150)
        
        self.txt_source = QLineEdit()
        self.txt_source.setPlaceholderText("Contoh: Wikipedia, Research Paper")
        
        self.txt_category = QLineEdit()
        self.txt_category.setPlaceholderText("Contoh: AI, Software Engineering")
        
        form_layout.addRow("Concept Key:", self.txt_key)
        form_layout.addRow("Definition / Value:", self.txt_value)
        form_layout.addRow("Source:", self.txt_source)
        form_layout.addRow("Category:", self.txt_category)
        
        layout.addLayout(form_layout)
        
        # Dialog Buttons (Save / Cancel)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_data(self) -> dict:
        return {
            "key": self.txt_key.text().strip(),
            "value": self.txt_value.toPlainText().strip(),
            "source": self.txt_source.text().strip(),
            "category": self.txt_category.text().strip()
        }


class KnowledgePage(QWidget):
    """
    Halaman Knowledge (Wiki basis pengetahuan).
    Mendukung pencarian dinamis, detail Markdown, dan popup tambah data.
    """
    def __init__(self):
        super().__init__()
        self.memory = MemoryManager()
        self._init_ui()
        self.load_knowledge_list()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header Page
        lbl_title = QLabel("📚 Nexus Knowledge Wiki")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(lbl_title)
        
        # Search & Add Row
        search_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Cari konsep pengetahuan...")
        self.txt_search.textChanged.connect(self.filter_knowledge_list)
        search_layout.addWidget(self.txt_search)
        
        self.btn_add = QPushButton(" Add Concept")
        self.btn_add.setIcon(qta.icon("fa5s.plus", color="white"))
        self.btn_add.clicked.connect(self._open_add_concept_dialog)
        search_layout.addWidget(self.btn_add)
        
        layout.addLayout(search_layout)
        
        # Splitter untuk List-Detail
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #333333; }")
        
        # Panel Kiri (List)
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            "QListWidget { background-color: #252526; border: 1px solid #333333; border-radius: 4px; padding: 5px; }"
            "QListWidget::item { color: #CCCCCC; padding: 8px; border-radius: 4px; }"
            "QListWidget::item:hover { background-color: #2A2D2E; }"
            "QListWidget::item:selected { background-color: #0E639C; color: #FFFFFF; }"
        )
        self.list_widget.currentItemChanged.connect(self._on_concept_selected)
        self.splitter.addWidget(self.list_widget)
        
        # Panel Kanan (Detail Viewer)
        self.detail_viewer = QTextEdit()
        self.detail_viewer.setReadOnly(True)
        self.detail_viewer.setStyleSheet(
            "QTextEdit { background-color: #1E1E1E; border: 1px solid #333333; border-radius: 4px; padding: 15px; }"
        )
        self.splitter.addWidget(self.detail_viewer)
        
        # Set Ratio awal splitter (30% list, 70% detail)
        self.splitter.setSizes([300, 700])
        
        layout.addWidget(self.splitter)
        
        # Menyimpan raw data knowledge untuk pencarian
        self.all_knowledge = []

    def load_knowledge_list(self):
        """Memuat daftar konsep dari SQLite."""
        self.list_widget.clear()
        self.all_knowledge = self.memory.get_all_knowledge()
        
        for k in self.all_knowledge:
            self.list_widget.addItem(k[0]) # k[0] adalah Key Konsep
            
        if self.all_knowledge:
            self.list_widget.setCurrentRow(0)
        else:
            self.detail_viewer.setHtml("<span style='color: #888888;'>Knowledge base is empty. Click 'Add Concept' to create one.</span>")

    def _on_concept_selected(self, current_item, previous_item):
        if not current_item:
            return
            
        concept_key = current_item.text()
        # Temukan data konsep di list memori
        concept_data = next((k for k in self.all_knowledge if k[0] == concept_key), None)
        
        if concept_data:
            # key, value, source, category, timestamp
            key, val, src, cat, time_str = concept_data
            
            formatted_val = val.replace('\n', '<br>')
            html = f"""
            <h2 style="color: #007ACC; margin-top: 0px;">{key}</h2>
            <p style="color: #888888; font-size: 11px;">
                <b>Category:</b> {cat or 'Uncategorized'} | 
                <b>Source:</b> {src or 'N/A'} | 
                <b>Saved:</b> {time_str}
            </p>
            <hr style="border: 1px solid #333333; margin-bottom: 15px;">
            <div style="color: #D4D4D4; line-height: 1.5; font-size: 13px;">
                {formatted_val}
            </div>
            """
            self.detail_viewer.setHtml(html)

    def filter_knowledge_list(self):
        """Menyaring konsep di list berdasarkan input pencarian."""
        query = self.txt_search.text().lower()
        self.list_widget.clear()
        
        filtered = [k for k in self.all_knowledge if query in k[0].lower() or query in k[1].lower()]
        
        for k in filtered:
            self.list_widget.addItem(k[0])
            
        if filtered:
            self.list_widget.setCurrentRow(0)
        else:
            self.detail_viewer.setHtml("<span style='color: #888888;'>No matching concepts found.</span>")

    def _open_add_concept_dialog(self):
        dialog = AddConceptDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["key"] or not data["value"]:
                QMessageBox.warning(self, "Validation Error", "Concept Key dan Definition tidak boleh kosong!")
                return
                
            self.memory.save_knowledge(
                data["key"], data["value"], data["source"], data["category"]
            )
            
            main_win = self.window()
            if hasattr(main_win, 'status_bar'):
                main_win.status_bar.showMessage(f"Konsep '{data['key']}' berhasil disimpan!", 4000)
                
            self.load_knowledge_list()
