#!/usr/bin/env python3
"""Clean a CSV export without changing the original file.

Usage:
    python csv_cleaner.py input.csv output.csv
"""

import csv
import sys
from pathlib import Path


def normalize_header(value: str) -> str:
    return "_".join(value.strip().lower().split())


def clean_cell(value: str) -> str:
    return " ".join(value.strip().split())


def clean_csv(input_path: Path, output_path: Path) -> int:
    with input_path.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError("The input CSV has no header row.")

        headers = [normalize_header(name) for name in reader.fieldnames]
        seen = set()
        rows = []

        for raw_row in reader:
            row = {header: clean_cell(raw_row.get(original, "")) for header, original in zip(headers, reader.fieldnames)}
            signature = tuple(row.get(header, "") for header in headers)
            if signature in seen:
                continue
            seen.add(signature)
            rows.append(row)

    with output_path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python csv_cleaner.py input.csv output.csv")

    written = clean_csv(Path(sys.argv[1]), Path(sys.argv[2]))
    print(f"Wrote {written} cleaned rows.")


if __name__ == "__main__":
    main()
