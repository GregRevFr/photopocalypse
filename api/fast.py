from fastapi import FastAPI, UploadFile, File
import uvicorn
from starlette.responses import StreamingResponse
import io

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
    headers = {"Classification": "This image is blurry"}
    return StreamingResponse(io.BytesIO(contents), media_type=file.content_type, headers=headers)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
