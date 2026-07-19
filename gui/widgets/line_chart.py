from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QPainterPath
from PySide6.QtCore import Qt, QPointF

class LineChart(QWidget):
    """
    Widget Grafik Garis Kustom yang digambar menggunakan QPainter.
    Ringan, berkinerja tinggi, dan memiliki visualisasi modern.
    """
    def __init__(self, title: str = "Metric Chart", color: str = "#007ACC"):
        super().__init__()
        self.title = title
        self.line_color = QColor(color)
        self.data_points = []
        self.setMinimumHeight(150)
        
    def set_data(self, points: list):
        """Set data points (list of floats/ints)."""
        self.data_points = points
        self.update() # Memicu paintEvent untuk menggambar ulang
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        padding = 20
        
        # Draw background panel
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#252526")))
        painter.drawRoundedRect(0, 0, width, height, 6, 6)
        
        # Draw Title
        painter.setPen(QColor("#CCCCCC"))
        painter.drawText(15, 20, self.title)
        
        if not self.data_points:
            painter.drawText(width // 2 - 50, height // 2, "No Telemetry Data")
            return
            
        # Tentukan batas atas dan bawah data
        max_val = max(self.data_points) if self.data_points else 100
        min_val = min(self.data_points) if self.data_points else 0
        
        # Mencegah pembagian dengan nol
        val_range = max_val - min_val
        if val_range == 0:
            val_range = 1.0
            
        # Gambar Grid Sederhana
        painter.setPen(QPen(QColor("#3A3A3C"), 1, Qt.DashLine))
        grid_lines = 4
        for i in range(1, grid_lines):
            y = padding + i * (height - 2 * padding) // grid_lines
            painter.drawLine(padding, y, width - padding, y)
            
        # Petakan titik data ke koordinat piksel layar
        points_count = len(self.data_points)
        x_step = (width - 2 * padding) / max(1, points_count - 1)
        
        path = QPainterPath()
        pixel_points = []
        
        for i, val in enumerate(self.data_points):
            x = padding + i * x_step
            # Normalisasi nilai y agar pas dalam padding atas/bawah
            y = height - padding - ((val - min_val) / val_range) * (height - 2 * padding - 20)
            
            pixel_points.append(QPointF(x, y))
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
                
        # Draw Gradient Area di bawah garis
        gradient_path = QPainterPath(path)
        gradient_path.lineTo(pixel_points[-1].x(), height - padding)
        gradient_path.lineTo(pixel_points[0].x(), height - padding)
        gradient_path.closeSubpath()
        
        gradient = QLinearGradient(0, padding, 0, height - padding)
        # Warna glow memudar ke bawah
        color_start = QColor(self.line_color)
        color_start.setAlpha(80)
        color_end = QColor(self.line_color)
        color_end.setAlpha(5)
        
        gradient.setColorAt(0, color_start)
        gradient.setColorAt(1, color_end)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawPath(gradient_path)
        
        # Draw Main Line
        pen = QPen(self.line_color, 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        
        # Draw Data Circles (untuk data point terakhir)
        if pixel_points:
            last_pt = pixel_points[-1]
            painter.setPen(QPen(self.line_color, 1))
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.drawEllipse(last_pt, 4, 4)
