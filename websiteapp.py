from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import subprocess  # ← ADDED

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["ai_blocker"]
collection = db["sites"]

# ── Hosts file setup ────────────────────────────────────
hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
redirect = "127.0.0.1"

def block_website(website):
    with open(hosts_path, "r+") as f:
        content = f.read()
        if website not in content:
            f.write(f"\n{redirect} {website}")
            f.write(f"\n{redirect} www.{website}")

def unblock_website(website):
    with open(hosts_path, "r") as f:
        lines = f.readlines()
    with open(hosts_path, "w") as f:
        for line in lines:
            if website not in line:
                f.write(line)
# ────────────────────────────────────────────────────────

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Add website
@app.route("/add", methods=["POST"])
def add_site():
    data = request.get_json()
    website = data.get("website")

    if website:
        collection.insert_one({"website": website})
        block_website(website)
        subprocess.run(["ipconfig", "/flushdns"], shell=True)
        return jsonify({"message": "Website blocked successfully!"})
    else:
        return jsonify({"message": "Invalid input!"})

# Get all websites
@app.route("/get", methods=["GET"])
def get_sites():
    sites = list(collection.find({}, {"_id": 0}))
    return jsonify(sites)

# Unblock website
@app.route("/unblock", methods=["POST"])
def unblock_site():
    data = request.get_json()
    website = data.get("website")

    if website:
        collection.delete_one({"website": website})
        unblock_website(website)
        subprocess.run(["ipconfig", "/flushdns"], shell=True)
        return jsonify({"message": "Website unblocked successfully!"})
    else:
        return jsonify({"message": "Invalid input!"})

# Run app
if __name__ == "__main__":
    app.run(debug=True)