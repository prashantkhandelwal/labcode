import uuid
from PIL import Image
from qdrant_client import QdrantClient, models
import os
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification

ROOT_DIR = 'insta-images'
COLLECTION = 'instaimages'
BATCH_SIZE = 50

client = QdrantClient(url="http://localhost:6333")

print("[INFO] Loading the model...")
model_name = "openai/clip-vit-base-patch32"
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForZeroShotImageClassification.from_pretrained(model_name)


if not client.collection_exists(COLLECTION):
    print("[INFO] Creating qdrant data collection...")
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config= {
            "image": models.VectorParams(size=512, distance=models.Distance.COSINE),
        }
    )

#####################BATCH UPLOAD######################

records = []
for sample in os.listdir('insta-images\\' + ROOT_DIR):
    idx = uuid.uuid4().int>>64
    path = os.path.join('insta-images\\' + ROOT_DIR, sample)
    payload = {"path": path}
    sampleImage = Image.open(path)
    processed_img = processor(text=None, images = sampleImage, return_tensors="pt")['pixel_values']
    img_embds = model.get_image_features(processed_img).detach().numpy().tolist()[0]
    records.append(models.PointStruct(id=idx, vector={"image": img_embds}, payload=payload))
    print(idx)

# Upload in batch of 50
for i in range(0,len(records), BATCH_SIZE):
   print(f"finished {i}")
   client.upload_points(
       collection_name=COLLECTION,
       points=records[i:i + BATCH_SIZE],
   )
