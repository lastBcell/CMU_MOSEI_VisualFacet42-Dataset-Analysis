import h5py
import requests
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------
# Paths
# ----------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(BASE), "Data")
OUT_DIR = os.path.join(BASE, "output")
LINK_DIR = os.path.join(OUT_DIR, "Links")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(LINK_DIR, exist_ok=True)

# ----------------------------
# Read MOSEI IDs
# ----------------------------
with h5py.File(os.path.join(DATA_DIR, "CMU_MOSEI_VisualFacet42.csd"), "r") as f:
    video_keys = list(f["FACET 4.2/data"].keys())


# ----------------------------
# Extract actual YouTube ID
# ----------------------------
def extract_video_id(key):
    """
    Converts things like:
    abcdefghijk[0]
    abcdefghijk_1
    abcdefghijk

    into

    abcdefghijk
    """
    if isinstance(key, bytes):
        key = key.decode()

    m = re.match(r"^([A-Za-z0-9_-]{11})", key)
    return m.group(1) if m else key


video_ids = sorted(set(extract_video_id(v) for v in video_keys))

print(f"Segments in dataset : {len(video_keys)}")
print(f"Unique YouTube IDs  : {len(video_ids)}")

num = input("How many videos to check? (Enter for all): ")

if num.strip().isdigit():
    video_ids = video_ids[:int(num)]

print(f"Checking {len(video_ids)} videos...\n")

# ----------------------------
# Shared Session
# ----------------------------
session = requests.Session()

session.headers.update({
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})

# ----------------------------
# Check one video
# ----------------------------
def check_video(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        r = session.get(url, timeout=10)

        if r.status_code != 200:
            return video_id, f"HTTP_{r.status_code}"

        match = re.search(
            r'"playabilityStatus".*?"status":"([^"]+)"',
            r.text
        )

        if match:
            status = match.group(1)

            if status == "OK":
                return video_id, "AVAILABLE"

            return video_id, f"UNAVAILABLE({status})"

        return video_id, "UNKNOWN"

    except Exception as e:
        return video_id, f"ERROR({type(e).__name__})"


# ----------------------------
# Parallel execution
# ----------------------------
available = []
unavailable = []

workers = 20

with ThreadPoolExecutor(max_workers=workers) as executor:

    futures = {
        executor.submit(check_video, vid): vid
        for vid in video_ids
    }

    total = len(futures)

    for i, future in enumerate(as_completed(futures), start=1):

        vid, status = future.result()

        print(f"[{i}/{total}] {vid} -> {status}")

        if status == "AVAILABLE":
            available.append(vid)
        else:
            unavailable.append((vid, status))

# ----------------------------
# Save files
# ----------------------------
with open(os.path.join(LINK_DIR, "video_links.txt"), "w") as f:

    f.write("STATUS\tVIDEO_ID\tURL\n")

    for vid in available:
        f.write(
            f"AVAILABLE\t{vid}\thttps://www.youtube.com/watch?v={vid}\n"
        )

    for vid, status in unavailable:
        f.write(
            f"{status}\t{vid}\thttps://www.youtube.com/watch?v={vid}\n"
        )


with open(os.path.join(LINK_DIR, "available.txt"), "w") as f:
    for vid in available:
        f.write(f"https://www.youtube.com/watch?v={vid}\n")


with open(os.path.join(LINK_DIR, "unavailable.txt"), "w") as f:
    for vid, _ in unavailable:
        f.write(f"https://www.youtube.com/watch?v={vid}\n")


print("\n====================================")
print(f"Checked      : {len(video_ids)}")
print(f"Available    : {len(available)}")
print(f"Unavailable  : {len(unavailable)}")
print("====================================")