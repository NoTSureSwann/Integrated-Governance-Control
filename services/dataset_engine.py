import os
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from utils.logger import log_info, log_error, log_warning

class DatasetEngine:
    """
    Layer 35, 36, 38: DATASET ENGINE & PREPROCESSING
    Menangani load, export, merge, split, cleaning, normalization,
    deduplikasi, dan persiapan data untuk training.
    """
    def __init__(self):
        # Menyimpan dataset yang sedang aktif di memori
        self.df: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}

    def load_dataset(self, file_path: str) -> bool:
        """Memuat dataset dari berbagai format file."""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                self.df = pd.read_csv(file_path)
            elif ext == '.json':
                self.df = pd.read_json(file_path)
            elif ext == '.jsonl':
                self.df = pd.read_json(file_path, lines=True)
            elif ext == '.parquet':
                self.df = pd.read_parquet(file_path)
            elif ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                self.df = pd.DataFrame({'text': lines})
            else:
                log_warning(f"Format {ext} belum didukung penuh oleh DatasetEngine, fallback ke CSV parser jika memungkinkan.")
                self.df = pd.read_csv(file_path)
            
            log_info(f"Dataset dimuat: {len(self.df)} baris dari {file_path}")
            return True
        except Exception as e:
            log_error(f"Gagal memuat dataset {file_path}: {e}")
            return False

    def export_dataset(self, file_path: str, format_type: str = 'csv') -> bool:
        """Mengekspor dataset ke berbagai format."""
        if self.df is None:
            log_warning("Tidak ada dataset untuk diekspor.")
            return False
            
        try:
            format_type = format_type.lower()
            if format_type == 'csv':
                self.df.to_csv(file_path, index=False)
            elif format_type == 'json':
                self.df.to_json(file_path, orient='records', indent=4)
            elif format_type == 'jsonl':
                self.df.to_json(file_path, orient='records', lines=True)
            elif format_type == 'parquet':
                self.df.to_parquet(file_path, index=False)
            elif format_type == 'markdown' or format_type == 'md':
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.df.to_markdown(index=False))
            else:
                log_warning(f"Format export {format_type} tidak dikenali.")
                return False
                
            log_info(f"Dataset diekspor ke {file_path} (Format: {format_type})")
            return True
        except Exception as e:
            log_error(f"Gagal mengekspor dataset: {e}")
            return False

    def get_overview(self) -> Dict[str, Any]:
        """Mengambil metrik overview (Layer 37 EDA)."""
        if self.df is None:
            return {}
        
        overview = {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "columns_list": list(self.df.columns),
            "missing_values": self.df.isnull().sum().to_dict(),
            "duplicates": int(self.df.duplicated().sum()),
            "memory_usage_mb": self.df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        return overview

    # --- Preprocessing Pipeline (Layer 36) ---
    def clean_missing_values(self, strategy: str = 'drop', fill_value: Any = None):
        if self.df is None: return
        if strategy == 'drop':
            self.df.dropna(inplace=True)
        elif strategy == 'fill' and fill_value is not None:
            self.df.fillna(fill_value, inplace=True)
            
    def deduplicate(self, subset: Optional[List[str]] = None):
        if self.df is None: return
        self.df.drop_duplicates(subset=subset, inplace=True)
        
    def normalize_text(self, column: str, lowercase: bool = True, remove_punctuation: bool = False):
        if self.df is None or column not in self.df.columns: return
        if self.df[column].dtype == 'object':
            if lowercase:
                self.df[column] = self.df[column].str.lower()
            if remove_punctuation:
                self.df[column] = self.df[column].str.replace(r'[^\w\s]', '', regex=True)

    def filter_data(self, query_string: str):
        if self.df is None: return
        try:
            self.df.query(query_string, inplace=True)
        except Exception as e:
            log_error(f"Query filter gagal: {e}")

    def detect_language(self, column: str):
        if self.df is None or column not in self.df.columns: return
        try:
            from langdetect import detect
            def safe_detect(text):
                try:
                    return detect(str(text))
                except:
                    return "unknown"
            
            self.df['detected_lang'] = self.df[column].apply(safe_detect)
        except ImportError:
            log_warning("Library 'langdetect' tidak ditemukan. Lewati deteksi bahasa.")

    # --- Training Preparation (Layer 38) ---
    def prepare_instruction_dataset(self, instruction_col: str, input_col: str, output_col: str) -> bool:
        """Membentuk dataframe menjadi format Alpaca/Instruction."""
        if self.df is None: return False
        
        required = [instruction_col, output_col]
        for col in required:
            if col not in self.df.columns:
                log_error(f"Kolom {col} tidak ditemukan untuk Instruction Dataset.")
                return False
                
        # Bentuk schema
        prepared_data = []
        for _, row in self.df.iterrows():
            record = {
                "instruction": row[instruction_col],
                "input": row[input_col] if input_col in self.df.columns and pd.notna(row[input_col]) else "",
                "output": row[output_col]
            }
            prepared_data.append(record)
            
        self.df = pd.DataFrame(prepared_data)
        log_info("Dataset berhasil diubah menjadi format Instruction.")
        return True
