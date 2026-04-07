from flask import Flask, request, send_file
from flask_cors import CORS
import os
import uuid
import shutil
import imageio_ffmpeg as ffmpeg
from spleeter.separator import Separator

# ✅ Set ffmpeg path
os.environ["FFMPEG_BINARY"] = ffmpeg.get_ffmpeg_exe()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load Spleeter model once
separator = Separator('spleeter:2stems-16kHz')

@app.route("/")
def home():
    return "Backend running 🚀"

@app.route("/upload", methods=["POST"])
def upload():
    try:
        # ✅ 1. Validate file
        if "file" not in request.files:
            return {"error": "No file uploaded"}, 400

        file = request.files["file"]

        if file.filename == "":
            return {"error": "Empty filename"}, 400

        print("📥 File received:", file.filename)

        # ✅ 2. Get correct extension
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in [".mp3", ".wav", ".m4a"]:
            return {"error": "Unsupported file format"}, 400

        # ✅ 3. Unique file path
        unique_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, unique_id + ext)

        file.save(input_path)
        print("💾 File saved at:", input_path)

        # ✅ 4. Process audio
        separator.separate_to_file(input_path, OUTPUT_FOLDER)
        print("🎵 Processing done")

        # ✅ 5. Output path
        folder_name = os.path.splitext(os.path.basename(input_path))[0]
        instrumental_path = os.path.join(
            OUTPUT_FOLDER, folder_name, "accompaniment.wav"
        )

        print("📂 Output path:", instrumental_path)

        # ✅ 6. Check output exists
        if not os.path.exists(instrumental_path):
            return {"error": "Processing failed"}, 500

        # ✅ 7. Send file
        response = send_file(instrumental_path, as_attachment=False)

        # ✅ 8. Cleanup (VERY IMPORTANT for Railway storage)
        try:
            os.remove(input_path)
            shutil.rmtree(os.path.join(OUTPUT_FOLDER, folder_name), ignore_errors=True)
            print("🧹 Cleanup done")
        except Exception as cleanup_error:
            print("Cleanup error:", cleanup_error)

        return response

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return {"error": str(e)}, 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
