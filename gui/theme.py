import os
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

class ThemeManager(QObject):
    theme_changed = Signal(str)  # "dark" or "light"

    def __init__(self):
        super().__init__()
        self.current_theme = "dark"

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()
        self.theme_changed.emit(self.current_theme)

    def apply_theme(self):
        app = QApplication.instance()
        if not app:
            return
            
        qss = self._get_theme_qss(self.current_theme)
        if qss:
            app.setStyleSheet(qss)

    def _get_theme_qss(self, name: str) -> str:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        theme_path = os.path.join(base_dir, "gui", "themes", f"{name}.qss")
        if os.path.exists(theme_path):
            try:
                with open(theme_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading QSS theme file: {e}")
        return ""
