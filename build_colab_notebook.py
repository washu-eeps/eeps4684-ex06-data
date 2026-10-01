"""Build the student Colab notebook using the unchanged CSV helper."""

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent
if ROOT.name == "instructor_guide":
    ROOT = ROOT.parent
OUTPUT = ROOT / "exercise06_convert_exports.ipynb"


def cell(kind: str, source: str, identifier: str) -> dict:
    """Create a notebook cell with no execution history."""
    result = {
        "cell_type": kind,
        "id": identifier,
        "metadata": {"id": identifier},
        "source": dedent(source).strip().splitlines(keepends=True),
    }
    if kind == "code":
        result.update(execution_count=None, outputs=[])
    return result


def main() -> None:
    """Generate the upload, conversion, and download workflow."""
    helper_path = ROOT / "normalize_export.py"
    if not helper_path.is_file():
        helper_path = ROOT / "exercise06_companion/normalize_export.py"
    helper = helper_path.read_text()
    notebook = json.loads(OUTPUT.read_text())
    notebook["cells"] = [
        cell("markdown", """
        # Exercise 06 Convert CloudCompare exports for QGIS

        Use this notebook for step 2.4. It changes column names so QGIS can use
        your CloudCompare results. It preserves every data row and numerical
        value, including missing values; it does not calculate distances,
        correct alignment, or apply a detection threshold.

        No local Python installation or separate script upload is needed.
        Sign in to Google Colab, click **Connect**, then run the three code cells
        below in order using the triangle beside each cell. Use the default
        CPU runtime; no GPU is needed. Your selected files are uploaded to the
        Colab runtime. This notebook does not request access to Google Drive.

        Before starting, export **m3c2.asc** and **c2c.asc** from CloudCompare:
        choose ASCII cloud, comma separator, column-name header, and no
        point-count header. Keep coordinates and scalar fields. Export the
        M3C2 output cloud for the first file and the June cloud carrying
        C2C absolute distances for the second.
        """, "introduction"),
        cell("markdown", """
        ## 1 Upload your two exports

        Run the cell and click **Choose Files**. Select both **m3c2.asc** and
        **c2c.asc**, then wait for both uploads to finish. Do not upload the LAS
        files, the companion ZIP, or a Python script. If either filename is
        different, rename your export before uploading.
        """, "upload-instructions"),
        cell("code", """
        from google.colab import files

        uploaded = files.upload()
        required_files = ("m3c2.asc", "c2c.asc")
        missing = [name for name in required_files if name not in uploaded]
        if missing:
            raise ValueError(
                "Missing " + ", ".join(missing)
                + ". Run this cell again and choose both exports."
            )
        print("Both exports uploaded. Run step 2 next.")
        """, "upload"),
        cell("markdown", """
        ## 2 Convert the column names

        Run the cell below. A successful conversion prints the number of rows
        preserved in each CSV. An error about missing fields means you should
        check which cloud you exported and whether you included scalar fields
        and a column-name header. Do not continue to step 3 after an error.

        Each run creates a separate output folder, preserving earlier CSVs.
        """, "conversion-instructions"),
        cell("code", dedent("""
        import csv
        import subprocess
        import sys
        import tempfile
        import zipfile
        from pathlib import Path

        archive_path = None
        if "uploaded" not in globals():
            raise ValueError("Run step 1 and upload both exports first.")
        output_folder = Path(tempfile.mkdtemp(prefix="exercise06_conversion_"))
        helper_path = output_folder / "normalize_export.py"
        """) + "\nhelper_path.write_text(" + repr(helper) + ", encoding='utf-8')\n\n" + dedent("""
        expected_fields = {
            "m3c2.asc": ("M3C2 distance", "distance uncertainty", "significant change"),
            "c2c.asc": ("C2C absolute distances",),
        }
        converted_files = []
        for filename, expected in expected_fields.items():
            if filename not in uploaded or not Path(filename).is_file():
                raise ValueError("Run step 1 and upload both exports first.")
            with Path(filename).open(newline="") as stream:
                header = next(csv.reader(stream), [])
            absent = [field for field in expected if field not in header]
            if absent:
                raise ValueError(
                    filename + " is missing " + ", ".join(absent)
                    + ". Check the selected cloud and ASCII export options."
                )
            output = output_folder / Path(filename).with_suffix(".csv").name
            result = subprocess.run(
                [sys.executable, str(helper_path), filename, str(output)],
                capture_output=True, text=True,
            )
            if result.returncode:
                raise RuntimeError(result.stderr.strip())
            message = result.stdout.strip().split(" in ")[0]
            print(output.name + ": " + message)
            converted_files.append(output)

        archive = output_folder / "exercise06_qgis_csvs.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for output in converted_files:
                bundle.write(output, arcname=output.name)
        archive_path = archive
        print("Conversion complete. Run step 3 to download both CSV files.")
        """), "convert"),
        cell("markdown", """
        ## 3 Download your results

        Run the cell below to download **exercise06_qgis_csvs.zip**. Extract
        the ZIP on your computer: it contains **m3c2.csv** and **c2c.csv**.
        Download the files before leaving Colab; runtime files are temporary.

        Continue with Part 4 in QGIS. Import each CSV as Delimited Text with
        **X field = X**, **Y field = Y**, and **EPSG:26913**. Check that the
        coordinates are around **X = 386000 m** and **Y = 3632800 m**. If they
        are small shifted coordinates, correct the CloudCompare export first;
        this notebook does not change coordinates.

        The M3C2 CSV uses **M3C2_distance**, **LoD95**, and **significant**.
        LoD95 is the exported distance uncertainty, already a detection
        threshold. The C2C CSV uses **C2C_distance**.
        """, "download-instructions"),
        cell("code", """
        if "archive_path" not in globals() or archive_path is None or not archive_path.is_file():
            raise RuntimeError("Complete step 2 successfully before downloading.")
        files.download(str(archive_path))
        """, "download"),
    ]
    notebook["metadata"] = {
        "colab": {"name": OUTPUT.name, "provenance": []},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    }
    OUTPUT.write_text(json.dumps(notebook, indent=2) + "\n")
    for item in notebook["cells"]:
        if item["cell_type"] == "code":
            compile("".join(item["source"]), item["id"], "exec")
    print(f"Wrote {OUTPUT.name}")


if __name__ == "__main__":
    main()
