import h5py
import numpy as np
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE), "Data")
OUT_DIR = os.path.join(BASE, "output")

f = h5py.File(os.path.join(DATA_DIR, 'CMU_MOSEI_VisualFacet42.csd'), 'r')
videos = f['FACET 4.2/data']

au_names = ["AU1","AU2","AU4","AU5","AU6","AU7","AU9","AU10",
            "AU12","AU14","AU15","AU17","AU18","AU20","AU23",
            "AU24","AU25","AU26","AU28","AU43"]

video_ids = sorted(videos.keys())

os.makedirs(OUT_DIR, exist_ok=True)

print(f"Total videos available: {len(video_ids)}")
num = input("How many videos to process? ")
num_videos = int(num) if num.isdigit() else 3
num_videos = min(num_videos, len(video_ids))

links_file = os.path.join(OUT_DIR, "AUvideo_links.txt")

header_csv = "Frame,StartTime,EndTime," + ",".join(au_names)
au_indices = np.arange(10, 30)
au_header_fmt = "{:>6} {:>9} {:>9}   " + "  ".join("{:>7}" for _ in au_names)
au_header_str = au_header_fmt.format("Frame", "Start(s)", "End(s)", *au_names)

links_lines = []

for v in range(num_videos):
    vid = video_ids[v]
    feats = videos[vid]['features'][()]
    intervals = videos[vid]['intervals'][()]
    au_data = feats[:, au_indices]

    n_frames = au_data.shape[0]
    yt_link = f"https://www.youtube.com/watch?v={vid}"

    print(f"=== Video {v+1}/{num_videos}: {vid} ===")
    print(f"YouTube: {yt_link}")
    print(f"Frames: {n_frames} | Duration: {intervals[-1,1]-intervals[0,0]:.2f}s")

    print(au_header_str)
    print("-" * len(au_header_str))
    for i in range(min(10, n_frames)):
        vals = [i, intervals[i,0], intervals[i,1]] + [au_data[i,j] for j in range(au_data.shape[1])]
        print("  ".join(f"{v:>7.3f}" if isinstance(v, float) else f"{v:>6}" if isinstance(v, int) else f"{v:>9.3f}" for v in vals))
    print()

    np.save(os.path.join(OUT_DIR, f"{vid}_au_activations.npy"), au_data)

    frame_nums = np.arange(n_frames)
    out_data = np.column_stack([
        frame_nums,
        intervals[:, 0],
        intervals[:, 1],
        au_data
    ])
    np.savetxt(
        os.path.join(OUT_DIR, f"{vid}_au_activations.csv"), out_data,
        delimiter=",", fmt="%d,%.6f,%.6f" + ",%.6f" * au_data.shape[1],
        header=header_csv, comments=""
    )
    print(f"Saved to {os.path.join(OUT_DIR, f'{vid}_au_activations.csv')}\n")

    links_lines.append(f"{vid}\thttps://www.youtube.com/watch?v={vid}\n")

with open(links_file, "w") as lf:
    lf.writelines(links_lines)
print(f"Links saved to {links_file}")

f.close()
print("Done!")
