import h5py
import os

f = h5py.File('Data/CMU_MOSEI_VisualFacet42.csd', 'r')
videos = f['FACET 4.2/data']
video_ids = list(videos.keys())

os.makedirs("links", exist_ok=True)

with open("links/ALLvideo_links.txt", "w") as out:
    for vid in video_ids:
        out.write(f"https://www.youtube.com/watch?v={vid}\n")

print(f"Extracted {len(video_ids)} YouTube links to links/video_links.txt")
f.close()
