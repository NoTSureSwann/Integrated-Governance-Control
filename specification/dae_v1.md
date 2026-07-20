# PROJECT NEXUS - MODULE SPECIFICATION

## DATA ACQUISITION ENGINE (DAE) v1.0

### MISSION
Bangun sebuah Data Acquisition Engine yang bertugas memperoleh data dari berbagai sumber terpercaya secara realtime maupun batch.

Data Acquisition Engine harus mampu:
- Search
- Fetch
- Crawl
- Download
- Parse
- Normalize
- Validate
- Deduplicate
- Classify
- Embed
- Store
- Index
- Knowledge Update
- Realtime Sync

---

### SUPPORTED PROTOCOLS & FILES
- **Protocols**: HTTPS, REST API, GraphQL, RSS, ATOM, Git, GitHub API, Sitemap.xml, robots.txt
- **Files**: TXT, CSV, JSON, JSONL, XML, YAML, PDF, DOC, DOCX, HTML, Markdown, JPEG, PNG, SVG, Git Repository, ZIP, TAR

---

### DOMAIN CONNECTORS MAPPING

#### Academic
- `arxiv.org`, `openalex.org`, `crossref.org`, `semanticscholar.org`, `doaj.org`, `pubmed.ncbi.nlm.nih.gov`, `plos.org`, `nature.com`, `springer.com`, `sciencedirect.com`, `mdpi.com`, `ieee.org`, `acm.org`

#### Knowledge
- `wikipedia.org`, `wikidata.org`, `dbpedia.org`, `archive.org`, `gutenberg.org`, `loc.gov`

#### Programming & Repositories
- `github.com`, `gitlab.com`, `codeberg.org`, `huggingface.co`, `pypi.org`, `npmjs.com`, `docker.com`, `readthedocs.io`, `devdocs.io`

#### Documentation
- `python.org`, `fastapi.tiangolo.com`, `docs.sqlalchemy.org`, `doc.qt.io`, `sqlite.org`, `redis.io`, `postgresql.org`, `kubernetes.io`

#### Government (Indonesia)
- `bps.go.id`, `brin.go.id`, `kemdikbud.go.id`, `kemkes.go.id`, `bssn.go.id`, `jdih.go.id`, `bi.go.id`, `ojk.go.id`, `data.go.id`, `satudata.go.id`

#### Government (International)
- `nist.gov`, `europa.eu`, `oecd.org`, `unesco.org`, `un.org`, `who.int`, `worldbank.org`, `imf.org`, `data.gov`, `data.europa.eu`

#### Artificial Intelligence
- `openai.com`, `anthropic.com`, `deepmind.google`, `ai.meta.com`, `mistral.ai`, `cohere.com`, `ollama.ai`, `langchain.com`, `llamaindex.ai`, `huggingface.co`

#### Research Benchmark
- `paperswithcode.com`, `huggingface.co/datasets`, `mteb.dev`, `mlcommons.org`, `kaggle.com`

#### Economics
- `fred.stlouisfed.org`, `worldbank.org`, `imf.org`, `oecd.org`, `tradingeconomics.com`, `bi.go.id`, `ojk.go.id`, `idx.co.id`

#### English Corpus
- `cambridge.org`, `britishcouncil.org`, `bbc.co.uk`, `learningenglish.voanews.com`, `ted.com`, `teded.com`, `oxfordlearnersdictionaries.com`

#### Cyber Security
- `mitre.org`, `owasp.org`, `cve.org`, `cisa.gov`, `first.org`

#### Robotics
- `ros.org`, `openrobotics.org`, `gazebosim.org`, `webots.cloud`, `opencv.org`, `nvidia.com`

---

### FETCH & RELIABILITY STRATEGY
```
Search -> Metadata -> Download -> Integrity Check (SHA256) -> Deduplicate -> Parser -> Cleaner -> Normalizer -> Knowledge Classification -> Reliability Score -> Embedding -> SQLite & Vectorstore -> Knowledge Graph
```

**Reliability Score Factors**: Authority Score, Government/Academic Trust, Citation Count, Publication Freshness, Repository Stars/Popularity, License Validation.
