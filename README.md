# BlameIO

**BlameIO** is an open-source observability tool designed to detect and attribute MySQL and PostgreSQL replication lag to high I/O workloads. By monitoring file-level I/O activity on the replica server, BlameIO correlates lag spikes with specific tables or indexes, helping engineers identify and fix inefficient queries, bad indexing, or schema design issues.

---

## 🧠 Key Idea

In over 95% of replication lag cases, the root cause is high I/O pressure on a specific table or index, often triggered by inefficient queries. **BlameIO** attributes replication lag to specific objects and operations in real time, enabling precise diagnosis and targeted optimization.

---

## 📊 Features

- ✅ Real-time I/O tracking per table/index using `filetop-bpfcc`
- ✅ Replication lag attribution (PostgreSQL and MySQL)
- ✅ Grafana dashboards with table/index breakdown
- ✅ Prometheus integration via Node Exporter's textfile collector
- ✅ Works in production with minimal overhead
- ✅ AlertManager support for replication lag alerts
- ✅ Plugin-free architecture using system-level BPF tools

---

## 🏗️ Architecture

![BlameIO Architecture](./blameio_architecture.png)

**BlameIO** continuously monitors file I/O metrics via `filetop-bpfcc`, maps file identifiers to hypertables or indexes using PostgreSQL metadata, and exports these metrics in Prometheus-compatible format for visualization and alerting.

---

## 💾 Supported Systems

- ✅ PostgreSQL (TimescaleDB optimized)
- ✅ MySQL (replica-aware)
- 🧪 Planned support: MongoDB, Redis, Cassandra, etc.

---

## 🔧 Requirements

### PostgreSQL / TimescaleDB

- `filetop-bpfcc` installed
- `node_exporter` with textfile collector
- Access to TimescaleDB catalog (hypertables, chunks)

### MySQL

- Access to `performance_schema.table_io_waits_summary_by_*`
- Optional: custom collectors with `collectd` or Python

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/blameio.git
cd blameio
```

### 2. Set up TimescaleDB and Grafana

Use the provided `docker-compose.yml` or deploy your own stack.

```bash
docker-compose up -d timescaledb grafana prometheus node_exporter
```

### 3. Deploy BlameIO Script (PostgreSQL)

```bash
sudo cp blameio_postgres.py /usr/local/bin/
sudo chmod +x /usr/local/bin/blameio_postgres.py
sudo /usr/local/bin/blameio_postgres.py
```

Adjust connection settings in the script as needed.

### 4. Enable Filetop (requires BCC)

```bash
sudo apt install bpfcc-tools
sudo filetop-bpfcc 2
```

### 5. Import Grafana Dashboards

Use the provided JSON templates or import them manually.

---

## 📈 Dashboards

- 📌 **Table I/O Breakdown**
- 📌 **Index I/O Breakdown**
- 📌 **Replication Lag Attribution**
- 📌 **Operation Type Breakdown (read/write/update/delete)**
- 📌 **Alert Triggers and Historical Trends**

---

## 📡 Alerting

BlameIO integrates with **Prometheus AlertManager** to notify engineers when:

- Replication lag exceeds a threshold
- Specific table or index shows unusual I/O activity
- WAL or binlog write spikes happen

---

## 🛠️ Advanced Usage

- Customize `COLLECTION_INTERVAL` and `FILETOP_INTERVAL` in the script
- Tune PromQL rules for per-table alerting
- Extend object resolution logic for other DB types

---

## 📚 License

Apache 2.0 — free to use and extend.

---

## ✨ Acknowledgements

BlameIO leverages open observability tools including:

- BCC (BPF Compiler Collection)
- TimescaleDB
- Prometheus
- Grafana
- PostgreSQL internal catalogs
