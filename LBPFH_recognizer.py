import cv2
import numpy as np
import os

# Function to get the images and label data
def get_images_and_labels(dataset_path):
    image_paths = [os.path.join(dataset_path, f) for f in os.listdir(dataset_path)]
    face_samples = []
    ids = []

    for image_path in image_paths:
        # Convert the image to grayscale
        gray_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        # Get the label of the image
        id = int(os.path.split(image_path)[-1].split(".")[1])
        # Detect the face in the image
        faces = face_cascade.detectMultiScale(gray_image)
        for (x, y, w, h) in faces:
            face_samples.append(gray_image[y:y+h, x:x+w])
            ids.append(id)
    
    return face_samples, ids

# Path to the dataset
dataset_path = 'dataset'

# Load the face cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Get the faces and labels
faces, ids = get_images_and_labels(dataset_path)

# Create the LBPH face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Train the recognizer on the faces and labels
recognizer.train(faces, np.array(ids))

# Save the trained model
recognizer.save('trainer.yml')

print("Model trained and saved as 'trainer.yml'")