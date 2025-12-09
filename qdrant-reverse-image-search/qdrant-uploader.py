import os
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification
from qdrant_client import QdrantClient
from qdrant_client.http import models
from tqdm import tqdm
import numpy as np

client = QdrantClient("localhost", port=6333)
print("[INFO] Client created...")

################### Dataset Loading ###################
image_dataset = []
COLLECTION_NAME = 'instaimages'
BATCH_SIZE = 50
ROOT_DIR = "insta-images"   # parent folder containing Batch_1 ... Batch_11

# Traverse all Batch_* folders
for batch_num in range(1, 12):  # Batch_1 to Batch_11
    batch_dir = os.path.join(ROOT_DIR, f"Batch_{batch_num}")
    print(f"[INFO] Traversing {batch_dir}...")

    for subdir, dirs, files in os.walk(batch_dir):
        for file in files:
            if file.lower().endswith((".jpeg", ".jpg", ".png")):
                image_path = os.path.join(subdir, file)
                try:
                    image = Image.open(image_path)
                    image_dataset.append((image, batch_dir, image_path))  # keep folder info
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")

################### Loading the CLIP model ###################
print("[INFO] Loading the model...")
model_name = "openai/clip-vit-base-patch32"
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForZeroShotImageClassification.from_pretrained(model_name)

###################----Creating a qdrant collection----######################
if not client.collection_exists(COLLECTION_NAME):
    print("[INFO] Creating qdrant data collection...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "image": models.VectorParams(size=512, distance=models.Distance.COSINE),
        }
    )

###################----creating records/vectors ----######################
print("[INFO] Creating a data collection...")
records = []
for idx, (sample, batch_dir, image_path) in tqdm(enumerate(image_dataset), total=len(image_dataset)):
    processed_img = processor(text=None, images=sample, return_tensors="pt")['pixel_values']
    img_embds = model.get_image_features(processed_img).detach().numpy().tolist()[0]

    payload = {"path": image_path, "batch": batch_dir}
    records.append(models.PointStruct(id=idx, vector={"image": img_embds}, payload=payload))

###################----uploading records----######################
print("[INFO] Uploading data records to data collection...")
for i in range(0, len(records), BATCH_SIZE):
    print(f"finished {i}")
    client.upload_points(
        collection_name=COLLECTION_NAME,
        points=records[i:i + BATCH_SIZE],
    )

print("[INFO] Successfully uploaded data records to data collection!")