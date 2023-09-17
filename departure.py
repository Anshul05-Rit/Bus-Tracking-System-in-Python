import cv2
from pyzbar.pyzbar import decode
from pymongo import MongoClient
import pyttsx3
import pymongo
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import secrets
import time
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection setup
client = MongoClient('mongodb://localhost:27017/')
db = client['bus']
collection = db['announcement']
collection_admin = db['admin']
collection_announcement = db['announcement']
collection_information = db['information']

@app.route('/')
def index():
    return render_template('signin.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/records')
def records():
    # Retrieve all documents from the MongoDB collection
    documents = list(collection.find())
    return render_template('records.html', documents=documents)

@app.route('/display_data')
def display_data():
    # Fetch all documents from the collection
    data = list(collection.find())  # Convert the cursor to a list

    # Render the template with the fetched data
    return render_template('departure.html', bus_info=data)
    
@app.route('/exitannounce', methods=['POST'])
def exitannounce():
    train_number = request.form['train_number']
    platform = request.form['platform']
    time_exit= request.form['time_exit']

    announcement_text2 = f"Attention! Bus number {train_number} is departing from platform number {platform} at {time_exit}."
    engine = pyttsx3.init()
    engine.say(announcement_text2)
    engine.runAndWait()

    return ''

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/index')
def edit():
    # Retrieve all documents from the MongoDB collection
    documents = list(collection_announcement.find())
    return render_template('index.html', documents=documents)

# Generate a secure random secret key
secret_key = secrets.token_hex(16)

# Set the secret key in your Flask application
app.secret_key = secret_key

@app.route('/logout')
def logout():
    session.pop('admin_id', None)
    return redirect(url_for('index'))

@app.route('/signin', methods=['POST'])
def signin():
    admin_id = request.form['admin_id']
    password = request.form['password']

    user = collection_admin.find_one({'admin_id': admin_id, 'password': password})
    if user is not None:
        return redirect(url_for('qr_detection'))
    else:
        return '''
            <script>
                alert('Invalid admin ID or password!');
                window.location.href = "/";
            </script>
        '''

@app.route('/qr_detection')
def qr_detection():
    return render_template('qr_detection.html')

def process_qr_code(qr_data):
    bus_info = collection_announcement.find({'train_number': qr_data})
    bus_info_list = list(bus_info)
    if len(bus_info_list) > 0:
        # Perform further processing based on your requirements
        return render_template('result.html', bus_info=bus_info_list)
    else:
        return "No matching bus number found."

@app.route('/detect_qr', methods=['POST'])
def detect_qr():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode('utf-8')
            result = process_qr_code(qr_data)
            if result is not None:
                cap.release()
                cv2.destroyAllWindows()
                return result

        cv2.imshow("QR Code Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return "No QR code detected."

@app.route('/save_info', methods=['POST'])
def save_info():
    train_number = request.form['train_number']
    departure = request.form['departure']
    platform = request.form['platform']
    time_exit= request.form['time_exit']

    new_information = {
        'train_number': train_number,
        'departure': departure,
        'platform': platform,
        'time_exit':time_exit    
    }
    collection_information.insert_one(new_information)

    return ''

@app.route('/announce', methods=['POST'])
def announce():
    train_number = request.form['train_number']
    departure = request.form['departure']
    platform = request.form['platform']

    announcement_text = f"Attention! Bus number {train_number} has arrived at {departure} stand on platform number {platform}."
    # announcement_text1 = f"This Bus is scheduled to depart within 10 minutes from platform number {platform}."

    # Convert announcement text to Marathi using a translation method or API
    marathi_announcement_text = translate_to_marathi(announcement_text)
    # marathi_announcement_text1 = translate_to_marathi(announcement_text1)

    # Speak the Marathi announcement
    speak_marathi_announcement(marathi_announcement_text)
    # speak_marathi_announcement(marathi_announcement_text1)

    return ''

def translate_to_marathi(text):
    marathi_text = text  # In this example, we are not performing actual translation

    return marathi_text

def speak_marathi_announcement(text):
    # Initialize the pyttsx3 engine for speech playback
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # You can adjust the speech rate as desired
    engine.setProperty('voice', 'marathi')  # Set the Marathi language voice

    # Speak the Marathi announcement
    engine.say(text)
    engine.runAndWait()

@app.route('/exitannounce', methods=['POST'])
def exitannounce():
    train_number = request.form['train_number']
    platform = request.form['platform']
    time_exit= request.form['time_exit']

    announcement_text2 = f"Attention! Bus number {train_number} is departing from platform number {platform} at {time_exit}."
    engine = pyttsx3.init()
    engine.say(announcement_text2)
    engine.runAndWait()

    return ''

@app.route('/edit/<id>')
def edit_info(id):
    # Retrieve the document with the specified ID from the MongoDB collection
    document = collection_announcement.find_one({'_id': ObjectId(id)})
    return render_template('edit.html', document=document)

@app.route('/update', methods=['POST'])
def update_info():
    # Retrieve the updated information from the form
    id = request.form['id']
    train_number = request.form['train_number']
    departure = request.form['departure']
    platform = request.form['platform']
    time_exit = request.form['time_exit']

    # Retrieve the document from the MongoDB collection
    document = collection_announcement.find_one({'_id': ObjectId(id)})

    # Update the document in the MongoDB collection
    collection_announcement.update_one({'_id': ObjectId(id)}, {'$set': {
        'train_number': train_number or document['train_number'],
        'departure': departure or document['departure'],
        'platform': platform or document['platform'],
        'time_exit': time_exit or document['time_exit']
    }})

    return redirect('/index')

@app.route('/delete/<id>')
def delete_info(id):
    # Delete the document with the specified ID from the MongoDB collection
    collection_announcement.delete_one({'_id': ObjectId(id)})
    return redirect('/index')


if __name__ == '__main__':
     app.run()
