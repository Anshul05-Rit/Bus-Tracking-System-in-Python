from flask import Flask, render_template, request
from pymongo import MongoClient
from pyzbar.pyzbar import decode
from PIL import Image
import datetime

app = Flask(__name__)

# MongoDB Configuration
client = MongoClient('mongodb://localhost:27017')
db = client['bus']  # Replace 'your_database' with your actual database name
collection = db['announcement']  # Replace 'your_collection' with your actual collection name

@app.route('/demo', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded image file
        image_file = request.files['qr_image']

        if image_file:
            try:
                # Decode the QR code
                image = Image.open(image_file)
                decoded_objects = decode(image)
                if decoded_objects:
                    qr_data = decoded_objects[0].data.decode('utf-8')

                    # Check if the QR data matches a train number in the database
                    train_info = collection.find_one({'train_number': qr_data})
                    if train_info:
                        # Get the current local time
                        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        return render_template('time.html', train_info=train_info, current_time=current_time)
                    else:
                        return "Train number not found in the database."

            except Exception as e:
                return f"Error: {str(e)}"

        return "No QR code detected in the uploaded image."

    return render_template('demo.html')

if __name__ == '__main__':
    app.run(debug=True)
