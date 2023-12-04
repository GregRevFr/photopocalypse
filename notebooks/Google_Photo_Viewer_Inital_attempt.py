'''
An app to help people remove unwanted photos from Google Photos, to save space, money and the planet.
'''
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.cloud import vision

# Scopes required by the Google Photos API
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

def authenticate_google_photos():
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

# create an album in Google Photos to store the photos proposed for deletion for user review
def create_album():
    creds = authenticate_google_photos()
    service = build('photoslibrary', 'v1', credentials=creds)
    request_body = {
        'album': {'title': 'Photos for review'}
    }
    response = service.albums().create(body=request_body).execute()
    return response.get('id')

from googleapiclient.discovery import build
import os

# ... (other imports and the authenticate_google_photos function)

def get_photos_for_analysis(service, pageSize=50):
    """
    Fetches a list of photos from the user's library.
    """
    results = service.mediaItems().list(pageSize=pageSize).execute()
    items = results.get('mediaItems', [])
    return items

def analyze_photo(photo):
    """
    Analyze the photo using custom criteria.
    This is a placeholder for the actual analysis logic.
    """
    # Placeholder: Replace with actual analysis code
    return True if some_condition else False

def add_photo_to_album(service, album_id, photo_id):
    """
    Adds a photo to the specified album.
    """
    service.albums().batchAddMediaItems(
        albumId=album_id,
        body={'mediaItemIds': [photo_id]}
    ).execute()

def main():
    creds = authenticate_google_photos()
    service = build('photoslibrary', 'v1', credentials=creds)

    # Create an album for review
    review_album_id = create_album(service)

    # Retrieve photos for analysis
    photos = get_photos_for_analysis(service)

    # Analyze photos and add to the review album if they match the criteria, include the tag of the rule used to add the photo
    for photo in photos:
        if analyze_photo(photo):
            add_photo_to_album(service, review_album_id, photo['id'])

            # rules for adding photos to the album

               # add photos that are blury / not in focus

                # add photos that are dark
                # add photos that are duplicates

image1 = Image.open('path_to_image_1.jpg')
image2 = Image.open('path_to_image_2.jpg')

# Compute hashes
hash1 = imagehash.average_hash(image1)
hash2 = imagehash.average_hash(image2)

# Compare hashes
if hash1 - hash2 == 0:
    print('Images are identical.')
else:
    # The smaller the number of differing bits, the more similar the images are.
    print(f'Images are different. Hamming distance: {hash1 - hash2}')



                # add photos that are screenshots
                # add photos that have not been viewed in the last 48 months
                # add photos that are not beautiful
                # add photos that are not meaningful
                # add photos of receipts
                # add photos of documents
                # add photos of whiteboards
                # add photos of text
                # add photos of notes
                # add photos of screenshots
                # selecting best portrait from series


def analyze_portraits(image_files):
    client = vision.ImageAnnotatorClient()

    best_photo_score = 0
    best_photo = None

    for image_file in image_files:
        with open(image_file, 'rb') as file:
            content = file.read()
        image = vision.Image(content=content)
        response = client.face_detection(image=image)
        faces = response.face_annotations

        # Define your criteria for the 'best' photo
        for face in faces:
            score = (face.joy_likelihood + face.surprise_likelihood +
                     (5 - face.sorrow_likelihood) + (5 - face.anger_likelihood))
            if score > best_photo_score:
                best_photo_score = score
                best_photo = image_file

    return best_photo

# Assuming you have a list of image file paths
image_files = ['portrait1.jpg', 'portrait2.jpg', 'portrait3.jpg', ...]
best_group_portrait = analyze_portraits(image_files)
print(f"The best photo is: {best_group_portrait}")


if __name__ == '__main__':
    main()
