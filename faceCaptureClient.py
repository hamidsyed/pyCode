import cv2
import requests
import numpy as np
import datetime 
# Load the face cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the webcam
cap = cv2.VideoCapture(0)

server_url = 'http://<server_ip>:<server_port>/upload'  # Replace with your server's IP and port

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(30, 30))
    
    for (x, y, w, h) in faces:
        # Extract the face from the frame
        face = frame[y:y+h, x:x+w]
        
        # Encode the face as a JPEG image
        _, img_encoded = cv2.imencode('.jpg', face)
        
        # Send the face to the server
        response = requests.post(server_url, files={'file': img_encoded.tobytes()})
        print(f"Server response: {response.text}")
    
    # Display the resulting frame
    cv2.imshow('Face Detection', frame)
    
    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
