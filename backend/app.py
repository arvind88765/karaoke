from flask import Flask, request, send_file
from flask_cors import CORS
import os
import uuid
from spleeter.separator import Separator

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load Spleeter model
separator = Separator('spleeter:2stems')

@app.route("/")
def home():
    return "Backend running 🚀"

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]

    unique_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_FOLDER, unique_id + ".mp3")

    file.save(input_path)

    # Process audio
    separator.separate_to_file(input_path, OUTPUT_FOLDER)

    folder_name = os.path.splitext(os.path.basename(input_path))[0]

    instrumental_path = os.path.join(
        OUTPUT_FOLDER, folder_name, "accompaniment.wav"
    )

    return send_file(instrumental_path, as_attachment=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
