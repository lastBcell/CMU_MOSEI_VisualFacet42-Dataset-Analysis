import h5py
import numpy as np
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE), "Data")
OUT_DIR = os.path.join(BASE, "output")
LINK_DIR = os.path.join(OUT_DIR, "Links")
AU_DIR = os.path.join(OUT_DIR, "AuFiles")

f = h5py.File(os.path.join(DATA_DIR, 'CMU_MOSEI_VisualFacet42.csd'), 'r')
videos = f['FACET 4.2/data']

au_names = ["AU1","AU2","AU4","AU5","AU6","AU7","AU9","AU10",
            "AU12","AU14","AU15","AU17","AU18","AU20","AU23",
            "AU24","AU25","AU26","AU28","AU43"]

os.makedirs(AU_DIR, exist_ok=True)

links_file = os.path.join(LINK_DIR, "available.txt")
if not os.path.exists(links_file):
    print(f"Error: {links_file} not found. Run check_links.py first.")
    f.close()
    exit()

with open(links_file, "r") as lf:
    available_urls = [line.strip() for line in lf if line.strip()]

available_ids = [url.split("watch?v=")[-1] for url in available_urls]

log_file = os.path.join(OUT_DIR, "extract_au.log")
log = open(log_file, "w")
_builtin_print = print
def log_print(*args, **kwargs):
    _builtin_print(*args, **kwargs)
    kwargs.pop("file", None)
    _builtin_print(*args, file=log, **kwargs)
print = log_print

print(f"Available videos to process: {len(available_ids)}\n")

success = 0
for v, vid in enumerate(available_ids):
    if vid not in videos:
        print(f"[{v+1}/{len(available_ids)}] {vid} not found in dataset, skipping")
        continue

    feats = videos[vid]['features'][()]
    intervals = videos[vid]['intervals'][()]
    au_data = feats[:, 10:30]

    yt_link = f"https://www.youtube.com/watch?v={vid}"

    print(f"=== Video {v+1}/{len(available_ids)}: {vid} ===")
    print(f"YouTube: {yt_link}")
    print(f"Frames: {au_data.shape[0]} | Duration: {intervals[-1,1]-intervals[0,0]:.2f}s")

    header = f"{'Frame':>6} {'Start(s)':>9} {'End(s)':>9}   " + "  ".join(f"{n:>7}" for n in au_names)
    print(header)
    print("-" * len(header))

    for i in range(min(10, au_data.shape[0])):
        row = f"{i:>6} {intervals[i,0]:>9.3f} {intervals[i,1]:>9.3f}   " + \
              "  ".join(f"{au_data[i,j]:>7.3f}" for j in range(20))
        print(row)
    print()

    np.save(os.path.join(AU_DIR, f"{vid}_au_activations.npy"), au_data)
    with open(os.path.join(AU_DIR, f"{vid}_au_activations.csv"), "w") as out:
        out.write("Frame,StartTime,EndTime," + ",".join(au_names) + "\n")
        for i in range(au_data.shape[0]):
            out.write(f"{i},{intervals[i,0]:.6f},{intervals[i,1]:.6f},")
            out.write(",".join(f"{au_data[i,j]:.6f}" for j in range(20)) + "\n")
    print(f"Saved to {os.path.join(AU_DIR, f'{vid}_au_activations.csv')}\n")
    success += 1

print(f"Done! Processed {success}/{len(available_ids)} available videos.")
f.close()
log.close()
_builtin_print("Done!")
