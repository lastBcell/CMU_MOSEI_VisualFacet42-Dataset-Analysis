import h5py
import numpy as np
import os
import sys

f = h5py.File('Data/CMU_MOSEI_VisualFacet42.csd', 'r')
videos = f['FACET 4.2/data']

au_names = ["AU1","AU2","AU4","AU5","AU6","AU7","AU9","AU10",
            "AU12","AU14","AU15","AU17","AU18","AU20","AU23",
            "AU24","AU25","AU26","AU28","AU43"]

video_ids = list(videos.keys())

out_dir = "au_outputs"
os.makedirs(out_dir, exist_ok=True)

log_file = os.path.join(out_dir, "extract_output.log")
log = open(log_file, "w")
_builtin_print = print
def log_print(*args, **kwargs):
    _builtin_print(*args, **kwargs)
    kwargs.pop("file", None)
    _builtin_print(*args, file=log, **kwargs)
print = log_print

print(f"Total videos available: {len(video_ids)}")
num = input("How many videos to process? ")
num_videos = int(num) if num.isdigit() else 3
num_videos = min(num_videos, len(video_ids))

links_dir = "links"
os.makedirs(links_dir, exist_ok=True)
links_file = os.path.join(links_dir, "AUvideo_links.txt")

print(f"Processing {num_videos} video(s)...\n")

for v in range(num_videos):
    vid = video_ids[v]
    feats = videos[vid]['features'][()]
    intervals = videos[vid]['intervals'][()]
    au_data = feats[:, 10:30]

    yt_link = f"https://www.youtube.com/watch?v={vid}"

    print(f"=== Video {v+1}/{num_videos}: {vid} ===")
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

    np.save(f"{out_dir}/{vid}_au_activations.npy", au_data)
    with open(f"{out_dir}/{vid}_au_activations.csv", "w") as out:
        out.write("Frame,StartTime,EndTime," + ",".join(au_names) + "\n")
        for i in range(au_data.shape[0]):
            out.write(f"{i},{intervals[i,0]:.6f},{intervals[i,1]:.6f},")
            out.write(",".join(f"{au_data[i,j]:.6f}" for j in range(20)) + "\n")
    print(f"Saved to {out_dir}/{vid}_au_activations.csv\n")

with open(links_file, "w") as lf:
    for v in range(num_videos):
        vid = video_ids[v]
        lf.write(f"{vid}\thttps://www.youtube.com/watch?v={vid}\n")
print(f"Links saved to {links_file}")

f.close()
log.close()
_builtin_print("Done!")
