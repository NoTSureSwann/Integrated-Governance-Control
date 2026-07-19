from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QTextEdit, QComboBox, 
                               QGroupBox, QFormLayout, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt
from services.dataset_engine import DatasetEngine
import os

class DatasetsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = DatasetEngine()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        title = QLabel("Dataset Engine & Pipeline")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # 1. Load/Export Section
        io_group = QGroupBox("1. Dataset I/O (Layer 35)")
        io_layout = QHBoxLayout(io_group)
        
        self.btn_load = QPushButton("Load Dataset")
        self.btn_load.clicked.connect(self._load_dataset)
        
        self.btn_export = QPushButton("Export Dataset")
        self.btn_export.clicked.connect(self._export_dataset)
        
        self.lbl_status = QLabel("Status: No dataset loaded.")
        
        io_layout.addWidget(self.btn_load)
        io_layout.addWidget(self.btn_export)
        io_layout.addWidget(self.lbl_status, stretch=1)
        layout.addWidget(io_group)

        # 2. Preprocessing Pipeline Section
        pipe_group = QGroupBox("2. Preprocessing Pipeline (Layer 36)")
        pipe_layout = QFormLayout(pipe_group)
        
        self.combo_missing = QComboBox()
        self.combo_missing.addItems(["drop", "fill"])
        btn_missing = QPushButton("Run Missing Values")
        btn_missing.clicked.connect(self._run_missing_values)
        pipe_layout.addRow(self.combo_missing, btn_missing)
        
        btn_dedup = QPushButton("Run Deduplication")
        btn_dedup.clicked.connect(self._run_dedup)
        pipe_layout.addRow(QLabel("Deduplicate rows:"), btn_dedup)
        
        self.combo_lang = QComboBox()
        self.combo_lang.setEditable(True)
        self.combo_lang.setPlaceholderText("Type column name...")
        btn_lang = QPushButton("Detect Language")
        btn_lang.clicked.connect(self._run_lang_detect)
        pipe_layout.addRow(self.combo_lang, btn_lang)
        
        layout.addWidget(pipe_group)

        # 3. Training Preparation Section
        train_group = QGroupBox("3. Training Preparation (Layer 38)")
        train_layout = QFormLayout(train_group)
        
        self.txt_instr = QLineEdit()
        self.txt_instr.setPlaceholderText("Instruction column name")
        
        self.txt_input = QLineEdit()
        self.txt_input.setPlaceholderText("Input column name (optional)")
        
        self.txt_output = QLineEdit()
        self.txt_output.setPlaceholderText("Output column name")
        
        btn_train = QPushButton("Format to Instruction Dataset")
        btn_train.clicked.connect(self._format_instruction)
        
        train_layout.addRow("Instruction Col:", self.txt_instr)
        train_layout.addRow("Input Col:", self.txt_input)
        train_layout.addRow("Output Col:", self.txt_output)
        train_layout.addRow("", btn_train)
        
        layout.addWidget(train_group)
        
        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

    def _log(self, msg: str):
        self.log_output.append(msg)

    def _load_dataset(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Dataset", "", "Data Files (*.csv *.json *.jsonl *.parquet *.txt *.md)")
        if file_path:
            success = self.engine.load_dataset(file_path)
            if success:
                overview = self.engine.get_overview()
                self.lbl_status.setText(f"Status: {overview.get('rows')} rows, {overview.get('columns')} columns loaded.")
                self._log(f"Loaded {file_path}")
                # Update combo boxes with column names
                cols = overview.get("columns_list", [])
                self.combo_lang.clear()
                self.combo_lang.addItems(cols)
                if cols:
                    self.txt_instr.setText(cols[0])
                    self.txt_output.setText(cols[-1])
            else:
                self.lbl_status.setText("Status: Load failed.")
                self._log("Failed to load dataset.")

    def _export_dataset(self):
        if self.engine.df is None:
            QMessageBox.warning(self, "Warning", "Load a dataset first!")
            return
            
        file_path, filter_str = QFileDialog.getSaveFileName(
            self, "Save Dataset", "", 
            "CSV (*.csv);;JSON (*.json);;JSONL (*.jsonl);;Parquet (*.parquet);;Markdown (*.md)"
        )
        if file_path:
            ext = os.path.splitext(file_path)[1].lower().replace(".", "")
            if ext == "": ext = "csv"
            
            success = self.engine.export_dataset(file_path, format_type=ext)
            if success:
                self._log(f"Exported to {file_path}")
            else:
                self._log("Export failed.")

    def _run_missing_values(self):
        if self.engine.df is None: return
        strategy = self.combo_missing.currentText()
        self.engine.clean_missing_values(strategy=strategy)
        self._log(f"Cleaned missing values using strategy: {strategy}")
        self._update_status()

    def _run_dedup(self):
        if self.engine.df is None: return
        self.engine.deduplicate()
        self._log("Deduplication completed.")
        self._update_status()

    def _run_lang_detect(self):
        col = self.combo_lang.currentText()
        if self.engine.df is None or not col: return
        self.engine.detect_language(col)
        self._log(f"Language detection completed for column: {col}")
        self._update_status()

    def _format_instruction(self):
        instr_col = self.txt_instr.text()
        input_col = self.txt_input.text()
        out_col = self.txt_output.text()
        
        if self.engine.df is None or not instr_col or not out_col:
            QMessageBox.warning(self, "Warning", "Need dataset, instruction col, and output col.")
            return
            
        success = self.engine.prepare_instruction_dataset(instr_col, input_col, out_col)
        if success:
            self._log("Formatted as Instruction Dataset (Alpaca style).")
            self._update_status()
        else:
            self._log("Failed to format dataset.")

    def _update_status(self):
        overview = self.engine.get_overview()
        self.lbl_status.setText(f"Status: {overview.get('rows')} rows, {overview.get('columns')} columns.")
