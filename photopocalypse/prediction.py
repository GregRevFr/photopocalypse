from keras.models import load_model
import os
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import cv2
import os


# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Define the relative path to the model file
relative_path = "models/blurr_model.h5"
# Join the current directory with the relative path
model_path = os.path.join(current_dir, relative_path)
# Load the model
model = load_model(model_path)

def predict_blurr_percentage(image):
    """
    Predicts the blur percentage of an image.

    Args:
        image (numpy.ndarray): The input image.

    Returns:
        str: The predicted blur percentage as a formatted string.
    """
    # Preprocessing
    # Check if the image needs to be converted from BGR to RGB
    if image.shape[-1] == 3:  # If it has 3 channels
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image

    # Resize the image to the expected input size of the model
    image_rgb = cv2.resize(image_rgb, dsize=(600, 600))

    # Expand dimensions to add the batch size
    image_rgb = np.expand_dims(image_rgb, axis=0)

    # Prediction
    prediction = model.predict(image_rgb)
    if prediction[0][0] > prediction[0][1]:
        classification = "blurry"
    else:
        classification = "not blurry"
    return f"This picture is {classification}. Bluriness: {prediction[0][0]:.2f} Sharpness: {prediction[0][1]:.2f}"
