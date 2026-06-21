import h5py
import subprocess
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE), "Data")
OUT_DIR = os.path.join(BASE, "output")

f = h5py.File(os.path.join(DATA_DIR, 'CMU_MOSEI_VisualFacet42.csd'), 'r')
videos = f['FACET 4.2/data']
video_ids = list(videos.keys())

print(f"Total videos: {len(video_ids)}")
num = input("How many videos to download? ")
num_videos = int(num) if num.isdigit() else 1
num_videos = min(num_videos, len(video_ids))

os.makedirs(OUT_DIR, exist_ok=True)

links_file = os.path.join(OUT_DIR, "video_links.txt")

for v in range(num_videos):
    vid = video_ids[v]
    out_path = os.path.join(OUT_DIR, f"{vid}.mp4")
    yt_link = f"https://www.youtube.com/watch?v={vid}"

    if os.path.exists(out_path):
        print(f"[{v+1}/{num_videos}] {vid}.mp4 already exists, skipping")
        continue
    print(f"[{v+1}/{num_videos}] Downloading {vid}...")
    print(f"  Link: {yt_link}")
    result = subprocess.run([
        "yt-dlp", "-f", "best[height<=480]",
        "-o", out_path,
        yt_link
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Failed: {result.stderr.strip()[:150]}")
    else:
        print(f"  Saved to {out_path}")

with open(links_file, "w") as lf:
    for v in range(num_videos):
        vid = video_ids[v]
        lf.write(f"{vid}\t{OUT_DIR}/{vid}.mp4\thttps://www.youtube.com/watch?v={vid}\n")
print(f"Links saved to {links_file}")

f.close()
