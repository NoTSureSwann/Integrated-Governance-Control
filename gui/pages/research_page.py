import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QSplitter, QFrame
from PySide6.QtCore import Qt, QThread, Signal
import qtawesome as qta
from connectors.github_analyzer import GitHubAnalyzer
from memory.memory_manager import MemoryManager

class ResearchWorker(QThread):
    """
    Worker Thread untuk melakukan analisis repositori GitHub secara asinkron.
    """
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, github_url: str, mock: bool = True):
        super().__init__()
        self.github_url = github_url
        self.mock = mock

    def run(self):
        try:
            analyzer = GitHubAnalyzer(mock=self.mock)
            output = analyzer.analyze_repository(self.github_url)
            self.finished.emit(output)
        except Exception as e:
            self.error.emit(str(e))


class ResearchPage(QWidget):
    """
    Halaman Research Workspace.
    Mendukung upload dokumen lokal dan analisis repositori GitHub.
    """
    def __init__(self):
        super().__init__()
        self.memory = MemoryManager()
        self.worker = None
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header Page
        lbl_title = QLabel("🔬 Research Workspace")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(lbl_title)
        
        # Panel Input Dokumen/Repo
        input_frame = QFrame()
        input_frame.setStyleSheet("background-color: #252526; border-radius: 6px; border: 1px solid #333333;")
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(12)
        
        # Row 1: File Uploader
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Upload Research Document:"))
        self.txt_file_path = QLineEdit()
        self.txt_file_path.setReadOnly(True)
        self.txt_file_path.setPlaceholderText("Pilih berkas PDF, DOCX, CSV, Markdown, Python...")
        self.btn_browse = QPushButton(" Browse File")
        self.btn_browse.setIcon(qta.icon("fa5s.folder-open", color="white"))
        self.btn_browse.clicked.connect(self._browse_file)
        file_layout.addWidget(self.txt_file_path)
        file_layout.addWidget(self.btn_browse)
        input_layout.addLayout(file_layout)
        
        # Row 2: GitHub Repository Analyzer
        repo_layout = QHBoxLayout()
        repo_layout.addWidget(QLabel("GitHub Repository URL:  "))
        self.txt_repo_url = QLineEdit()
        self.txt_repo_url.setPlaceholderText("https://github.com/username/repository...")
        repo_layout.addWidget(self.txt_repo_url)
        input_layout.addLayout(repo_layout)
        
        # Row 3: Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_analyze = QPushButton(" Analyze Research / Repo")
        self.btn_analyze.setIcon(qta.icon("fa5s.brain", color="white"))
        self.btn_analyze.setFixedHeight(35)
        self.btn_analyze.clicked.connect(self._start_analysis)
        btn_layout.addWidget(self.btn_analyze)
        btn_layout.addStretch()
        input_layout.addLayout(btn_layout)
        
        layout.addWidget(input_frame)
        
        # Splitter untuk hasil analisis
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Panel Kiri: Paper Summary
        panel_left = QWidget()
        layout_left = QVBoxLayout(panel_left)
        layout_left.setContentsMargins(0, 0, 5, 0)
        layout_left.addWidget(QLabel("📝 Paper Summary & Repository Analysis:"))
        self.txt_summary = QTextEdit()
        self.txt_summary.setReadOnly(True)
        self.txt_summary.setPlaceholderText("Analysis results will be displayed here...")
        layout_left.addWidget(self.txt_summary)
        self.splitter.addWidget(panel_left)
        
        # Panel Kanan: Knowledge Graph (Entities & Relations)
        panel_right = QWidget()
        layout_right = QVBoxLayout(panel_right)
        layout_right.setContentsMargins(5, 0, 0, 0)
        layout_right.addWidget(QLabel("🕸️ Extracted Entities & Concept Relations:"))
        self.txt_graph = QTextEdit()
        self.txt_graph.setReadOnly(True)
        self.txt_graph.setPlaceholderText("Extracted knowledge concepts will be listed here...")
        layout_right.addWidget(self.txt_graph)
        self.splitter.addWidget(panel_right)
        
        layout.addWidget(self.splitter)
        
    def _browse_file(self):
        file_filter = "All Files (*);;Documents (*.pdf *.docx *.txt *.md);;Data & Code (*.csv *.json *.yaml *.py)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih Dokumen Riset", "", file_filter)
        if file_path:
            self.txt_file_path.setText(file_path)
            
    def _start_analysis(self):
        file_path = self.txt_file_path.text().strip()
        repo_url = self.txt_repo_url.text().strip()
        
        if not file_path and not repo_url:
            return
            
        self.btn_analyze.setEnabled(False)
        self.txt_summary.setText("Analyzing document/repository in background. Please wait...")
        self.txt_graph.clear()
        
        # Integrasi logs ke Bottom Panel
        main_win = self.window()
        if hasattr(main_win, 'bottom_panel'):
            main_win.bottom_panel.append_log(f"\n[RESEARCH]: Memulai analisis pada File: '{file_path}' | Repo: '{repo_url}'")
            
        if repo_url:
            # Jalankan analisis repositori asinkron
            import config
            self.worker = ResearchWorker(repo_url, mock=config.MOCK_MODE)
            self.worker.finished.connect(self._handle_repo_analysis_finished)
            self.worker.error.connect(self._handle_analysis_error)
            self.worker.start()
        else:
            # Simulasi analisis berkas lokal
            self._analyze_local_file(file_path)
            
    def _analyze_local_file(self, file_path: str):
        basename = os.path.basename(file_path)
        summary = f"""# Intisari Analisis Berkas: {basename}

- **Jenis Berkas**: Dokumen Lokal ({os.path.splitext(basename)[1].upper()})
- **Waktu Ekstraksi**: Real-time
- **Status Otorisasi**: Read-Only (Local Workspace)

## 1. Hasil Ekstraksi Utama
Berdasarkan penganalisis dokumen modular, berkas ini membahas struktur logis pemrograman Python. Struktur modular divalidasi berhasil mencegah kerumitan runtime.

## 2. Landasan Teori
- Pemisahan tanggung jawab (Parnas, 1972)
- Clean architecture dan modular by default
"""
        concepts = f"""[ENTITY] -> File: {basename}
[CONCEPT] -> Clean Code
[RELATION] -> File: {basename} -- implements --> Clean Code
[IMPORTANCE] -> High (Score 9)
"""
        self.txt_summary.setText(summary)
        self.txt_graph.setText(concepts)
        self.btn_analyze.setEnabled(True)
        
        # Simpan ke tabel research database
        self.memory.save_research("Local-Doc", f"Analisis berkas: {basename}", file_path)
        
        # Tambahkan ke knowledge base secara otomatis (Rule 10: Improve Continuously)
        self.memory.save_knowledge(f"Doc:{basename}", f"Ekstraksi konsep dari dokumen lokal {basename}.", file_path, "Research")

    def _handle_repo_analysis_finished(self, output: str):
        self.txt_summary.setText(output)
        
        # Ekstrak beberapa entitas contoh untuk divisualisasikan
        concepts = """[ENTITY] -> GitHub Repository
[CONCEPT] -> Modular Architecture
[RELATION] -> Repository -- implements --> Modular Architecture
[CONCEPT] -> SQLite Database
[RELATION] -> Repository -- uses --> SQLite Database
"""
        self.txt_graph.setText(concepts)
        self.btn_analyze.setEnabled(True)
        
        # Simpan hasil riset repositori ke database
        self.memory.save_research("Repo-Analysis", "Analisis struktur repositori GitHub", self.txt_repo_url.text().strip())
        self.memory.save_knowledge("GitHub-Repo", "Repositori sumber pembelajaran berizin.", self.txt_repo_url.text().strip(), "Connector")
        
        main_win = self.window()
        if hasattr(main_win, 'status_bar'):
            main_win.status_bar.showMessage("Analisis repositori berhasil diselesaikan!", 4000)

    def _handle_analysis_error(self, err: str):
        self.txt_summary.setText(f"**Error during analysis:**\n{err}")
        self.btn_analyze.setEnabled(True)
