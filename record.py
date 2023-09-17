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


@app.route('/print_records')
def print_records():
    # Retrieve all documents from the MongoDB collection
    documents = list(collection_information.find())

    # Create a BytesIO object to store the generated PDF
    pdf_buffer = BytesIO()

    # Create the PDF using ReportLab
    p = canvas.Canvas(pdf_buffer)
    p.setFont("Helvetica", 8)
    y = 750  # Initial y-coordinate for drawing the table

    # Define column widths and spacing
    col_widths = [80, 80, 80, 80, 80, 80]  # Increased column width
    col_spacing = 10

    # Draw the table headers
    headers = ['Bus Number', 'Departure', 'Time Entered', 'Platform', 'Driver Name', 'Conductor Name']
    for i, header in enumerate(headers):
        p.drawString(50 + sum(col_widths[:i]) + i * col_spacing, y, header)

    # Draw the table rows
    row_counter = 0
    page_counter = 1
    for document in documents:
        if row_counter == 20:
            # Start a new page
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 750  # Reset the y-coordinate for the new page
            row_counter = 0
            page_counter += 1
            for i, header in enumerate(headers):
                p.drawString(50 + sum(col_widths[:i]) + i * col_spacing, y, header)

        bus_number = document['train_number']
        departure = document['departure']
        platform = document['platform']
        driver_name = document['driver_name']
        conductor_name = document['conductor_name']

        # Get the current local time
        now = datetime.now()
        local_time = now.strftime("%H:%M:%S")

        row_data = [bus_number, departure, local_time, platform, driver_name, conductor_name]

        # Draw the row data
        y -= 30  # Increase vertical spacing between rows
        for i, data in enumerate(row_data):
            p.drawString(50 + sum(col_widths[:i]) + i * col_spacing, y, str(data))

        row_counter += 1

    # Save the PDF
    p.showPage()
    p.save()

    # Set the response headers for PDF
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=entry_records_page{page_counter}.pdf'

    return response

if __name__ == '__main__':
    app.run()