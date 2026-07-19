from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QTableWidget, QTableWidgetItem)
import json
import os
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from utils.logger import log_error, log_info

class TrainingAnalysisPage(QWidget):
    def __init__(self):
        super().__init__()
        self.results = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Post-Training Analysis (Layer 39)")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        self.btn_import = QPushButton("Import Evaluation JSON")
        self.btn_import.clicked.connect(self._import_results)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_import)
        layout.addLayout(header_layout)
        
        # Metrics Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Experiment", "Accuracy", "Precision", "Recall", "F1 Score"])
        layout.addWidget(self.table)
        
        # Chart
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)

    def _import_results(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Eval JSON", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Coba parse loss/accuracy
                exp_name = data.get("experiment_name", os.path.basename(file_path))
                acc = data.get("accuracy", 0.0)
                prec = data.get("precision", 0.0)
                rec = data.get("recall", 0.0)
                f1 = data.get("f1_score", 0.0)
                
                self.results.append({
                    "name": exp_name,
                    "acc": acc, "prec": prec, "rec": rec, "f1": f1
                })
                
                self._update_table()
                self._update_chart()
                log_info(f"Imported training results from {file_path}")
            except Exception as e:
                log_error(f"Failed to import results: {e}")

    def _update_table(self):
        self.table.setRowCount(len(self.results))
        for row, res in enumerate(self.results):
            self.table.setItem(row, 0, QTableWidgetItem(str(res['name'])))
            self.table.setItem(row, 1, QTableWidgetItem(f"{res['acc']:.4f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{res['prec']:.4f}"))
            self.table.setItem(row, 3, QTableWidgetItem(f"{res['rec']:.4f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{res['f1']:.4f}"))

    def _update_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if self.results:
            names = [r['name'] for r in self.results]
            f1_scores = [r['f1'] for r in self.results]
            ax.bar(names, f1_scores, color='skyblue')
            ax.set_title("F1 Score Comparison")
            ax.set_ylabel("F1 Score")
            ax.set_ylim(0, 1.0)
            
        self.canvas.draw()
