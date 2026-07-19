from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

class BottomPanel(QWidget):
    """
    Komponen Bottom Panel untuk Console, Logs, Errors, dan Warnings.
    """
    def __init__(self):
        super().__init__()
        self.setObjectName("bottomPanel")
        self.setFixedHeight(200) # Bisa di-resize menggunakan QSplitter nantinya
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        lbl_title = QLabel("Console / Logs")
        lbl_title.setStyleSheet("color: #0E639C; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        self.console_output = QTextEdit()
        self.console_output.setObjectName("consoleText")
        self.console_output.setReadOnly(True)
        self.console_output.append("Project Nexus OS Initialized...")
        self.console_output.append("Waiting for Agent Activity...")
        
        layout.addWidget(self.console_output)
        
    def append_log(self, text: str):
        """Tambahkan teks ke dalam console."""
        self.console_output.append(text)
        # Auto-scroll ke bawah
        sb = self.console_output.verticalScrollBar()
        sb.setValue(sb.maximum())
