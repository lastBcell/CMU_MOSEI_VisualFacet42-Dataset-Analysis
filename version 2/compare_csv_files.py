import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
AU_DIR = os.path.join(BASE, "output", "AuFiles")
OPENFACE_DIR = os.path.join(os.path.dirname(BASE), "Openface_output")

def strip_prefix(name):
    return re.sub(r'^(\d+_)+', '', name)

def get_base_id(filename, suffix):
    stripped = strip_prefix(filename)
    if stripped.endswith(suffix):
        return stripped[: -len(suffix)]
    return None

au_files = [f for f in os.listdir(AU_DIR) if f.endswith("_au_activations.csv")]
of_files = [f for f in os.listdir(OPENFACE_DIR) if f.endswith(".csv") and not f.endswith("_details.txt")]

au_ids = {}
for f in au_files:
    base = get_base_id(f, "_au_activations.csv")
    if base:
        au_ids[base] = f

of_ids = {}
for f in of_files:
    base = get_base_id(f, ".csv")
    if base:
        of_ids[base] = f

common = sorted(au_ids.keys() & of_ids.keys())

print(f"CSVs in AuFiles dir      : {len(au_ids)}")
print(f"CSVs in Openface_output  : {len(of_ids)}")
print(f"Common video IDs         : {len(common)}")
print()

if common:
    print("Common CSV files:")
    for i, vid in enumerate(common, 1):
        au_csv_old = os.path.join(AU_DIR, au_ids[vid])
        au_npy_old = os.path.join(AU_DIR, f"{vid}_au_activations.npy")
        of_old = os.path.join(OPENFACE_DIR, of_ids[vid])
        of_txt_old = os.path.join(OPENFACE_DIR, f"{vid}_of_details.txt")

        au_csv_new = os.path.join(AU_DIR, f"{i:02d}_{vid}_au_activations.csv")
        au_npy_new = os.path.join(AU_DIR, f"{i:02d}_{vid}_au_activations.npy")
        of_new = os.path.join(OPENFACE_DIR, f"{i:02d}_{vid}.csv")
        of_txt_new = os.path.join(OPENFACE_DIR, f"{i:02d}_{vid}_of_details.txt")

        if au_csv_old != au_csv_new:
            os.rename(au_csv_old, au_csv_new)
        if os.path.exists(au_npy_old):
            os.rename(au_npy_old, au_npy_new)
        if of_old != of_new:
            os.rename(of_old, of_new)
        if os.path.exists(of_txt_old):
            os.rename(of_txt_old, of_txt_new)

        print(f"  [{i:02d}] {vid}")
        print(f"       AU CSV    : {au_csv_new}")
        if os.path.exists(au_npy_new):
            print(f"       AU NPY    : {au_npy_new}")
        else:
            print(f"       AU NPY    : (not found)")
        print(f"       OpenFace  : {of_new}")
        if os.path.exists(of_txt_new):
            print(f"       OF Txt    : {of_txt_new}")
else:
    print("No common files found.")
