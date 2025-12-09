from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid
import json

from PIL import Image
from qdrant_client import QdrantClient, models
import os
from transformers import  AutoProcessor, AutoModelForZeroShotImageClassification

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 👈 Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

app.mount("/pin", StaticFiles(directory="pin"), name="pin")


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    # Generate a unique filename
    file_ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_name

    # Save the uploaded file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    client = QdrantClient(url="http://localhost:6333")
    
    model_name = "openai/clip-vit-base-patch32"
    #tokenizer = AutoTokenizer.from_pretrained(model_name)
    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModelForZeroShotImageClassification.from_pretrained(model_name)

    processed_img = processor(text=None, images=Image.open(file_path), return_tensors="pt")['pixel_values']

    im =  model.get_image_features(processed_img).detach().numpy().tolist()[0]

    search_result = client.query_points(
        collection_name="random",
        query=im,
        using="image",
        query_filter=None,
        # query_filter=Filter(
        #     must=[FieldCondition(key="title", match=MatchValue(value="algorithm"))]
        # ),
        with_payload=True,
        limit=20,
    ).points
    
    json_result = [
    {
        "id": str(point.id),
        "score": point.score,
        "payload": point.payload  # This might include fields like "image", "name", etc.
    }
    for point in search_result
]
    # Optional: Convert to JSON string if needed
    #json_output = json.dumps(json_result, indent=2)
    #print(json_output)

    return JSONResponse(content=json_result)
