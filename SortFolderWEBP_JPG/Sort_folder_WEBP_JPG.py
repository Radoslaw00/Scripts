import os
import shutil

def sort_images():
    base_dir = os.getcwd()
    jpg_dir = os.path.join(base_dir, "JPG")
    webp_dir = os.path.join(base_dir, "WEBP")
    os.makedirs(jpg_dir, exist_ok=True)
    os.makedirs(webp_dir, exist_ok=True)
    for filename in os.listdir(base_dir):
        if filename.lower().endswith((".jpg", ".jpeg")):
            shutil.move(os.path.join(base_dir, filename), os.path.join(jpg_dir, filename))
        elif filename.lower().endswith(".webp"):
            shutil.move(os.path.join(base_dir, filename), os.path.join(webp_dir, filename))
if __name__ == "__main__":
    sort_images()
    print("Done!")