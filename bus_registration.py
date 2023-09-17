import pymongo
from flask import Flask, request, render_template_string

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["bus"]
collection = db["announcement"]

app = Flask(__name__)

# Render the initial HTML form
@app.route("/")
def index():
    return render_template_string(open("registration.html").read())

# Handle the form submission and store data in MongoDB
@app.route("/submit", methods=["POST"])
def submit():
    bus_number = request.form["train_number"]
    conductor_name = request.form["conductor_name"]
    driver_name = request.form["driver_name"]
    platform = request.form["platform"]
    departure = request.form["departure"]

    bus_data = {
        "train_number": bus_number,
        "conductor_name": conductor_name,
        "driver_name": driver_name,
        "platform": platform,
        "departure": departure,
    }

    # Store the bus data in MongoDB
    collection.insert_one(bus_data)

    return "Bus information submitted successfully."

if __name__ == "__main__":
    app.run(debug=True)
