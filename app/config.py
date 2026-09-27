import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Settings:
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("APP_DATA_DIR", ROOT / ".data")))
    packs_dir: Path = ROOT / "packs"
    allowed_hosts: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            host.strip()
            for host in os.getenv("APP_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
            if host.strip()
        )
    )
    model_base_url: str = field(default_factory=lambda: os.getenv("MODEL_BASE_URL", "").rstrip("/"))
    model_api_key: str = field(default_factory=lambda: os.getenv("MODEL_API_KEY", ""))
    model_name: str = field(default_factory=lambda: os.getenv("MODEL_NAME", ""))
    timeout: float = field(default_factory=lambda: float(os.getenv("MODEL_TIMEOUT_SECONDS", "45")))
    stage_models: dict[str, str] = field(
        default_factory=lambda: {
            stage: os.getenv("MODEL_" + stage.upper(), "")
            for stage in ("extract", "review", "critic")
        }
    )

    @property
    def model_ready(self):
        parts = urlsplit(self.model_base_url)
        return (
            parts.scheme in {"http", "https"}
            and bool(parts.hostname)
            and not parts.username
            and not parts.password
            and not parts.query
            and not parts.fragment
            and bool(self.model_name)
        )
