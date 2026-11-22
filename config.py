"""Configuration module for PerkPilot."""
import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass(frozen=True)
class Settings:
    google_api_key: str
    model_name: str
    db_path: str
    max_purchase_amount: float

def get_settings() -> Settings:
    base_dir = Path(__file__).resolve().parent
    default_db = str(base_dir / "data" / "perkpilot.db")
    max_amt_env = os.getenv("PERKPILOT_MAX_PURCHASE_AMOUNT", "").strip()
    max_amt = float(max_amt_env) if max_amt_env else 100000.0
    model_name = (os.getenv("GEMINI_MODEL") or os.getenv("PERKPILOT_MODEL") or "gemini-3.1-flash-lite").strip()
    return Settings(
        google_api_key=os.getenv("GOOGLE_API_KEY", "").strip(),
        model_name=model_name,
        db_path=os.getenv("PERKPILOT_DB_PATH", default_db).strip(),
        max_purchase_amount=max_amt,
    )
