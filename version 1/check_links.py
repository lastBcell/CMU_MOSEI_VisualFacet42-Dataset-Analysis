import h5py
import requests
import os
import re
import time

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE), "Data")
OUT_DIR = os.path.join(BASE, "output")

f = h5py.File(os.path.join(DATA_DIR, 'CMU_MOSEI_VisualFacet42.csd'), 'r')
videos = f['FACET 4.2/data']
video_ids = list(videos.keys())

print(f"Total videos available: {len(video_ids)}")
num = input("How many videos to check? ")
num_videos = int(num) if num.isdigit() else 10
num_videos = min(num_videos, len(video_ids))

os.makedirs(OUT_DIR, exist_ok=True)

available = []
unavailable = []

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for i in range(num_videos):
    vid = video_ids[i]
    url = f"https://www.youtube.com/watch?v={vid}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            m = re.search(r'"playabilityStatus":\{"status":"([^"]+)"', resp.text)
            if m:
                s = "AVAILABLE" if m.group(1) == "OK" else f"UNAVAILABLE({m.group(1)})"
            else:
                s = "AVAILABLE"
        else:
            s = f"HTTP_{resp.status_code}"
    except:
        s = "ERROR"

    if s.startswith("AVAILABLE"):
        available.append(vid)
    else:
        unavailable.append(vid)

    print(f"[{i+1}/{num_videos}] {vid} -> {s}")
    time.sleep(0.3)

with open(os.path.join(OUT_DIR, "video_links.txt"), "w") as out:
    out.write("STATUS\tVIDEO_ID\tURL\n")
    for vid in available:
        out.write(f"AVAILABLE\t{vid}\thttps://www.youtube.com/watch?v={vid}\n")
    for vid in unavailable:
        out.write(f"UNAVAILABLE\t{vid}\thttps://www.youtube.com/watch?v={vid}\n")

with open(os.path.join(OUT_DIR, "available.txt"), "w") as out:
    for vid in available:
        out.write(f"https://www.youtube.com/watch?v={vid}\n")

with open(os.path.join(OUT_DIR, "unavailable.txt"), "w") as out:
    for vid in unavailable:
        out.write(f"https://www.youtube.com/watch?v={vid}\n")

print(f"\nDone! Checked: {num_videos}, Available: {len(available)}, Unavailable: {len(unavailable)}")
f.close()
