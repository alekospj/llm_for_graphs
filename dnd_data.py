import kagglehub
import os
import shutil

# Set destination folder
data_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(data_dir, exist_ok=True)

# Download latest version of the dataset
path = kagglehub.dataset_download("rohitsahoo/sales-forecasting")

print("Downloaded to:", path)

# Move all files from the downloaded path to ./data/
for filename in os.listdir(path):
    src = os.path.join(path, filename)
    dst = os.path.join(data_dir, filename)
    
    # Avoid overwriting if file already exists (optional)
    if not os.path.exists(dst):
        shutil.move(src, dst)
    else:
        print(f"Skipped (already exists): {filename}")

print("Files moved to ./data/")
