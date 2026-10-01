"""Convert a CloudCompare comma-delimited ASCII export to a QGIS CSV.

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve() or args.output.exists():
        parser.error("Choose a new output file; existing files are preserved.")
    count = 0
    with args.input.open(newline="") as source, args.output.open("x", newline="") as target:
        reader, writer = csv.reader(source), csv.writer(target)
        fields = next(reader)
        fields[0] = fields[0].removeprefix("//")
        if fields[:3] != ["X", "Y", "Z"]:
            raise ValueError("Expected header X,Y,Z and a comma-separated export with column names.")
        writer.writerow([FIELD_NAMES.get(f, f) for f in fields])
        for row in reader:
            if len(row) != len(fields):
                raise ValueError(f"Row {count+2}: field count differs from header")
            writer.writerow(row)
            count += 1
    print(f"Preserved {count} rows in {args.output}")


if __name__ == "__main__":
    main()
