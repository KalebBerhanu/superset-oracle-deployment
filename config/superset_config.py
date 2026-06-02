# =========================================================
# CRITICAL: ORACLE DRIVER INJECTION (MUST RUN FIRST)
# =========================================================
import sys

try:
    import oracledb
    # Emulate the legacy version structure so SQLAlchemy accepts it
    oracledb.version = "8.3.0" 
    
    # Inject oracledb into the system modules as 'cx_Oracle'
    sys.modules["cx_Oracle"] = oracledb
    import cx_Oracle
    
    # NOTE: We intentionally DO NOT call init_oracle_client() here.
    # This keeps the driver in pure-Python Thin Mode.
    
    print(">>> Oracle DB drivers injected successfully in Thin Mode.")
except ModuleNotFoundError:
    print(">>> Oracle driver not detected in virtual env yet. Waiting for pip sync...")
# =========================================================
# STANDARD CONFIGURATIONS
# =========================================================
import os

# Essential Security Configuration
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "qdZkhGYe2Tif1vs1vUShalURc65VV30KQSAtGYfL368")

# Metadata Database Configuration
ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = 8088

# Customize Feature Flags here without rebuilding images
FEATURE_FLAGS = {
    "EMBEDDED_SUPERSET": True,
    "ALERT_REPORTS": False,
    "DASHBOARD_CROSS_FILTERS": True,
    # Superset 6.1 Optional Performance Enhancement for Table Components
    "FEATURE_AG_GRID_TABLE_ENABLED": True 
}

# Legacy/Global fallbacks for compatibility
APP_NAME = "CBE Internal BI"
APP_ICON = "/static/assets/images/custom/my_logo.png"
APP_ICON_DARK = "/static/assets/images/custom/my_logo.png"

# =========================================================
# SUPERSET 6.1.0 THEME SPECS (Ant Design v5 Compliant)
# =========================================================
THEME_DEFAULT = {
    "token": {
        "brandLogoUrl": "/static/assets/images/custom/my_logo.png",
        "brandLogoHref": "/superset/welcome/",
        # New 6.1 Property: overrides global configurations cleanly
        "brandAppName": "CBE Internal BI" 
    }
}

THEME_DARK = {
    "algorithm": "dark",
    "token": {
        "brandLogoUrl": "/static/assets/images/custom/my_logo.png",
        "brandLogoHref": "/superset/welcome/",
        # Explicit definition preserves text across the dark background switch
        "brandAppName": "CBE Internal BI" 
    }
}