import os
import face_recognition
import shutil
import numpy as np

# Directory containing the images
#input_directory = 'images'
input_directory = 'extracted_faces'
# Directory to save classified faces
output_directory = 'classified_faces'

# Create output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Load all images and their encodings
face_encodings = []
image_files = []
count = 0
for filename in os.listdir(input_directory):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(input_directory, filename)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)
        print(f"{count}: Processing File: {image_path}")
        count = count + 1

        if encoding:  # Ensure at least one face is found
            face_encodings.append(encoding[0])  # Take the first face encoding
            image_files.append(filename)

# Classify faces based on similarity
for i, encoding in enumerate(face_encodings):
    #matches = face_recognition.compare_faces(face_encodings, encoding)
    matches = face_recognition.face_distance(face_encodings, encoding)
    
    # Create a unique folder for each unique face
    unique_folder_name = f'face_{i}'
    unique_folder_path = os.path.join(output_directory, unique_folder_name)
    
    if not os.path.exists(unique_folder_path):
        os.makedirs(unique_folder_path)

    # Move similar faces into their respective folders
    for j, match in enumerate(matches):
        if float(match) > float(0.88) and i != j:  # If it's a match and not the same image
            print("match")
            shutil.copy(os.path.join(input_directory, image_files[j]), unique_folder_path)
            #matches = np.delete(matches, j)    
            #image_files.pop(j)

    # Also copy the original image to its folder
    shutil.copy(os.path.join(input_directory, image_files[i]), unique_folder_path)

print("Classification complete! Check the 'classified_faces' directory.")