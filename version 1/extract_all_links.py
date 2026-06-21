import h5py
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE), "Data")
OUT_DIR = os.path.join(BASE, "output")

f = h5py.File(os.path.join(DATA_DIR, 'CMU_MOSEI_VisualFacet42.csd'), 'r')
videos = f['FACET 4.2/data']
video_ids = list(videos.keys())

os.makedirs(OUT_DIR, exist_ok=True)

with open(os.path.join(OUT_DIR, "ALLvideo_links.txt"), "w") as out:
    for vid in video_ids:
        out.write(f"{vid} - https://www.youtube.com/watch?v={vid}\n")

print(f"Extracted {len(video_ids)} YouTube links to {os.path.join(OUT_DIR, 'ALLvideo_links.txt')}")
f.close()
