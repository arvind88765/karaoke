from flask import Flask, request, send_file
from flask_cors import CORS
import os
import uuid
import imageio_ffmpeg as ffmpeg
from spleeter.separator import Separator

# ✅ Set ffmpeg path (VERY IMPORTANT)
os.environ["FFMPEG_BINARY"] = ffmpeg.get_ffmpeg_exe()

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
    try:
        if "file" not in request.files:
            return {"error": "No file uploaded"}, 400

        file = request.files["file"]

        print("📥 File received:", file.filename)

        unique_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, unique_id + ".mp3")

        file.save(input_path)
        print("💾 File saved at:", input_path)

        # 🎧 Process audio
        separator.separate_to_file(input_path, OUTPUT_FOLDER)
        print("🎵 Processing done")

        folder_name = os.path.splitext(os.path.basename(input_path))[0]

        instrumental_path = os.path.join(
            OUTPUT_FOLDER, folder_name, "accompaniment.wav"
        )

        print("📂 Output path:", instrumental_path)

        if not os.path.exists(instrumental_path):
            print("❌ Output file missing")
            return {"error": "Output file not found"}, 500

        print("✅ Sending file")

        return send_file(instrumental_path, as_attachment=False)

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return {"error": str(e)}, 500

    # ✅ Safety check
    if not os.path.exists(instrumental_path):
        return {"error": "Processing failed"}, 500

    return send_file(instrumental_path, as_attachment=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
