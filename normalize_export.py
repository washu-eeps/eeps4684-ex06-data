"""Convert a CloudCompare ASCII export to a QGIS CSV.

Usage: python3 normalize_export.py input.asc output.csv
Preserves every row and every numerical string, including nan. Renames the
CloudCompare scalar fields; no filtering, bias correction, or interpolation.
"""
from pathlib import Path
import argparse
import csv

FIELD_NAMES = {
    "M3C2 distance": "M3C2_distance", "distance uncertainty": "LoD95",
    "significant change": "significant", "STD_cloud1": "STD_jan09",
    "STD_cloud2": "STD_jun10", "Npoints_cloud1": "N_jan09",
    "Npoints_cloud2": "N_jun10", "C2C absolute distances": "C2C_distance",
}



def read_export(path: Path):
    """Read comma, tab, semicolon, or whitespace exports, validating optional point counts.

    Values remain strings. No data rows or missing values are removed.
    """
    with path.open(newline="", encoding="utf-8-sig") as source:
        first = source.readline().strip().removeprefix("//").strip()
        delimiter = next((sep for sep in (",", "\t", ";") if sep in first), None)
        parse = (lambda line: next(csv.reader([line], delimiter=delimiter))) if delimiter else str.split
        fields = [field.strip() for field in parse(first)]
        if fields[:3] != ["X", "Y", "Z"]:
            raise ValueError("Expected a column-name header starting with X Y Z.")
        normalized = [FIELD_NAMES.get(field.replace("_", " "), FIELD_NAMES.get(field, field)) for field in fields]
        if len(set(normalized)) != len(normalized):
            raise ValueError("Duplicate column names after normalization.")
        rows = []
        declared_count = None
        for line_number, line in enumerate(source, start=2):
            row = parse(line)
            if line_number == 2 and len(row) == 1 and row[0].strip().isdigit():
                declared_count = int(row[0])
                continue
            if len(row) != len(fields):
                raise ValueError(f"Line {line_number}: field count differs from header; no rows were removed.")
            rows.append(row)
        if declared_count is not None and declared_count != len(rows):
            raise ValueError(f"Point-count header says {declared_count}; found {len(rows)} data rows.")
    return normalized, rows, declared_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.exists():
        parser.error("Choose a new output file; existing files are preserved.")
    fields, rows, declared_count = read_export(args.input)
    with args.output.open("x", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(fields)
        writer.writerows(rows)
    if declared_count is not None:
        print(f"Validated optional point-count header: {declared_count}")
    print(f"Preserved {len(rows)} rows in {args.output}")


if __name__ == "__main__":
    main()
