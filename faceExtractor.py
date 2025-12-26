import face_recognition
import os
from PIL import Image

# List of image file paths
#image_files = ["image1.jpg", "image2.jpg", "image3.jpg"]
input_directory = 'cropped_face'
# Directory to save extracted faces
output_dir = "extracted_faces"
#os.makedirs(output_dir, exist_ok=True)
for image_file in os.listdir(input_directory):

    image_path = os.path.join(input_directory, image_file)

    # Load the image
    image = face_recognition.load_image_file(image_path)
    
    # Find all face locations in the image
    face_locations = face_recognition.face_locations(image)
    
    # Loop through each face found in the image
    for i, face_location in enumerate(face_locations):
        # Extract the face
        top, right, bottom, left = face_location
        face_image = image[top:bottom, left:right]
        
        # Convert the face to a PIL Image
        pil_image = Image.fromarray(face_image)
        
        # Save the face image
        face_filename = os.path.join(output_dir, f"{os.path.splitext(image_file)[0]}_face_{i+1}.jpg")
        pil_image.save(face_filename)

        print(f"Saved {face_filename}")

print("Face extraction complete!")