from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests

TAIPEI_TZ = ZoneInfo("Asia/Taipei")
UTC_TZ = ZoneInfo("UTC")

FOLDER_ID = "1zEkCW3lUWbAIa65XHfINbLDhCKUt-9pY"
SOURCES: dict[str, str] = {
    "tw_stock_futures_summary": "https://mis23ms.github.io/tw-stock-futures/summary.json",
    "tw_stock_options_options_data": "https://mis23ms.github.io/tw-stock-options/options_data.json",
    "tw_stock_06_summary": "https://mis23ms.github.io/tw-stock-06/summary.json",
    "tw_stock_06_data": "https://raw.githubusercontent.com/mis23ms/tw-stock-06/main/docs/data.json",
    "us_market_tracker_etf": "https://mis23ms.github.io/us-market-tracker/data/etf.json",
}


class FetchError(RuntimeError):
    pass


def fetch_json(url: str, timeout: int = 60) -> Any:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    try:
        return response.json()
    except json.JSONDecodeError as exc:
        raise FetchError(f"Invalid JSON from {url}: {exc}") from exc


def build_output() -> tuple[dict[str, Any], str]:
    now_taipei = datetime.now(TAIPEI_TZ)
    now_utc = datetime.now(UTC_TZ)
    filename = f"daily_{now_taipei.strftime('%Y%m%d')}.json"

    combined: dict[str, Any] = {
        "file_name": filename,
        "generated_at_taipei": now_taipei.isoformat(),
        "generated_at_utc": now_utc.isoformat(),
        "source_urls": SOURCES,
        "data": {},
    }

    for key, url in SOURCES.items():
        combined["data"][key] = fetch_json(url)

    return combined, filename


def write_local_file(payload: dict[str, Any], filename: str) -> Path:
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return out_path


def get_drive_service():
    scopes = ["https://www.googleapis.com/auth/drive"]
    credentials, _ = google.auth.default(scopes=scopes)
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def find_existing_file(service, folder_id: str, filename: str) -> str | None:
    query = (
        f"name = '{filename}' and '{folder_id}' in parents and trashed = false"
    )
    response = (
        service.files()
        .list(
            q=query,
            spaces="drive",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            fields="files(id, name)",
            pageSize=10,
        )
        .execute()
    )
    files = response.get("files", [])
    return files[0]["id"] if files else None


def upload_to_drive(local_path: Path, filename: str, folder_id: str) -> dict[str, Any]:
    service = get_drive_service()
    media = MediaFileUpload(str(local_path), mimetype="application/json", resumable=False)
    existing_file_id = find_existing_file(service, folder_id, filename)

    if existing_file_id:
        result = (
            service.files()
            .update(
                fileId=existing_file_id,
                media_body=media,
                supportsAllDrives=True,
                fields="id, name, webViewLink, webContentLink",
            )
            .execute()
        )
        result["action"] = "updated"
        return result

    metadata = {
        "name": filename,
        "parents": [folder_id],
    }
    result = (
        service.files()
        .create(
            body=metadata,
            media_body=media,
            supportsAllDrives=True,
            fields="id, name, webViewLink, webContentLink",
        )
        .execute()
    )
    result["action"] = "created"
    return result


def main() -> int:
    try:
        payload, filename = build_output()
        local_path = write_local_file(payload, filename)
        upload_result = upload_to_drive(local_path, filename, FOLDER_ID)

        print(f"Saved local file: {local_path}")
        print(json.dumps(upload_result, ensure_ascii=False, indent=2))
        return 0
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
