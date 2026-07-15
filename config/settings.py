from pathlib import Path
import os


DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = DASHBOARD_ROOT.parent
DEFAULT_DATA_DIR = WORKSPACE_ROOT / "ssdc-data-cleaning" / "data_clean"
DATA_ENV_VAR = "SSDC_DATA_DIR"


def resolve_data_dir() -> Path:
    """Resolve the local cleaned-data directory without relying on cwd."""
    configured = os.getenv(DATA_ENV_VAR)
    return Path(configured).expanduser().resolve() if configured else DEFAULT_DATA_DIR
