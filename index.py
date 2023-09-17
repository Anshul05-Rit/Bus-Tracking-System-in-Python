import cv2
from pyzbar.pyzbar import decode
from pymongo import MongoClient
import pyttsx3
import pymongo
from flask import Flask, render_template, request, redirect, url_for
from googletrans import Translator
from gtts import gTTS
import os
import sys
import pygame
from bson.objectid import ObjectId
from flask import make_response
from io import BytesIO
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib.pagesizes import letter

app = Flask(__name__)
client = pymongo.MongoClient('mongodb://localhost:27017')
db = client['bus']
collection_admin = db['admin']
collection_announcement = db['announcement']
collection_information = db['information']
collection = db['announcement']
collection_bus = db["collection"]

@app.route('/')
def index():
    return render_template('qr_detection.html')

@app.route('/index')
def result():
    return render_template('index.html')

@app.route('/records_printing')
def records():
    documents = list(collection_information.find())
    return render_template('records_printing.html', documents=documents)

@app.route('/display_data')
def display_data():
    data = list(collection.find())
    return render_template('departure.html', bus_info=data)

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/edit_page')
def edit():
    documents = list(collection_announcement.find())
    return render_template('edit_page.html', documents=documents)

@app.route('/qr_detection')
def qr_detection():
    return render_template('qr_detection.html')

def process_qr_code(qr_data):
    bus_info = collection_announcement.find({'train_number': qr_data})
    bus_info_list = list(bus_info)
    if len(bus_info_list) > 0:
        now = datetime.now()
        local_time = now.strftime("%H:%M:%S")
        return render_template('index.html', bus_info=bus_info_list, local_time=local_time)
    else:
        return '''
            <script>
                alert('Qr code is not Detected !');
                window.location.href = "/qr_detection";
            </script>
        '''

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
    driver_name = request.form['driver_name']
    conductor_name = request.form['conductor_name']
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    new_information = {
        'train_number': train_number,
        'departure': departure,
        'platform': platform, 
        'conductor_name': conductor_name,
        'driver_name': driver_name,
        'current_time': current_time
    }
    collection_information.insert_one(new_information)

    return ''

def translate_text(source_text, target_lang):
    translator = Translator()
    translation = translator.translate(source_text, src='en', dest=target_lang)
    translated_text = translation.text
    return translated_text

def text_to_speech(text, lang='en', filename='temp.mp3'):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

    pygame.mixer.init()
    sound = pygame.mixer.Sound(filename)
    sound.play()
    while pygame.mixer.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()
    os.remove(filename)

@app.route('/announce', methods=['POST'])
def announce():
    train_number = request.form['train_number']
    departure = request.form['departure']
    platform = request.form['platform']

    announcement_text = f"Attention! Bus number {train_number} has arrived at {departure} stand on platform number {platform}."
    
    target_language = "mr"  # Target language code for Marathi
    translated_text = translate_text(announcement_text, target_language)
    
    if os.name == 'nt':
        os.system('chcp 65001')

    text_to_speech(translated_text, lang=target_language)

    return ''

@app.route('/exitannounce', methods=['POST'])
def exitannounce():
    train_number = request.form['train_number']
    departure = request.form['departure']
    platform = request.form['platform']
    time_exit = request.form['time_exit']

    announcement_text1 = f"Attention! Bus number {train_number} has arrived at {departure} stand on platform number {platform} at {time_exit}."

    target_language1 = "mr"  # Target language code for Marathi
    translated_text1 = translate_text(announcement_text1, target_language1)

    if os.name == 'nt':
        os.system('chcp 65001')

    text_to_speech(translated_text1, lang=target_language1, filename='temp1.mp3')

    return '''
                <script>
                alert('Departure announcement made');
            </script>
            '''

@app.route('/edit/<id>')
def edit_info(id):
    document = collection_announcement.find_one({'_id': ObjectId(id)})
    return render_template('edit.html', document=document)

@app.route('/update', methods=['POST'])
def update_info():
    id = request.form['id']
    train_number = request.form['train_number']
    driver_name = request.form['driver_name']
    conductor_name = request.form['conductor_name']
    departure = request.form['departure']
    platform = request.form['platform']

    document = collection_announcement.find_one({'_id': ObjectId(id)})

    collection_announcement.update_one({'_id': ObjectId(id)}, {'$set': {
        'train_number': train_number or document['train_number'],
        'driver_name': driver_name or document['driver_name'],
        'conductor_name': conductor_name or document['conductor_name'],
        'departure': departure or document['departure'],
        'platform': platform or document['platform']
    }})

    return redirect('/edit_page')

@app.route('/delete/<id>')
def delete_info(id):
    collection_announcement.delete_one({'_id': ObjectId(id)})
    return redirect('/edit_page')

@app.route('/print_records')
def print_records():
    documents = list(collection_information.find())
    pdf_buffer = BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=letter)
    p.setFont("Helvetica", 9)
    y = 700

    col_widths = [80, 80, 80, 80, 80, 80]
    col_spacing = 10

    headers = ['Bus Number', 'Driver Name', 'Conductor Name', 'Departure', 'Arrival Time', 'Platform']

    for i, header in enumerate(headers):
        p.drawString(50 + sum(col_widths[:i]) + i * col_spacing, y, header)

    row_counter = 0
    page_counter = 1
    for document in documents:
        if row_counter == 20:
            p.showPage()
            p.setFont("Helvetica", 8)
            y = 700
            row_counter = 0
            page_counter += 1
            for i, header in enumerate(headers):
                p.drawString(50 + sum(col_widths[:i]) + i * col_spacing, y, header)

        bus_number = document['train_number']
        departure = document['departure']
        platform = document['platform']
        driver_name = document['driver_name']
        conductor_name = document['conductor_name']
        current_time = document['current_time']

        row_data = [bus_number, driver_name, conductor_name, departure, current_time, platform]

        y -= 30
        for i, data in enumerate(row_data):
            p.drawString(50 + sum(col_widths[:i]) + i * col_spacing, y, str(data))

        row_counter += 1

    p.showPage()
    p.save()

    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=entry_records_page{page_counter}.pdf'

    return response

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        start_point = request.form.get("starting_point")
        destination = request.form.get("destination")

        # Fetch information based on starting_point and destination
        records = list(collection_bus.find({"starting_point": start_point, "destination": destination}))
        return render_template("search.html", records=records)

    return render_template("search.html", records=None)


if __name__ == '__main__':
    app.run()
