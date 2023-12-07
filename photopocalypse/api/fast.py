from fastapi import FastAPI, UploadFile, File
import uvicorn
from starlette.responses import StreamingResponse
import io
import photopocalypse.prediction as prediction
import numpy as np
import cv2

app = FastAPI()

@app.get("/")
def read_root():
    """
    Returns a dictionary with a greeting message.

    Returns:
        dict: A dictionary with the greeting message.
    """
    return {"Hello": "World"}

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    #TODO This needs refactoring (move preprocessing to preprocessor)
    """
    Uploads an image file and returns a streaming response with the file contents.

    Parameters:
        file (UploadFile): The image file to be uploaded.

    Returns:
        StreamingResponse: A streaming response containing the file contents.

    Raises:
        None
    """
    contents = await file.read()  # Read file contents

     # Convert bytes to a NumPy array
    nparr = np.frombuffer(contents, np.uint8) #! Here we need to add the final preprocessing
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    Classification = prediction.predict_blurr_percentage(image)
    headers = {"Classification": Classification}
    return StreamingResponse(io.BytesIO(contents), media_type=file.content_type, headers=headers)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)