"""Download and preserve the complete official CFPB complaint archive."""
from __future__ import annotations
import hashlib, json, logging, zipfile
from datetime import datetime, timezone
from pathlib import Path
import requests
from tqdm import tqdm
from .config import DATA_URL, SOURCE_PAGE, RAW_ARCHIVE, RAW_CSV, METADATA

LOG = logging.getLogger(__name__)

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def download_data(force: bool = False) -> Path:
    """Fetch official ZIP when needed, extract the CSV unchanged, and write metadata."""
    RAW_ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    valid_archive = RAW_ARCHIVE.exists() and zipfile.is_zipfile(RAW_ARCHIVE)
    downloaded_this_run=force or not valid_archive
    prior_metadata=json.loads(METADATA.read_text(encoding="utf-8")) if METADATA.exists() else {}
    now=datetime.now(timezone.utc)
    if downloaded_this_run:
        temporary = RAW_ARCHIVE.with_suffix(".zip.part")
        try:
            with requests.get(DATA_URL, stream=True, timeout=(30, 180)) as response:
                response.raise_for_status()
                total = int(response.headers.get("content-length", 0))
                with temporary.open("wb") as target, tqdm(total=total, unit="B", unit_scale=True, desc="CFPB archive") as bar:
                    for block in response.iter_content(chunk_size=1024 * 1024):
                        if block:
                            target.write(block); bar.update(len(block))
            if not zipfile.is_zipfile(temporary):
                raise ValueError("Downloaded CFPB file is not a valid ZIP archive")
            temporary.replace(RAW_ARCHIVE)
        except Exception:
            temporary.unlink(missing_ok=True)
            LOG.exception("CFPB download failed")
            raise
    with zipfile.ZipFile(RAW_ARCHIVE) as archive:
        candidates = [n for n in archive.namelist() if n.lower().endswith(".csv")]
        if not candidates:
            raise ValueError("Official CFPB ZIP contains no CSV")
        member = max(candidates, key=lambda name: archive.getinfo(name).file_size)
        if not RAW_CSV.exists() or RAW_CSV.stat().st_size != archive.getinfo(member).file_size:
            with archive.open(member) as source, RAW_CSV.open("wb") as target:
                while block := source.read(8 * 1024 * 1024): target.write(block)
    metadata = {
        "source": "Consumer Financial Protection Bureau Consumer Complaint Database",
        "source_url": SOURCE_PAGE, "download_url": DATA_URL,
        "download_date_utc": now.date().isoformat() if downloaded_this_run else prior_metadata.get("download_date_utc",now.date().isoformat()),
        "last_verified_utc": now.isoformat(),
        "archive_filename": RAW_ARCHIVE.name, "archive_size_bytes": RAW_ARCHIVE.stat().st_size,
        "archive_sha256": sha256_file(RAW_ARCHIVE), "filename": RAW_CSV.name,
        "filesize_bytes": RAW_CSV.stat().st_size, "sha256": sha256_file(RAW_CSV),
        "source_member": member,
        "description": "Complete public CFPB consumer complaint records released in the official download at execution time."
    }
    METADATA.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    LOG.info("Preserved %s (%s bytes)", RAW_CSV, RAW_CSV.stat().st_size)
    return RAW_CSV

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    download_data()
