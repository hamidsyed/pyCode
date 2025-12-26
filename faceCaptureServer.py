from flask import Flask, request
import os
from datetime import datetime 

app = Flask(__name__)
upload_folder = 'uploads'
os.makedirs(upload_folder, exist_ok=True)
count = 0
@app.route('/upload', methods=['POST'])
def upload_file():
    global count
    print("Receiving file... ")
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    t = datetime.now()
    ct = t.strftime("%H_%M_%S")
    count = count + 1
    filename = "Face_" + ct + "_cnt_" + str(count) + "_.jpg" 
    file_path = os.path.join(upload_folder, filename)
    print(file_path)
    file.save(('%s'%(file_path)))
    return f"File saved at {file_path}", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
