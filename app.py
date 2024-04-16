# Importing Required Modules 
from flask import Flask, request, redirect, url_for
from firebase_admin import credentials, storage
import firebase_admin
import os
from rembg import remove 
from PIL import Image
import cv2 
import numpy as np

app = Flask(__name__)

cred = credentials.Certificate("picmee-id.json")
firebase_admin.initialize_app(cred, {
       'storageBucket': 'picmee-id.appspot.com'
})

bucket = storage.bucket()

class Tool:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
    
    def remove_bg(self):
        # Processing the image 
        input = Image.open(self.input_path) 

        # Removing the background from the given Image 
        output = remove(input) 

        #Saving the image in the given path 
        output.save(self.output_path)

    def enhance(self):
        # Load the image 
        image = cv2.imread(self.input_path) 
        
        # Create the sharpening kernel 
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) 
        
        # Sharpen the image 
        sharpened_image = cv2.filter2D(image, -1, kernel) 
        
        #Save the image 
        cv2.imwrite(self.output_path, sharpened_image)

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        input_path = 'uploads/' + file.filename
        file.save(input_path)
        output_path = 'results/' + file.filename + '_no_bg.png'
        tool = Tool(input_path, output_path)
        tool.remove_bg()
        
        blob = bucket.blob(output_path)
        blob.upload_from_filename(output_path)
        blob_name = str(blob.name).replace('/', '%2F')
        result_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/{blob_name}?alt=media"
        os.remove(input_path)
        os.remove(output_path)

        return result_url


@app.route('/enhance', methods=['POST'])
def enhance():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file:
        input_path = 'uploads/' + file.filename
        file.save(input_path)
        output_path = 'results/' + file.filename + '_enhanced.jpg'
        tool = Tool(input_path, output_path)
        tool.enhance()
        
        blob = bucket.blob(output_path)
        blob.upload_from_filename(output_path)
        blob_name = str(blob.name).replace('/', '%2F')
        result_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/{blob_name}?alt=media"
        os.remove(input_path)
        os.remove(output_path)

        return result_url

if __name__ == '__main__':
    app.run(debug=True)