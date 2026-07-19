import json
import re
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QProgressBar, QTabWidget, QFrame
from PySide6.QtCore import Qt, QThread, Signal
import qtawesome as qta
from memory.memory_manager import MemoryManager
from agents.english_tutor import EnglishTutorAgent
import config
from utils.logger import log_info

class EnglishTutorWorker(QThread):
    """
    Worker Thread untuk melakukan analisis tata bahasa secara asinkron.
    """
    finished = Signal(str, dict) # feedback_text, scores_dict
    error = Signal(str)

    def __init__(self, text_to_check: str, mock: bool = True):
        super().__init__()
        self.text_to_check = text_to_check
        self.mock = mock

    def run(self):
        try:
            agent = EnglishTutorAgent()
            response = agent.run(context={}, user_prompt=self.text_to_check, mock=self.mock)
            
            # Cari block JSON di dalam teks respon
            scores = {"level": "B2", "vocab_score": 60, "grammar_score": 60, "writing_score": 60}
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                try:
                    scores = json.loads(match.group(0))
                    # Bersihkan json block dari response agar lebih rapi untuk dibaca pengguna
                    response = response.replace(match.group(0), "").strip()
                except Exception:
                    pass
                    
            self.finished.emit(response, scores)
        except Exception as e:
            self.error.emit(str(e))

    def _run_mock(self):
        # Simulasi deteksi kesalahan tata bahasa sederhana
        text = self.text_to_check.lower()
        
        feedback = f"""# English Writing & Grammar Assessment

- **Teks Input**: "{self.text_to_check}"
- **Status Analisis**: Offline Simulation (Mock)

## 1. Koreksi Tata Bahasa (Grammar Corrections)
"""
        
        grammar_score = 75
        vocab_score = 70
        writing_score = 72
        level = "B2"
        
        if "don't" in text and ("he" in text or "she" in text or "it" in text):
            feedback += "- *Kesalahan*: 'He don't / She don't'\n- *Koreksi*: 'He doesn't / She doesn't'\n- *Penjelasan*: Subject ketiga tunggal (He/She/It) menggunakan auxiliary verb 'does not' (doesn't), bukan 'do not' (don't).\n\n"
            grammar_score = 55
            level = "B1"
        else:
            feedback += "Tidak ditemukan kesalahan tata bahasa fatal yang terdeteksi secara otomatis dalam mode offline.\n\n"
            
        feedback += """## 2. Saran Kosakata (Vocabulary Suggestions)
- Cobalah menggunakan kata-kata yang lebih spesifik untuk konteks akademis/teknis. 
  Contoh: ganti 'make' dengan 'develop' atau 'implement' saat berbicara tentang pembuatan kode program.

## 3. Rekomendasi
- Teruskan menulis secara aktif dan saksikan peningkatan skor Anda di Dashboard!
"""
        scores = {
            "level": level,
            "vocab_score": vocab_score,
            "grammar_score": grammar_score,
            "writing_score": writing_score
        }
        self.finished.emit(feedback, scores)


class EnglishPage(QWidget):
    def __init__(self):
        super().__init__()
        self.memory = MemoryManager()
        self.worker = None
        self._init_ui()
        self.refresh_dashboard()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header Page
        lbl_title = QLabel("🇬🇧 English Trainer Engine")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(lbl_title)
        
        # QTabWidget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            "QTabWidget::pane { border: 1px solid #333333; background: #252526; border-radius: 4px; }"
            "QTabBar::tab { background: #2D2D2D; color: #888888; padding: 10px 15px; border: 1px solid #333333; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }"
            "QTabBar::tab:selected { background: #252526; color: #FFFFFF; border-bottom: 2px solid #007ACC; }"
        )
        
        # 1. TAB 1: DASHBOARD PROGRESS
        self.tab_dashboard = QWidget()
        self._setup_dashboard_tab()
        self.tabs.addTab(self.tab_dashboard, "CEFR Progress Dashboard")
        
        # 2. TAB 2: GRAMMAR CHECKER
        self.tab_checker = QWidget()
        self._setup_checker_tab()
        self.tabs.addTab(self.tab_checker, "Grammar & Writing Checker")
        
        layout.addWidget(self.tabs)
        
    def _setup_dashboard_tab(self):
        layout = QVBoxLayout(self.tab_dashboard)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Big CEFR Card
        self.cefr_frame = QFrame()
        self.cefr_frame.setStyleSheet("background-color: #0E639C; border-radius: 8px;")
        self.cefr_frame.setFixedHeight(120)
        cefr_layout = QVBoxLayout(self.cefr_frame)
        cefr_layout.setContentsMargins(20, 15, 20, 15)
        
        lbl_cefr_title = QLabel("CURRENT CEFR LEVEL")
        lbl_cefr_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #E0F0FF;")
        self.lbl_cefr_val = QLabel("B2 - Upper Intermediate")
        self.lbl_cefr_val.setStyleSheet("font-size: 28px; font-weight: bold; color: #FFFFFF;")
        
        cefr_layout.addWidget(lbl_cefr_title)
        cefr_layout.addWidget(self.lbl_cefr_val)
        layout.addWidget(self.cefr_frame)
        
        # Progress Bars Container
        bars_frame = QFrame()
        bars_frame.setStyleSheet("background-color: #1E1E1E; border-radius: 6px; border: 1px solid #333333;")
        bars_layout = QVBoxLayout(bars_frame)
        bars_layout.setContentsMargins(20, 20, 20, 20)
        bars_layout.setSpacing(15)
        
        # Vocabulary Progress
        bars_layout.addWidget(QLabel("Vocabulary Growth:"))
        self.pb_vocab = QProgressBar()
        self.pb_vocab.setValue(50)
        self.pb_vocab.setStyleSheet("QProgressBar { background-color: #2D2D2D; border: 1px solid #333333; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #007ACC; border-radius: 3px; }")
        bars_layout.addWidget(self.pb_vocab)
        
        # Grammar Progress
        bars_layout.addWidget(QLabel("Grammar Accuracy:"))
        self.pb_grammar = QProgressBar()
        self.pb_grammar.setValue(50)
        self.pb_grammar.setStyleSheet("QProgressBar { background-color: #2D2D2D; border: 1px solid #333333; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #00C250; border-radius: 3px; }")
        bars_layout.addWidget(self.pb_grammar)
        
        # Writing Progress
        bars_layout.addWidget(QLabel("Writing Skill:"))
        self.pb_writing = QProgressBar()
        self.pb_writing.setValue(50)
        self.pb_writing.setStyleSheet("QProgressBar { background-color: #2D2D2D; border: 1px solid #333333; border-radius: 4px; text-align: center; } QProgressBar::chunk { background-color: #8338EC; border-radius: 3px; }")
        bars_layout.addWidget(self.pb_writing)
        
        layout.addWidget(bars_frame)
        
        # Recommendations
        layout.addWidget(QLabel("<b>Learning Recommendation:</b>"))
        self.lbl_recommendation = QLabel("Teruskan menulis esai secara rutin untuk melatih penataan struktur kalimat kompleks.")
        self.lbl_recommendation.setWordWrap(True)
        self.lbl_recommendation.setStyleSheet("color: #CCCCCC; font-style: italic;")
        layout.addWidget(self.lbl_recommendation)
        
        layout.addStretch()

    def _setup_checker_tab(self):
        layout = QVBoxLayout(self.tab_checker)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        layout.addWidget(QLabel("Write or paste English text to evaluate (essays, code comments, business emails):"))
        self.txt_checker_input = QTextEdit()
        self.txt_checker_input.setPlaceholderText("Write your English sentences here (e.g. 'He don't know how coding.')...")
        self.txt_checker_input.setMaximumHeight(150)
        layout.addWidget(self.txt_checker_input)
        
        self.btn_check = QPushButton(" Evaluate Writing & Grammar")
        self.btn_check.setIcon(qta.icon("fa5s.spell-check", color="white"))
        self.btn_check.setFixedHeight(35)
        self.btn_check.clicked.connect(self._check_writing)
        layout.addWidget(self.btn_check)
        
        layout.addWidget(QLabel("Analysis & AI Tutor Feedback:"))
        self.txt_feedback = QTextEdit()
        self.txt_feedback.setReadOnly(True)
        self.txt_feedback.setPlaceholderText("Grammar corrections, vocabulary choices, and CEFR estimates will be shown here...")
        layout.addWidget(self.txt_feedback)

    def refresh_dashboard(self):
        """Memuat tingkat kemahiran terakhir dari database SQLite."""
        level, vocab, grammar, writing = self.memory.get_latest_english_progress()
        
        # Update UI Labels & Bars
        cefr_desc = {
            "A1": "A1 - Beginner",
            "A2": "A2 - Elementary",
            "B1": "B1 - Intermediate",
            "B2": "B2 - Upper Intermediate",
            "C1": "C1 - Advanced",
            "C2": "C2 - Proficient"
        }
        self.lbl_cefr_val.setText(cefr_desc.get(level, f"{level} - Intermediate"))
        
        self.pb_vocab.setValue(vocab)
        self.pb_grammar.setValue(grammar)
        self.pb_writing.setValue(writing)
        
        # Generate dynamic recommendations based on weakest score
        scores = {"Vocabulary": vocab, "Grammar": grammar, "Writing": writing}
        weakest = min(scores, key=scores.get)
        
        recommendations = {
            "Vocabulary": "Kosakata Anda perlu ditingkatkan. Cobalah membaca dokumentasi teknis dalam bahasa Inggris atau makalah ilmiah di arXiv.",
            "Grammar": "Perhatikan kesesuaian subjek dan kata kerja (subject-verb agreement). Gunakan alat checker asinkron di tab sebelah secara rutin.",
            "Writing": "Fokus pada pembuatan struktur paragraf yang koheren. Latih menulis dokumentasi API atau penjelasan arsitektur modular dalam bahasa Inggris."
        }
        self.lbl_recommendation.setText(recommendations[weakest])

    def _check_writing(self):
        text = self.txt_checker_input.toPlainText().strip()
        if not text:
            return
            
        self.btn_check.setEnabled(False)
        self.txt_feedback.setText("AI English Tutor is analyzing your text...")
        
        main_win = self.window()
        if hasattr(main_win, 'bottom_panel'):
            main_win.bottom_panel.append_log(f"\n[ENGLISH TUTOR]: Memulai analisis teks: '{text}'")
            
        # Panggil worker asinkron
        self.worker = EnglishTutorWorker(text, mock=config.MOCK_MODE)
        self.worker.finished.connect(self._handle_tutor_finished)
        self.worker.error.connect(self._handle_tutor_error)
        self.worker.start()

    def _handle_tutor_finished(self, feedback: str, scores: dict):
        self.txt_feedback.setText(feedback)
        self.btn_check.setEnabled(True)
        
        # Simpan progres baru ke database
        level = scores.get("level", "B2")
        vocab = scores.get("vocab_score", 50)
        grammar = scores.get("grammar_score", 50)
        writing = scores.get("writing_score", 50)
        
        self.memory.save_english_progress(level, vocab, grammar, writing)
        
        # Refresh dashboard
        self.refresh_dashboard()
        
        main_win = self.window()
        if hasattr(main_win, 'status_bar'):
            main_win.status_bar.showMessage(f"Evaluasi selesai! Level CEFR tulisan: {level}", 4000)

    def _handle_tutor_error(self, err: str):
        self.txt_feedback.setText(f"**Error checking writing:**\n{err}")
        self.btn_check.setEnabled(True)
