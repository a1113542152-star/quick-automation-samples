#!/usr/bin/env python3
"""Create a CSV report from a public JSON API endpoint.

Usage:
    python public_api_report.py https://api.example.com/items report.csv
"""

import csv
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen


def fetch_json(url: str):
    request = Request(url, headers={"User-Agent": "same-day-automation-sample/1.0"})
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def flatten_record(record: dict) -> dict:
    flat = {}
    for key, value in record.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            flat[key] = value
        else:
            flat[key] = json.dumps(value, ensure_ascii=False)
    return flat


def rows_from_payload(payload):
    if isinstance(payload, list):
        return [flatten_record(item) for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list):
                return [flatten_record(item) for item in value if isinstance(item, dict)]
        return [flatten_record(payload)]
    return []


def write_report(url: str, output_path: Path) -> int:
    rows = rows_from_payload(fetch_json(url))
    if not rows:
        raise ValueError("No object rows found in the JSON response.")

    headers = sorted({key for row in rows for key in row})
    with output_path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python public_api_report.py https://api.example.com/items report.csv")

    count = write_report(sys.argv[1], Path(sys.argv[2]))
    print(f"Wrote {count} rows.")


if __name__ == "__main__":
    main()
