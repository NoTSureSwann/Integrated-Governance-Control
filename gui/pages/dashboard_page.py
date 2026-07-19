import sqlite3
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import QTimer, Qt
from gui.widgets.line_chart import LineChart
from services.websocket_client import nexus_ws_client

class MetricCard(QFrame):
    """
    Panel Kartu Metrik Desain Modern.
    """
    def __init__(self, title: str, value: str, subtext: str = ""):
        super().__init__()
        self.setStyleSheet(
            "background-color: #252526; border-radius: 6px; border: 1px solid #333333;"
        )
        self.setContentsMargins(15, 12, 15, 12)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #888888; text-transform: uppercase;")
        layout.addWidget(self.lbl_title)
        
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(self.lbl_value)
        
        self.lbl_sub = QLabel(subtext)
        self.lbl_sub.setStyleSheet("font-size: 11px; color: #007ACC;")
        layout.addWidget(self.lbl_sub)

    def update_val(self, value: str, subtext: str = None):
        self.lbl_value.setText(value)
        if subtext is not None:
            self.lbl_sub.setText(subtext)


class DashboardPage(QWidget):
    """
    Halaman Dashboard Utama dengan Metrik Real-Time dan Visualisasi Grafik.
    """
    def __init__(self):
        super().__init__()
        self.db_path = "database/nexus_telemetry.db"
        
        # Simpan riwayat metrik secara lokal untuk visualisasi grafik
        self.cpu_history = [0] * 20
        self.ram_history = [0] * 20
        
        self._init_ui()
        
        # Hubungkan ke WebSocket Client
        nexus_ws_client.event_received.connect(self._on_event_received)
        self._refresh_dashboard()

    def _on_event_received(self, event):
        """Menyerap event real-time dari WebSocket Server untuk update GUI."""
        evt_type = event.event_type
        
        if evt_type == "TelemetryUpdated":
            cpu = event.payload.get("cpu", 0)
            ram = event.payload.get("ram", 0)
            gpu = event.payload.get("gpu", 0)
            
            # Geser antrian data metrik
            self.cpu_history.pop(0)
            self.cpu_history.append(cpu)
            
            self.ram_history.pop(0)
            self.ram_history.append(ram)
            
            # Gambar ulang grafik secara real-time
            self.chart_cpu.set_data(self.cpu_history)
            self.chart_ram.set_data(self.ram_history)
            
            # Perbarui visualisasi status di Metric Card
            self.card_project.update_val("Project Nexus v0.2", f"CPU: {cpu}% | RAM: {ram}% | GPU: {gpu}%")
            
        elif evt_type == "DatabaseChanged":
            self._refresh_dashboard()
            
        elif evt_type == "AgentThinking":
            self.card_agent.update_val(event.agent, "Status: Running")
            if event.model and event.model != "N/A":
                self.card_model.update_val(event.model, "Active LLM Model")
                
        elif evt_type == "AgentFinished":
            self.card_agent.update_val("Idle", "Waiting for Tasks")
        
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Heder Page
        lbl_title = QLabel("👁️ Live Metrics & Dashboard")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        main_layout.addWidget(lbl_title)
        
        # Grid Metric Cards
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        self.card_project = MetricCard("Current Project", "Project Nexus v0.2", "Workspace: Active")
        self.card_model = MetricCard("Running Model", "Llama-3.3-70b", "API Provider: Groq")
        self.card_agent = MetricCard("Active Agent", "Idle", "Waiting for Tasks")
        self.card_api = MetricCard("API Status", "Connected", "Latency: 0 ms")
        self.card_tokens = MetricCard("Est. Token Usage", "0", "Accumulated Logs")
        self.card_db = MetricCard("SQLite Storage", "database/nexus.db", "Connection Active")
        
        grid_layout.addWidget(self.card_project, 0, 0)
        grid_layout.addWidget(self.card_model, 0, 1)
        grid_layout.addWidget(self.card_agent, 0, 2)
        grid_layout.addWidget(self.card_api, 1, 0)
        grid_layout.addWidget(self.card_tokens, 1, 1)
        grid_layout.addWidget(self.card_db, 1, 2)
        
        main_layout.addLayout(grid_layout)
        
        # Grafik Baris (CPU & RAM)
        charts_layout = QHBoxLayout()
        self.chart_cpu = LineChart("CPU Usage History (%)", color="#00C250")
        self.chart_ram = LineChart("RAM Usage History (%)", color="#FFB703")
        
        charts_layout.addWidget(self.chart_cpu)
        charts_layout.addWidget(self.chart_ram)
        main_layout.addLayout(charts_layout)
        
        # Tabel Recent Activities
        main_layout.addWidget(QLabel("Recent Agent Activities (Last 5 Logs):"))
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Agent", "Model", "Task Executed", "Latency"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet(
            "QTableWidget { background-color: #252526; gridline-color: #333333; border: 1px solid #333333; border-radius: 4px; }"
            "QHeaderView::section { background-color: #2D2D30; color: #CCCCCC; border: 1px solid #333333; padding: 4px; }"
            "QTableWidget::item { color: #CCCCCC; }"
        )
        main_layout.addWidget(self.table)
        
    def _refresh_dashboard(self):
        """Membaca Telemetry Database dan Memperbarui Layar."""
        if not os.path.exists(self.db_path):
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. Ambil 20 record terakhir untuk data grafik
            cursor.execute(
                "SELECT cpu_usage, ram_usage, agent_name, model_name, api_latency, token_usage, task_name, timestamp "
                "FROM metrics ORDER BY timestamp DESC LIMIT 20"
            )
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return
                
            # Urutkan secara kronologis untuk grafik
            rows_chrono = list(reversed(rows))
            cpu_points = [r[0] for r in rows_chrono]
            ram_points = [r[1] for r in rows_chrono]
            
            # Update Charts
            self.chart_cpu.set_data(cpu_points)
            self.chart_ram.set_data(ram_points)
            
            # Update Cards berdasarkan record terbaru
            latest = rows[0]
            self.card_agent.update_val(latest[2], "Status: Active")
            self.card_model.update_val(latest[3], "Active LLM Model")
            self.card_api.update_val("Connected", f"Latency: {latest[4]:.1f} ms")
            
            # Hitung total token dari 20 log terakhir sebagai sampel
            total_tokens = sum([r[5] for r in rows])
            self.card_tokens.update_val(str(total_tokens), "Last 20 Runs")
            
            # Update Tabel
            self.table.setRowCount(min(5, len(rows)))
            for row_idx, r in enumerate(rows[:5]):
                # timestamp, agent, model, task, latency
                self.table.setItem(row_idx, 0, QTableWidgetItem(r[7]))
                self.table.setItem(row_idx, 1, QTableWidgetItem(r[2]))
                self.table.setItem(row_idx, 2, QTableWidgetItem(r[3]))
                self.table.setItem(row_idx, 3, QTableWidgetItem(r[6]))
                self.table.setItem(row_idx, 4, QTableWidgetItem(f"{r[4]:.1f} ms"))
                
        except Exception:
            pass
