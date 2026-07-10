import os
import shutil
import random
from pathlib import Path

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".tiff", ".tif", ".webp", ".svg", ".ico",
    ".heic", ".heif", ".raw", ".cr2", ".nef",
    ".orf", ".psd", ".eps",
}

def get_image_files(src_dir):
    images = []
    for root, _, files in os.walk(src_dir):
        for f in files:
            if Path(f).suffix.lower() in IMAGE_EXTENSIONS:
                images.append(os.path.join(root, f))
    return images

def main():
    src = input("Enter the source folder path: ").strip()
    dst = input("Enter the output folder path: ").strip()
    folder_name = input("Enter folder name: ").strip()
    batch_no = input("Enter batch number: ").strip()

    src, dst = Path(src), Path(dst)

    if not src.is_dir():
        print(f"Error: Source folder '{src}' does not exist.")
        return

    dst.mkdir(parents=True, exist_ok=True)

    images = get_image_files(src)
    if not images:
        print("No image files found in the source folder.")
        return

    random.shuffle(images)

    n = len(images)
    split = n // 3
    remainder = n % 3
    sizes = [split + (1 if i < remainder else 0) for i in range(3)]

    batches = []
    idx = 0
    for size in sizes:
        batches.append(images[idx : idx + size])
        idx += size

    for i, batch in enumerate(batches, 1):
        subfolder = dst / f"{folder_name}_{batch_no}_part_{i}"
        subfolder.mkdir(parents=True, exist_ok=True)
        for img_path in batch:
            shutil.copy2(img_path, subfolder / Path(img_path).name)

    print(f"Done! Copied {n} images into 3 subfolders under '{dst}'.")

if __name__ == "__main__":
    main()
