# Architecture Decision Record (ADR)
## ADR-001: Transisi ke Micro Kernel & Event-Driven Architecture

**Status**: Diterima
**Tanggal**: 2026-07-20
**Konteks**: 
Project Nexus perlu diubah dari sebuah AI *Assistant* atau *Orchestrator* monolitik sederhana menjadi sebuah *AI Operating System* penuh (SRS v2.0 - Codename ATHENA). Hal ini diperlukan untuk mendukung skala riset (AGI, Robotika, Edge AI), modularitas, dan pemrosesan asinkron dari berbagai fungsi kognitif. Struktur folder monolitik akan menghambat skalabilitas dan kolaborasi tim.

**Keputusan**:
1. Menggunakan **Micro Kernel Architecture**. Kernel (`kernel/`) tidak memuat implementasi logika model (LLM), melainkan hanya mengurus *Lifecycle*, *Routing*, dan *Message Bus*.
2. Memecah setiap komponen fungsionalitas (seperti `cognitive/`, `memory/`, `knowledge/`, `datasets/`, `vectorstore/`) menjadi modul mandiri di level-akar (*root-level*) berdasarkan prinsip *Clean Architecture* dan memiliki *Single Responsibility*.
3. Menerapkan **Event-Driven Architecture (EDA)** menggunakan *Message Queue* dan *Event Bus* untuk seluruh komunikasi antar-modul tanpa adanya ketergantungan langsung (*hard dependency*).

**Konsekuensi**:
- **Positif**: Modul dapat ditulis dan diuji secara independen. Menambahkan *engine* baru (misalnya `vision/` atau `robotics/`) tidak akan mengganggu `kernel/`.
- **Negatif**: Meningkatkan kompleksitas sistem (membutuhkan pengelolaan *Event Payload* yang ketat) dan *overhead* refactoring impor.
