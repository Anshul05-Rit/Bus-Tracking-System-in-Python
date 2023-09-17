from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Replace with your MongoDB connection details
client = MongoClient("mongodb://localhost:27017")
db = client["bus"]
collection = db["collection"]
collection_information = db['information']

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        start_point = request.form.get("starting_point")
        destination = request.form.get("destination")

        # Fetch information based on starting_point and destination
        records = list(collection.find({"starting_point": start_point, "destination": destination}))
        return render_template(".html", records=records)

    return render_template("index.html", records=None)