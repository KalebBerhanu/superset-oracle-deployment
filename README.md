# Apache Superset 6.1.0 Hub with Native Oracle DB Thin-Mode Connectivity

This repository provides a standardized, lightweight blueprint for deploying a containerized instance of **Apache Superset 6.1.0** via Docker Compose. It is uniquely engineered to bypass permission boundaries and connect seamlessly to a local or remote Oracle Database instance using the pure-Python `oracledb` library running completely in **Thin Mode**.

---

## 🏗️ Architectural Challenges & Workarounds Implemented

Deploying Apache Superset 6.1.0 with official images introduces severe isolation and package conflicts when trying to add vendor-specific drivers like Oracle. This configuration implements specific system workarounds to stabilize the stack:

### 1. Python Environment Path Redirection (`PYTHONPATH`)
* **The Barrier:** The Superset 6.1.0 container runs its production environment out of a strict virtual environment (`/app/.venv`) that drops root elevation during normal operation. Running a generic `pip install` inside the boot script forces packages to install inside the unprivileged user-space home directory (`/app/superset_home/.local/...`), leaving the core application blind to the driver and throwing a `ModuleNotFoundError`.
* **The Resolution:** Packages are systematically isolated into a write-safe local footprint, and a strict `PYTHONPATH` environment override is injected into both the application core and the database migration services. This tells the Python engine runtime to look dynamically inside the mounted user-space folders.

### 2. Pure-Python Thin-Mode Oracle Driver Bootstrapping
* **The Barrier:** Standard Python database interfaces for Oracle (like legacy `cx_Oracle` or default SQLAlchemy setups) depend heavily on native C-binaries and a heavy installation of the Oracle Instant Client inside the Linux container, which creates massive image bloat and permission maintenance overhead.
* **The Resolution:** A custom module intercept script is placed at the absolute top of `superset_config.py`. It runs before any database connection pooling begins, dropping the modern `oracledb` library into Python’s internal global `sys.modules` map masqueraded as `cx_Oracle`. It emulates legacy structural properties (`oracledb.version = "8.3.0"`) so SQLAlchemy accepts the handshake, opening native TCP/IP communication sockets without needing a single native client binary file.

### 3. Ant Design v5 Visual Asset Compliance
* **The Barrier:** Superset 6.1.0 introduces strict visual theme tokens under Ant Design v5. Relying entirely on legacy fallback variables like `APP_NAME` or `APP_ICON` can degrade interface consistency or trigger client-side rendering errors.
* **The Resolution:** Configured templates capture the unified `brandAppName` schema alongside explicit algorithm dictionaries for both standard and dark-mode operations.

---

## 📁 Repository Structure

```text
.
├── config/
│   └── superset_config.py     # Global Superset setups & runtime Oracle driver interceptor
├── branding/                  # Shared asset path for custom application images/logos
├── superset_home/             # Persistent storage volume path (SQLite metadata, logs, etc.)
│   └── .gitkeep               # Preserves the directory blueprint framework in Git
├── .env.example               # Template file for required deployment environment secrets
├── .gitignore                 # Strict filter avoiding commit pollution (ignores local caches)
├── docker-compose.yml         # Unified service engine mesh mapping and PYTHONPATH injections
└── requirements.txt           # Python application layer dependencies tracker (oracledb)