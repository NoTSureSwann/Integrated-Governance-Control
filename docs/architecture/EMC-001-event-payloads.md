# Event & Message Contract (EMC)
## EMC-001: Struktur Muatan Event Bus & Message Bus

**Tujuan**: Menstandarisasi struktur data JSON yang beredar di dalam `MessageBus` dan `EventBus` Project Nexus OS.

### 1. Standar Payload Utama (NexusEvent)
Setiap event yang dipancarkan oleh *Publisher* harus memenuhi skema berikut:
```json
{
  "event_id": "uuid4",
  "event_type": "WorkspaceUpdated",
  "timestamp": "ISO-8601",
  "publisher": "module_name",
  "priority": "HIGH|MEDIUM|LOW",
  "payload": {
    // Data spesifik
  }
}
```

### 2. Event Types & Spesifikasi Payload

#### a. `WorkspaceUpdated`
Diterbitkan oleh `workspace` (Workspace Watcher).
```json
{
  "event_type": "WorkspaceUpdated",
  "payload": {
    "file_path": "/workspace/sandbox/temp.py",
    "change_type": "MODIFIED",
    "lines_changed": 15
  }
}
```

#### b. `KnowledgeUpdated`
Diterbitkan oleh `knowledge` (Knowledge Engine).
```json
{
  "event_type": "KnowledgeUpdated",
  "payload": {
    "knowledge_id": "knw-1234",
    "vector_index_updated": true,
    "entities_added": ["Machine Learning", "Neural Network"]
  }
}
```

#### c. `TaskFinished`
Diterbitkan oleh `orchestrator` atau `supervisor`.
```json
{
  "event_type": "TaskFinished",
  "payload": {
    "task_id": "tsk-9999",
    "agent_used": "Kimi",
    "hybrid_score": 0.88,
    "status": "SUCCESS"
  }
}
```
