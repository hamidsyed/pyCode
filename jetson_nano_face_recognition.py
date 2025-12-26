import cv2
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img

def load_dataset(dataset_path):
    # This function loads images and their labels from a directory
    images = []  # This will hold all the images
    labels = []  # This will hold labels for the images
    for label_dir in os.listdir(dataset_path):
        # Check each folder in the dataset directory
        if not label_dir.startswith('.'):
            # Ignore hidden files
            for image_path in os.listdir(dataset_path + '/' + label_dir):
                print(label_dir)
                # Load each image in grayscale (black and white)
                image = cv2.imread(dataset_path + '/' + label_dir + '/' + image_path, cv2.IMREAD_GRAYSCALE)
                images.append(image)  # Add image to the list
                labels.append(int("0" if "Unknown" in label_dir else "1"))  # Add label to the list
    return np.array(images), np.array(labels)  # Return images and labels as arrays

def get_name_by_label(label):
    # This function returns a name associated with a numerical label
    # You can add more people to this list!
    label_dict = {0: "Imaad"}
    return label_dict.get(label, "Unknown")  # If label is not found, return 'Unknown'

# Initialize face detection model using a pre-trained Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load TensorFlow model
# Make sure to replace this path with the actual path to your model
model_path = '/home/jetson/fr/tensorflow_model.h5'
model = load_model(model_path)

# Main execution starts here
if __name__ == "__main__":
    # Path to your dataset of face images
    dataset_path = "/home/jetson/fr/dataset"
    images, labels = load_dataset(dataset_path)

    # Set up face recognizer using OpenCV
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, labels)

    # Start the webcam
    webcam = cv2.VideoCapture(0)

    while True:
        ret, frame = webcam.read()

        # Convert the video frame to grayscale because face detection is faster in black and white
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Extract the face from the frame
            face_roi = gray[y:y+h, x:x+w]

            # Use the OpenCV recognizer to predict who it is
            label, confidence = recognizer.predict(face_roi)

            # Now use the TensorFlow model to get a second opinion!
            face_img = cv2.resize(face_roi, (224, 224))  # Resize to required size for the model
            face_img = face_img.astype("float") / 255.0  # Normalize the image
            face_img = img_to_array(face_img)
            face_img = np.expand_dims(face_img, axis=0)

            predictions = model.predict(face_img)
            deep_label = np.argmax(predictions[0])

            # Get names for both methods
            name = get_name_by_label(label)
            deep_name = get_name_by_label(deep_label)
            cv2.putText(frame, f"{name}/{deep_name} Confidence: {round(confidence)}", (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)

        # Show the frame with detected faces
        cv2.imshow("Face Recognition", frame)

        # Press 'q' to quit the program
        if cv2.waitKey(1) == ord('q'):
            break

    # Release the webcam and close all windows
    webcam.release()
    cv2.destroyAllWindows()
