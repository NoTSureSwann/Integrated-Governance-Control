from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class ChatBubble(QFrame):
    """
    Widget Gelembung Chat Kustom yang membedakan tampilan User dan Agent.
    """
    def __init__(self, text: str, is_user: bool = False):
        super().__init__()
        self.is_user = is_user
        self._init_ui(text)
        
    def _init_ui(self, text: str):
        # Outer Layout to handle alignment (Left for Agent, Right for User)
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(5, 5, 5, 5)
        outer_layout.setSpacing(0)
        
        # Inner bubble container
        bubble = QFrame()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(12, 10, 12, 10)
        
        lbl_sender = QLabel("YOU" if self.is_user else "NEXUS AGENT")
        lbl_sender.setStyleSheet(
            "font-size: 10px; font-weight: bold; color: #888888; margin-bottom: 2px;"
        )
        bubble_layout.addWidget(lbl_sender)
        
        lbl_text = QLabel(text)
        lbl_text.setWordWrap(True)
        lbl_text.setTextFormat(Qt.MarkdownText) # Mengaktifkan render markdown dasar bawaan Qt
        
        if self.is_user:
            # User Bubble Styling (Aksen Biru)
            bubble.setStyleSheet(
                "background-color: #007ACC; border-radius: 12px; border-top-right-radius: 2px;"
            )
            lbl_text.setStyleSheet("color: #FFFFFF; font-size: 13px;")
            outer_layout.addStretch()
            outer_layout.addWidget(bubble)
        else:
            # Agent Bubble Styling (Latar Gelap)
            bubble.setStyleSheet(
                "background-color: #2D2D2D; border-radius: 12px; border-top-left-radius: 2px; border: 1px solid #3E3E3E;"
            )
            lbl_text.setStyleSheet("color: #D4D4D4; font-size: 13px;")
            outer_layout.addWidget(bubble)
            outer_layout.addStretch()
            
        bubble_layout.addWidget(lbl_text)
