import os
import yt_dlp

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "output")
LINK_DIR = os.path.join(OUT_DIR, "Links")
VIDEO_DIR = os.path.join(OUT_DIR, "video_out")

links_file = os.path.join(LINK_DIR, "available.txt")
if not os.path.exists(links_file):
    print(f"Error: {links_file} not found. Run check_links.py first.")
    exit()

with open(links_file, "r") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Total available videos: {len(urls)}")
num = input("How many videos to download? ")
num_videos = int(num) if num.isdigit() else 1
num_videos = min(num_videos, len(urls))

os.makedirs(VIDEO_DIR, exist_ok=True)

saved_links = os.path.join(OUT_DIR, "downloaded_links.txt")

for v in range(num_videos):
    url = urls[v]
    vid = url.split("watch?v=")[-1]
    out_path = os.path.join(VIDEO_DIR, f"{vid}.mp4")

    if os.path.exists(out_path):
        print(f"[{v+1}/{num_videos}] {vid}.mp4 already exists, skipping")
        continue

    print(f"[{v+1}/{num_videos}] Downloading {vid}...")
    print(f"  Link: {url}")
    ydl_opts = {
        'format': 'best[height<=480]',
        'outtmpl': out_path,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"  Saved to {out_path}")
    except Exception as e:
        print(f"  Failed: {str(e)[:150]}")

with open(saved_links, "w") as lf:
    for v in range(num_videos):
        url = urls[v]
        vid = url.split("watch?v=")[-1]
        lf.write(f"{vid}\t{os.path.join(VIDEO_DIR, f'{vid}.mp4')}\t{url}\n")
print(f"Links saved to {saved_links}")
