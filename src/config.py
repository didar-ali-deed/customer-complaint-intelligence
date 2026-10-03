"""Central paths and dataset settings."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PAGE = "https://www.consumerfinance.gov/data-research/consumer-complaints/"
DATA_URL = "https://files.consumerfinance.gov/ccdb/complaints.csv.zip"
RAW_ARCHIVE = ROOT / "data/raw/complaints.csv.zip"
RAW_CSV = ROOT / "data/raw/complaints.csv"
METADATA = ROOT / "data/raw/source_metadata.json"
PROFILE_CSV = ROOT / "outputs/reports/raw_data_profile.csv"
PROFILE_JSON = ROOT / "outputs/reports/raw_data_profile.json"
CLEAN_DIR = ROOT / "data/interim/complaints_clean"
DB_PATH = ROOT / "database/complaints.db"
CHUNK_SIZE = 100_000
NLP_MAX_DOCUMENTS = 150_000

for path in (ROOT / "outputs/logs", ROOT / "outputs/reports", ROOT / "outputs/tables", ROOT / "outputs/figures"):
    path.mkdir(parents=True, exist_ok=True)
