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

# 🚀 Quick Start Deployment Guide

## Prerequisites

Before you begin, ensure the following are installed and configured:

- Windows 10/11
- Docker Desktop running with the **WSL 2 backend**
- Git command-line interface

---

## 1. Clone the Repository and Configure Environment Variables

Clone this repository to your local machine and create your environment configuration file.

```bash
# Copy the template and create a local environment file
cp .env.example .env
```

Open the newly created `.env` file and verify that a secure cryptographic value is assigned to:

```env
SUPERSET_SECRET_KEY=
```

> **Note:** `SUPERSET_SECRET_KEY` is used by Superset to securely encrypt sensitive metadata, including database connection credentials.

---

## 2. Start the Docker Stack

To ensure a clean deployment and remove any stale containers, volumes, or cached configurations, run:

```bash
# Stop and remove containers, networks, and volumes
docker-compose down -v

# Start all services in detached mode
docker-compose up -d
```

---

## 3. Verify Container Initialization

Monitor the initialization container logs to confirm successful setup:

```bash
docker logs -f superset_init
```

Look for the following message near the end of the logs:

```text
>>> Oracle DB drivers injected successfully in Thin Mode.
```

This indicates that the Oracle drivers were installed successfully and the environment is ready.

---

# 🔌 Connecting Superset to Oracle Database

Once initialization is complete:

1. Open your browser and navigate to:

   ```text
   http://localhost:8088
   ```

2. Log in using the default credentials:

   ```text
   Username: admin
   Password: admin
   ```

3. Navigate to:

   ```text
   Settings → Database Connections
   ```

4. Click:

   ```text
   + DATABASE
   ```

5. Select:

   ```text
   Other
   ```

6. Configure the database connection.

### Display Name

```text
CBE Corporate Warehouse
```

### SQLAlchemy URI

```text
oracle+cx_oracle://USERNAME:PASSWORD@host.docker.internal:1521/?service_name=SERVICENAME
```

---

## ⚠️ Important Connection Notes

### SQLAlchemy Driver Prefix

The following prefix is mandatory:

```text
oracle+cx_oracle://
```

This enables the custom Oracle configuration included in this deployment.

### Host Resolution

```text
host.docker.internal
```

This hostname allows containers running inside Docker to connect back to services running on the Windows host machine, including the Oracle database listener.

---

## Connection Verification

1. Click **Test Connection**.
2. Wait for the success notification.
3. Click **Connect** to save the database configuration.

---

# 🛑 Maintenance and Contribution Guidelines

The included `.gitignore` excludes the following items from source control:

### Python Cache Files

```text
pip_cache/
```

### Runtime Data

```text
superset_home/
```

> Except for `.gitkeep` files used to preserve directory structure.

### Environment Secrets

```text
.env
```

---

## Adding New Python Dependencies

When introducing additional Python packages:

1. Add the package to:

   ```text
   requirements.txt
   ```

2. Restart the environment:

   ```bash
   docker-compose down
   docker-compose up -d
   ```

This automatically rebuilds the Python environment and installs any newly declared dependencies.

---

## Useful Docker Commands

### View Running Containers

```bash
docker ps
```

### View Superset Logs

```bash
docker logs -f superset_app
```

### Stop the Environment

```bash
docker-compose down
```

### Stop and Remove Volumes

```bash
docker-compose down -v
```

### Restart the Environment

```bash
docker-compose restart
```

---

## Default Access

| Service | URL | Credentials |
|----------|-----|-------------|
| Apache Superset | http://localhost:8088 | admin / admin |

---