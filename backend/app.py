from flask import Flask, request, send_file
from flask_cors import CORS
import os
import uuid
import subprocess
from spleeter.separator import Separator

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 🔥 Ensure ffmpeg exists
def ensure_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("FFmpeg already installed ✅")
    except:
        print("Installing FFmpeg... 🔧")
        os.system("apt-get update && apt-get install -y ffmpeg")

ensure_ffmpeg()

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

    # 🎧 Process audio
    try:
        separator.separate_to_file(input_path, OUTPUT_FOLDER)
    except Exception as e:
        return {"error": str(e)}, 500

    folder_name = os.path.splitext(os.path.basename(input_path))[0]

    instrumental_path = os.path.join(
        OUTPUT_FOLDER, folder_name, "accompaniment.wav"
    )

    # 🔥 Check file exists
    if not os.path.exists(instrumental_path):
        return {"error": "Processing failed"}, 500

    return send_file(instrumental_path, as_attachment=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
