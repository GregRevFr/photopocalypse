import streamlit as st
from streamlit_option_menu import option_menu
import requests
import os
import json
import base64
from PIL import Image
from io import BytesIO
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import numpy as np
from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.preprocessing import image
import matplotlib.pyplot as plt
import hdbscan
from sklearn.metrics.pairwise import pairwise_distances

# Scopes for Google Photos API
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

# Set page config
st.set_page_config(layout="wide")

# CSS styles
st.markdown(
    """
    <style>
    body, .stApp {
        background: linear-gradient(45deg, #bfe9ff, #ffffff) !important;
        width: 100vw !important;
        height: 100vh !important;
        margin: 0 !important;
        overflow: auto !important;
    }
    .card {
        transition: transform 0.2s; /* Smooth transition for the transform */
    }
    .card:hover {
        transform: scale(1.05); /* Increase the scale slightly when hovered */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Function definitions for PhotoUnion
def get_google_photos_service(credentials):
    print(credentials)
    flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
    creds = flow.run_local_server(port=0)
    return build('photoslibrary', 'v1', credentials=creds, static_discovery=False)


def list_media_items(service, pageSize=100):
    results = service.mediaItems().list(pageSize=pageSize).execute()
    items = results.get('mediaItems', [])
    return items


def extract_features_from_url(url, model):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.convert('RGB')
    img = img.resize((224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    return model.predict(img_array).flatten()


def process_images(credentials):
    service = get_google_photos_service(credentials)
    media_items = list_media_items(service)
    model = ResNet50(weights='imagenet', include_top=False)
    features_list = [extract_features_from_url(item['baseUrl'], model) for item in media_items]
    distance_matrix = pairwise_distances(features_list, metric='cosine').astype(np.float64)
    clusterer = hdbscan.HDBSCAN(metric='precomputed', min_cluster_size=2, min_samples=1, cluster_selection_epsilon=0.1)
    clusterer.fit(distance_matrix)
    labels = clusterer.labels_
    image_groups = {}
    for i, label in enumerate(labels):
        if label != -1:
            if label in image_groups:
                image_groups[label].append(media_items[i]['baseUrl'])
            else:
                image_groups[label] = [media_items[i]['baseUrl']]
    return image_groups


def display_image_groups(image_groups):
    for group_id, images in image_groups.items():
        if len(images) > 0:
            st.write(f"Group {group_id} ({len(images)} images):")
            cols = st.columns(len(images))
            for col, img_url in zip(cols, images):
                img = Image.open(BytesIO(requests.get(img_url).content))
                col.image(img, use_column_width=True)


# Function to send file to server
def send_file_to_server(file):
    url = 'https://phurge-api-ieuwqkua2q-ew.a.run.app/upload-image/'
    files = {'file': (file.name, file, 'multipart/form-data')}
    response = requests.post(url, files=files)
    return response


# Function to convert image to base64
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


# Add this new function to send selected files to the deblur API
def deblur_image(file):
    url = 'https://phurge-ieuwqkua2q-ew.a.run.app/upload-image/'
    files = {'file': (file.name, file, 'multipart/form-data')}
    response = requests.post(url, files=files)
    return response


# Function to generate HTML content for a card
def card(title, text, image, styles):
    image_container_height = "200px"
    card_style = "; ".join(f"{key}: {value}" for key, value in styles.get("card", {}).items())
    text_style = "; ".join(f"{key}: {value}" for key, value in styles.get("text", {}).items())

    html_content = f"""
    <div class="card" style="{card_style}">
        <div style="height: {image_container_height};">
            <img src="{image}" alt="{title}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 7px;">
        </div>
    </div>
    """
    return html_content


def image_logo():
    col1, col2, col3 = st.columns([1, 2, 3])
    # Leave the first column empty
    with col3:
        image_path = 'photos/logo.png'
        print(f"Image Path: {image_path}")

        # Check if the file exists
        if os.path.exists(image_path):
            print("Image file exists.")
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()
        # Display the image with custom CSS for positioning, size, rounded corners, and border
        st.markdown(
            f'<img src="data:image/png;base64,{encoded_image}" style="position: absolute; top: 0px; right: 0px; max-width: 40%;">',
            unsafe_allow_html=True)


# Function to display a sidebar menu
def sidebar_menu():
    with st.sidebar:
        selected = option_menu(
            menu_title="PHOTOPOCALYPSE",
            options=["HOME", "PHOTOPOCALYPSE", "PHOTOUNION"],
            icons=["house", "rocket", "camera"],
            menu_icon="cast",
            default_index=1,
            styles={
                "container": {"padding": "0!important", "background-color": "#D5D5D8"},
                "icon": {"color": "#0080FF", "font-size": "25px"},
                "nav-link-selected": {"background-color": "#012862", "color": "#FFFFFF"},
            }
        )

        # Display the legend in the sidebar
        st.markdown("""
            <div style="position: fixed; bottom: 20px; left: 40px;">
                <h1 style='color: #012862; font-size: 20px; font-family: sans-serif;'>
                Legend:</h1>
                <p style ='font-size: 17px;'><span style="display: inline-block; width: 30px; height: 7px; background-color: red;"></span> Blur picture</p>
                <p style ='font-size: 17px;'><span style="display: inline-block; width: 30px; height: 7px; background-color: green;"></span> Picture not blur</p>
            </div>
            """,
                    unsafe_allow_html=True
                    )

    if selected == "PHOTOPOCALYPSE":
        build_blurnotblur_page()
    if selected == "PHOTOUNION":
        build_photounion_page()
    elif selected == "home":
        st.write("Welcome home!")


# Function to build the main page
def build_blurnotblur_page():
    # Custom CSS to hide the file uploader status
    st.markdown("""
        <style>
        /* This hides the uploaded file information in Streamlit */
        .st-emotion-cache-fqsvsg.e1b2p2ww9 {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Custom CSS to text
    st.markdown(
        """
        <h1 style='color: #012862; font-size: 36px; font-family: sans-serif; font-weight: bold;'>
            Photopocalypse </h1>
        </h1>
        """,
        unsafe_allow_html=True
    )

    # Container for the file uploader
    with st.container():
        uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True,
                                          type=["txt", "csv", "pdf", "json", "png", "jpg", "svg", "jpeg"])

        # Check if files are uploaded before attempting to display them
        if uploaded_files:
            blurry_images = []
            image_cards = []
            for file in uploaded_files:
                response = send_file_to_server(file)

                if response.status_code == 200:
                    image = Image.open(BytesIO(response.content))
                    base64_image = image_to_base64(image)
                    headers = response.headers
                    blurriness = headers.get("classification")
                    border_color = "red" if blurriness and blurriness.startswith("This picture is blurry.") else "green"

                    if border_color == "red":
                        # Add to blurry images list if the image is blurry
                        blurry_images.append(file)

                    # Create a dictionary for each image with its details
                    image_cards.append({
                        "file_name": file.name,
                        "base64_image": base64_image,
                        "border_color": border_color
                    })

            # Sort the list of cards by border_color, green first then red
            image_cards.sort(key=lambda x: x['border_color'], reverse=True)

            # Display sorted cards
            with st.container():
                cols = st.columns(3)
                col_index = 0

                for image_card in image_cards:
                    card_html = card(
                        title=image_card["file_name"],
                        text="",
                        image=f"data:image/png;base64,{image_card['base64_image']}",
                        styles={
                            'card': {
                                "width": "100%",
                                "height": "auto",
                                "margin": "10px",
                                "border-radius": "10px",
                                "box-shadow": "0 0 10px rgba(0,0,0,0.5)",
                                "display": "flex",
                                "flex-direction": "column",
                                "align-items": "center",
                                "border-color": image_card["border_color"],
                                "border-style": "solid",
                                "border-width": "4px"
                            }
                        }
                    )
                    cols[col_index % 3].markdown(card_html, unsafe_allow_html=True)
                    col_index += 1

        # Button to deblur all blurry images
        if st.button("Deblur Blurry Images"):
            if not blurry_images:
                st.warning("No blurry images to deblur.")
            else:
                for file in blurry_images:
                    # Send the file to the deblur API
                    response = deblur_image(file)
                    if response.status_code == 200:
                        # Assuming the API returns the image directly
                        deblurred_image = Image.open(BytesIO(response.content))
                        st.image(deblurred_image, caption=f"Deblurred {file.name}")
                    else:
                        st.error(f"Failed to deblur {file.name}")


# Function to build the main page
def build_photounion_page():
    # Custom CSS to hide the file uploader status
    st.title("PhotoUnion")
    st.write("PhotoUnion groups your similar images together using advanced machine learning techniques.")
    st.write("PhotoUnion groups your similar images together using advanced machine learning techniques.")
    st.write("PhotoUnion groups your similar images together using advanced machine learning techniques.")
    st.write("PhotoUnion groups your similar images together using advanced machine learning techniques.")

    uploaded_credentials = st.file_uploader("Upload Google API Credentials", type=["json"])

    if uploaded_credentials is not None:
        credentials_json = json.loads(uploaded_credentials.getvalue().decode())
        image_groups = process_images(credentials_json)
        display_image_groups(image_groups)


if __name__ == '__main__':
    # Use the gradient class for the whole page
    st.markdown('<div class="gradient-background">', unsafe_allow_html=True)
    image_logo()
    sidebar_menu()
    # Close the div tag at the end of your content
    st.markdown('</div>', unsafe_allow_html=True)
