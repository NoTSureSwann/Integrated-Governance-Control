from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QProgressBar

class RightPanel(QWidget):
    """
    Komponen Right Panel untuk Activity, Task, Reasoning, dan Running Agent.
    """
    def __init__(self):
        super().__init__()
        self.setObjectName("rightPanel")
        self.setFixedWidth(280)
        self._init_ui()
        
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Activity Label
        lbl_title = QLabel("AI Activity")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #007ACC;")
        layout.addWidget(lbl_title)
        
        # Current Task
        layout.addWidget(QLabel("Current Task:"))
        self.lbl_task = QLabel("Waiting for input...")
        self.lbl_task.setStyleSheet("color: #CCCCCC; font-style: italic;")
        self.lbl_task.setWordWrap(True)
        layout.addWidget(self.lbl_task)
        
        # Reasoning Area
        layout.addWidget(QLabel("Agent Reasoning:"))
        self.txt_reasoning = QTextEdit()
        self.txt_reasoning.setReadOnly(True)
        self.txt_reasoning.setPlaceholderText("Agent thoughts will appear here...")
        layout.addWidget(self.txt_reasoning)
        
        # Queue / Progress
        layout.addWidget(QLabel("Queue Status:"))
        self.lbl_queue = QLabel("0 tasks in queue")
        self.lbl_queue.setStyleSheet("color: #00C250; font-weight: bold;")
        layout.addWidget(self.lbl_queue)
        
        layout.addWidget(QLabel("Task Progress:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
    def update_task(self, task: str):
        self.lbl_task.setText(task)
        
    def append_reasoning(self, text: str):
        self.txt_reasoning.append(text)
        
    def set_progress(self, percentage: int):
        self.progress_bar.setValue(percentage)
        
    def update_queue_status(self, count: int):
        self.lbl_queue.setText(f"{count} tasks in queue")
