import pyEzviz

# Create a new Ezviz object
ezviz = pyEzviz.Ezviz('smhadil@gmail.com', 'admin@12345')

# Get the list of all your CCTV cameras
cameras = ezviz.get_cameras()

# Select the camera you want to capture the output from
camera = cameras[0]

# Start capturing the output from the camera
camera.start_capture()

# Save the output to a file
with open('output.mp4', 'wb') as f:
    while True:
        frame = camera.get_frame()
        if frame is not None:
            f.write(frame)

# Stop capturing the output from the camera
camera.stop_capture()
