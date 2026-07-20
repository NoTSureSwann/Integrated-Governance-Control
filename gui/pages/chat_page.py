from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QScrollArea, QFrame, QApplication
from PySide6.QtCore import Qt, QThread, Signal, QEvent
import qtawesome as qta

from gui.widgets.chat_bubble import ChatBubble
from orchestrator import NexusOrchestrator
import utils.logger as log
from adapters.database.memory_adapter import MemoryRepositoryAdapter
from services.websocket_client import nexus_ws_client

from services.task_engine import task_engine

class ChatPage(QWidget):
    """
    Halaman Chat Utama ala ChatGPT.
    Mendukung Bubble Chat scrollable, streaming log, dan loading state.
    """
    def __init__(self):
        super().__init__()
        self._init_ui()
        self.last_prompt = ""
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 1. Area Chat Scrollable
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: transparent;")
        
        self.chat_container = QFrame()
        self.chat_container.setStyleSheet("background-color: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_layout.setSpacing(15)
        self.chat_layout.addStretch() # Mendorong gelembung chat ke bawah
        
        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area)
        
        # 2. Control Bar (Regenerate, Copy, etc)
        self.control_layout = QHBoxLayout()
        self.control_layout.setSpacing(10)
        
        self.btn_copy = QPushButton(" Copy Report")
        self.btn_copy.setIcon(qta.icon("fa5s.copy", color="white"))
        self.btn_copy.setEnabled(False)
        self.btn_copy.clicked.connect(self._copy_last_response)
        
        self.btn_regenerate = QPushButton(" Regenerate")
        self.btn_regenerate.setIcon(qta.icon("fa5s.redo", color="white"))
        self.btn_regenerate.setEnabled(False)
        self.btn_regenerate.clicked.connect(self._regenerate_chat)
        
        self.control_layout.addWidget(self.btn_copy)
        self.control_layout.addWidget(self.btn_regenerate)
        self.control_layout.addStretch()
        
        layout.addLayout(self.control_layout)
        
        # 3. Panel Input Pesan
        input_container = QFrame()
        input_container.setStyleSheet("background-color: #252526; border-radius: 8px; border: 1px solid #333333;")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(8, 8, 8, 8)
        
        self.txt_input = QTextEdit()
        self.txt_input.setPlaceholderText("Tanyakan sesuatu ke Nexus Multi-Agent (misal: 'Optimalkan kode ini')...")
        self.txt_input.setMaximumHeight(80)
        self.txt_input.setStyleSheet("background-color: transparent; border: none; font-size: 13px;")
        # Menangani enter key untuk submit
        self.txt_input.installEventFilter(self)
        
        self.btn_send = QPushButton()
        self.btn_send.setIcon(qta.icon("fa5s.paper-plane", color="white"))
        self.btn_send.setFixedSize(40, 40)
        self.btn_send.setStyleSheet("background-color: #0E639C; border-radius: 6px;")
        self.btn_send.clicked.connect(self._send_message)
        
        input_layout.addWidget(self.txt_input)
        input_layout.addWidget(self.btn_send)
        
        layout.addWidget(input_container)
        
        # Simpan teks evaluasi terakhir untuk di-copy
        self.last_evaluation = ""
        self.memory = MemoryRepositoryAdapter()
        
        # Hubungkan ke WebSocket Client
        nexus_ws_client.event_received.connect(self._on_event_received)

    def eventFilter(self, obj, event):
        """Menangkap enter key di QTextEdit untuk mengirim pesan (Shift+Enter untuk baris baru)."""
        if obj is self.txt_input and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
                self._send_message()
                return True
        return super().eventFilter(obj, event)

    def _send_message(self):
        prompt = self.txt_input.toPlainText().strip()
        if not prompt:
            return
            
        self.last_prompt = prompt
        self.txt_input.clear()
        
        # 1. Tampilkan Gelembung Chat User & Simpan ke Memori
        user_bubble = ChatBubble(prompt, is_user=True)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, user_bubble)
        self._scroll_to_bottom()
        self.memory.save_message("user", prompt)
        
        # 2. Reset Right/Bottom Panels di MainWindow
        main_win = self.window()
        if hasattr(main_win, 'right_panel') and hasattr(main_win, 'bottom_panel'):
            main_win.right_panel.update_task(prompt)
            main_win.right_panel.txt_reasoning.clear()
            main_win.right_panel.set_progress(5)
            main_win.bottom_panel.append_log(f"\n[USER PROMPT]: {prompt}")
            
        # 3. Disable Buttons selama proses running
        self.btn_send.setEnabled(False)
        self.btn_copy.setEnabled(False)
        self.btn_regenerate.setEnabled(False)
        
        # 4. Masukkan task ke TaskEngine secara asinkron
        import config
        task_engine.submit_task(prompt, mock_mode=config.MOCK_MODE)

    def _on_event_received(self, event):
        """Menerima dan memproses event dari EventBus secara asinkron (Thread-safe)."""
        main_win = self.window()
        if not (hasattr(main_win, 'right_panel') and hasattr(main_win, 'bottom_panel')):
            return
            
        evt_type = event.event_type
        msg = event.payload.get("message", "")
        agent = event.agent
        
        # 1. Tulis logs ke Bottom Panel
        if evt_type in ("TaskQueued", "TaskStarted", "AgentThinking", "AgentFinished", "TaskCompleted", "TaskFailed"):
            log_line = f"[{evt_type}] {msg}"
            if agent and agent != "System":
                log_line = f"[{evt_type} - {agent.upper()}] {msg}"
            main_win.bottom_panel.append_log(log_line)
            
        # 2. Update progress bar dan reasoning di Right Panel
        if evt_type == "TaskQueued":
            queue_size = event.payload.get("queue_size", 1)
            main_win.right_panel.update_queue_status(queue_size)
            
        elif evt_type == "TaskStarted":
            main_win.right_panel.update_task(msg)
            main_win.right_panel.txt_reasoning.clear()
            main_win.right_panel.set_progress(5)
            # Karena sudah mulai, queue size harusnya berkurang (asumsi sederhana)
            current_q = getattr(main_win.right_panel, "_current_q", 1)
            main_win.right_panel._current_q = max(0, current_q - 1)
            main_win.right_panel.update_queue_status(main_win.right_panel._current_q)
            
        elif evt_type == "AgentThinking":
            main_win.right_panel.append_reasoning(f"\n--- {agent.upper()} START ---")
            main_win.right_panel.append_reasoning(msg)
            
            # Map progress
            progress_map = {"Planner": 20, "Research": 40, "Developer": 60, "Reviewer": 80}
            if agent in progress_map:
                main_win.right_panel.set_progress(progress_map[agent])
                
        elif evt_type == "AgentFinished":
            main_win.right_panel.append_reasoning(f"\n[OUTPUT]:\n{msg[:200]}...\n--- {agent.upper()} COMPLETE ---")
            
        elif evt_type == "TaskCompleted":
            result = event.payload.get("result", {})
            self._handle_pipeline_finished(result)
            
        elif evt_type == "TaskFailed":
            err_msg = event.payload.get("error", "Unknown error")
            self._handle_pipeline_error(err_msg)

    def _handle_pipeline_finished(self, result: dict):
        # 1. Tampilkan Gelembung Balasan Evaluasi Akhir dari Reviewer Agent & Simpan ke Memori
        self.last_evaluation = result.get("evaluation", "")
        agent_bubble = ChatBubble(self.last_evaluation, is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, agent_bubble)
        self._scroll_to_bottom()
        self.memory.save_message("assistant", self.last_evaluation)
        
        # 2. Update Progress di Right Panel ke 100%
        main_win = self.window()
        if hasattr(main_win, 'right_panel'):
            main_win.right_panel.set_progress(100)
            
        # 3. Aktifkan kembali kontrol UI
        self.btn_send.setEnabled(True)
        self.btn_copy.setEnabled(True)
        self.btn_regenerate.setEnabled(True)

    def _handle_pipeline_error(self, err_msg: str):
        error_bubble = ChatBubble(f"**Error Executing Pipeline:**\n{err_msg}", is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, error_bubble)
        self._scroll_to_bottom()
        
        self.btn_send.setEnabled(True)
        self.btn_regenerate.setEnabled(True)

    def _scroll_to_bottom(self):
        sb = self.scroll_area.verticalScrollBar()
        # Delay kecil agar komponen gelembung baru selesai di-render
        QApplication.processEvents()
        sb.setValue(sb.maximum())

    def _copy_last_response(self):
        if self.last_evaluation:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.last_evaluation)
            main_win = self.window()
            if hasattr(main_win, 'status_bar'):
                main_win.status_bar.showMessage("Hasil Evaluasi disalin ke Clipboard!", 3000)

    def _regenerate_chat(self):
        if self.last_prompt:
            self._send_message()
