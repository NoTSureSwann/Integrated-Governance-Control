from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QScrollArea, QFrame, QSplitter)
from PySide6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from services.dataset_engine import DatasetEngine
import pandas as pd

class EDAPage(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = DatasetEngine()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Exploratory Data Analysis (EDA)")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.btn_load = QPushButton("Load Dataset for EDA")
        self.btn_load.clicked.connect(self._load_dataset)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_load)
        layout.addLayout(header_layout)
        
        self.lbl_overview = QLabel("No dataset loaded.")
        layout.addWidget(self.lbl_overview)
        
        # Splitter for layout
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left Panel (Stats)
        self.stats_panel = QLabel("Statistics will appear here.")
        self.stats_panel.setAlignment(Qt.AlignTop)
        self.stats_panel.setObjectName("stats_panel")
        
        scroll_stats = QScrollArea()
        scroll_stats.setWidgetResizable(True)
        scroll_stats.setWidget(self.stats_panel)
        splitter.addWidget(scroll_stats)
        
        # Right Panel (Charts)
        chart_widget = QWidget()
        self.chart_layout = QVBoxLayout(chart_widget)
        
        # Matplotlib Figure
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.chart_layout.addWidget(self.canvas)
        
        splitter.addWidget(chart_widget)
        splitter.setSizes([300, 700])

    def _load_dataset(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Dataset", "", "Data Files (*.csv *.json *.jsonl *.parquet)")
        if file_path:
            if self.engine.load_dataset(file_path):
                self._update_dashboard()

    def _update_dashboard(self):
        overview = self.engine.get_overview()
        
        # Update labels
        rows = overview.get('rows', 0)
        cols = overview.get('columns', 0)
        mem = overview.get('memory_usage_mb', 0)
        self.lbl_overview.setText(f"Dataset Overview: {rows} Rows, {cols} Columns, {mem:.2f} MB")
        
        # Stats text
        stats_text = f"<b>Data Types:</b><br>"
        if self.engine.df is not None:
            dtypes = self.engine.df.dtypes
            for col, dtype in dtypes.items():
                stats_text += f"- {col}: {dtype}<br>"
                
            stats_text += "<br><b>Missing Values:</b><br>"
            missing = overview.get('missing_values', {})
            for col, val in missing.items():
                if val > 0:
                    stats_text += f"- {col}: {val} missing<br>"
                    
            stats_text += f"<br><b>Duplicates:</b> {overview.get('duplicates', 0)}"
        self.stats_panel.setText(stats_text)
        
        # Plot missing values distribution
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        missing_series = pd.Series(missing)
        missing_series = missing_series[missing_series > 0]
        
        if not missing_series.empty:
            missing_series.plot(kind='bar', ax=ax, color='salmon')
            ax.set_title("Missing Values per Column")
            ax.set_ylabel("Count")
            self.figure.tight_layout()
        else:
            ax.text(0.5, 0.5, 'No Missing Values Found', horizontalalignment='center', verticalalignment='center', fontsize=12)
            ax.set_title("Data Quality")
            
        self.canvas.draw()
