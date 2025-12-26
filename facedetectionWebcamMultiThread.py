import cv2
import threading
import queue

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Queue to hold frames
frame_queue = queue.Queue(maxsize=10)  # Limit the queue size to prevent excessive memory usage

# Function to capture video from webcam
def capture_video():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Resize the frame to reduce processing load
        frame = cv2.resize(frame, (640, 480))
        # Put the frame into the queue
        if not frame_queue.full():
            frame_queue.put(frame)
    cap.release()

# Function to process frames and detect faces
def process_frames():
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Display the resulting frame with a bounding box around detected faces
            cv2.imshow('Webcam Video', frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# Create threads for capturing and processing video
capture_thread = threading.Thread(target=capture_video)
process_thread = threading.Thread(target=process_frames)

# Start threads
capture_thread.start()
process_thread.start()

# Wait for threads to finish
capture_thread.join()
process_thread.join()

# Cleanup
cv2.destroyAllWindows()