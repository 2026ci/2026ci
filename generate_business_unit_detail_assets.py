from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path


ROOT = Path("/Users/stricky/SynologyDrive/한화오션/keword_")
ASSETS = ROOT / "assets"
DOWNLOADS = Path("/Users/stricky/Downloads")

DETAIL_SOURCES = {
    "biz-merchant": DOWNLOADS / "000_상선사업부.csv",
    "biz-obu": DOWNLOADS / "000_2__Energy_Plant_Unit__.csv",
    "biz-special": DOWNLOADS / "000_특수선사업부.csv",
    "biz-manufacturing": DOWNLOADS / "000_제조총괄&CSHO__.csv",
    "biz-ax": DOWNLOADS / "000_AX사업부.csv",
    "biz-strategy": DOWNLOADS / "000_제품전략기술원.csv",
    "biz-support": DOWNLOADS / "000_경영지원.csv",
}

PRODUCTION_SOURCE = {
    "biz-production": DOWNLOADS / "000_생산직.csv",
}

HEADER_MAP = {
    "사업부": "division_name",
    "division_name": "division_name",
    "담당": "구분",
    "담당명": "구분",
    "구분": "구분",
    "응답자수": "응답인원",
}


def normalize_headers(headers: list[str]) -> list[str]:
    return [HEADER_MAP.get(header.strip(), header.strip()) for header in headers]


def read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    if not rows:
        return [], []

    headers = normalize_headers(rows[0])
    body = [[cell.strip() for cell in row] for row in rows[1:]]
    return headers, body


def to_csv_text(headers: list[str], rows: list[list[str]]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return buffer.getvalue().rstrip("\n")


def to_body_text(rows: list[list[str]]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerows(rows)
    return buffer.getvalue().rstrip("\n")


def escape_template_literal(text: str) -> str:
    return text.replace("\\", "\\\\").replace("`", "\\`")


def build_asset_file(source_map: dict[str, Path], output_path: Path) -> None:
    lines = [
        "window.businessUnitDetailHeaders = window.businessUnitDetailHeaders || {};",
        "window.businessUnitDetailCsv = window.businessUnitDetailCsv || {};",
    ]

    for section_id, path in source_map.items():
        headers, rows = read_csv(path)
        header_text = ",".join(headers)
        body_text = to_body_text(rows)
        lines.append(f'window.businessUnitDetailHeaders["{section_id}"] = `{escape_template_literal(header_text)}`;')
        lines.append(f'window.businessUnitDetailCsv["{section_id}"] = `{escape_template_literal(body_text)}`;')

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    build_asset_file(DETAIL_SOURCES, ASSETS / "business-unit-detail-data.js")
    build_asset_file(PRODUCTION_SOURCE, ASSETS / "business-unit-production-data.js")


if __name__ == "__main__":
    main()
