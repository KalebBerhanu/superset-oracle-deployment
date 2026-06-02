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
🚀 Quick Start Deployment Guide
Prerequisites
Windows 10/11 with Docker Desktop installed and running (using the WSL 2 backend).

Git command-line interface configured.

1. Clone the Blueprint and Create Environment Settings
Clone this repository to your development path. Before building the containers, instantiate your localized environment file from the provided template:

Bash
# Copy the structure template to create your live .env profile
cp .env.example .env
Open the newly created .env file and verify that a secure, cryptographic key is assigned to SUPERSET_SECRET_KEY (used to securely encrypt database credential strings in the metadata store).

2. Launch the Stack cleanly
To guarantee that old caching modules or stale container configurations are fully wiped out, initialize the stack using anonymous volume flags:

Bash
# Bring down lingering containers and clear historical state hooks
docker-compose down -v

# Fire up the container mesh network in detached background mode
docker-compose up -d
3. Verify Container Initialization Logs
The database initialization script runs schema upgrades and builds default administrative roles. You can monitor this progress in real time:

Bash
docker logs -f superset_init
Look for >>> Oracle DB drivers injected successfully in Thin Mode. near the end of the log cycle to confirm successful deployment.

🔌 Establishing the Oracle Database Connection
Once initialization completes successfully, navigate your web browser to http://localhost:8088 and authenticate using the default management credentials (admin / admin).

Navigate to the top right menu dashboard: Settings ➡️ Database Connections.

Click + DATABASE and select Other from the connection wizard selector list.

Construct your connection targeting properties using the following pattern:

Display Name: CBE Corporate Warehouse

SQLAlchemy URI*:

Plaintext
oracle+cx_oracle://WHUSER:WHUSER_123@host.docker.internal:1521/?service_name=PLUGABLE.docker.internal
Crucial Properties Note:

The prefix oracle+cx_oracle:// is required to trip our custom configuration injection engine.

host.docker.internal is used to securely exit the containerized Linux network space and route straight back to your host Windows machine where your local Oracle Database listens.

Click Test connection. Once the green success notification banner loads, click Connect to save the entry.