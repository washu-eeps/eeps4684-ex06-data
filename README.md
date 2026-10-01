# EEPS 4684/5684 Exercise 06 export converter

Convert CloudCompare ASCII exports to CSV files for the lidar change-detection
exercise in Geospatial Field Methods at Washington University in St. Louis.

[Open the notebook in Colab](https://colab.research.google.com/github/washu-eeps/eeps4684-ex06-data/blob/main/exercise06_convert_exports.ipynb)

No local Python installation is needed. Connect to the default CPU runtime and
run the notebook's upload, conversion, and download cells in order. Upload your
`m3c2.asc` and `c2c.asc` exports, then download and extract
`exercise06_qgis_csvs.zip`. Import the CSVs into QGIS as described in the handout.

The notebook contains the conversion helper; students do not need to upload a
Python script. It renames scalar-field columns and preserves every data row and
numerical string, including missing values. It does not calculate point-cloud
distances, adjust coordinates, apply a detection mask, or estimate survey
accuracy. Uploaded files go to the Colab runtime; Google Drive access is not
requested. The notebook contains no completed exercise results or lidar data.

## CloudCompare export settings

Export the M3C2 output cloud as `m3c2.asc` and the June cloud carrying
`C2C absolute distances` as `c2c.asc`. Choose ASCII cloud, a comma separator,
a column-name header, no point-count header, and coordinates plus scalar fields.
Preserve the original survey coordinates when saving.

If Save does nothing on macOS, open Display > Display settings, disable
Use native load/save dialogs, click OK, then retry Save. See the
[CloudCompare support thread](https://cloudcompare.org/forum/viewtopic.php?t=7450).

## Local alternative and reproduction

With Python 3.9 or later, the helper can also run locally with no extra libraries:

```bash
python3 normalize_export.py m3c2.asc m3c2.csv
python3 normalize_export.py c2c.asc c2c.csv
```

The notebook embeds the same helper. Regenerate it from the included script:

```bash
python3 build_colab_notebook.py
```

The helper refuses to overwrite an existing CSV. The notebook uses a separate
output folder for each conversion run.
