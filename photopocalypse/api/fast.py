from fastapi import FastAPI, UploadFile, File
import uvicorn
from starlette.responses import StreamingResponse
import io
import photopocalypse.prediction as prediction
import numpy as np
import cv2
from keras.models import load_model
import os
import tensorflow_hub as hub
import photopocalypse.preprocessor as preprocessor
import photopocalypse.postprocessing as postprep
from io import BytesIO
import zipfile
from cachetools import LRUCache
import logging
import json_log_formatter

app = FastAPI()


# Custom JSON Formatter for structured logging
class CustomJsonFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message, extra, record):
        extra['message'] = message
        if record.exc_info:
            extra['exc_info'] = self.formatException(record.exc_info)
        return extra


# Configure logging
formatter = CustomJsonFormatter()
file_handler = logging.FileHandler('prediction.log')
file_handler.setFormatter(formatter)
logger = logging.getLogger('photopocalypse')
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the parent directory
parent_dir = os.path.dirname(current_dir)
# Define the relative path to the model file
blurr_model_path = os.path.join(parent_dir, 'models', 'blurr_model.h5')
blurr_model = load_model(blurr_model_path)
sharpening_model_path = "https://tfhub.dev/captain-pool/esrgan-tf2/1"
sharpening_model = hub.load(sharpening_model_path)

# Cache for storing images
image_cache = LRUCache(maxsize=100)


@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"Hello": "World"}


@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    Classification = prediction.predict_blurr_percentage(image, blurr_model)
    logger.info(f"Classification: {Classification}", extra={'filename': file.filename})

    if Classification.startswith("This picture is blurry."):
        image_cache[file.filename] = contents
        logger.info(f"Added {file.filename} to cache", extra={'cache_size': len(image_cache)})
    else:
        logger.info(f"Did not add {file.filename} to cache", extra={'cache_size': len(image_cache)})

    headers = {"Classification": Classification}
    return StreamingResponse(io.BytesIO(contents), media_type=file.content_type, headers=headers)


@app.post("/upscale-images/")
async def upscale_images():
    filename, contents = next(iter(image_cache.items()))
    preprocessed_image = preprocessor.preprocess_image(contents)
    sharpened_image = prediction.predict_upscaled(preprocessed_image, sharpening_model)
    postprocessed_image = postprep.postprep_sharpening(sharpened_image)

    headers = {
        "Content-Disposition": f"attachment; filename={filename}"
    }

    return StreamingResponse(io.BytesIO(postprocessed_image), media_type="image/jpeg", headers=headers)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
