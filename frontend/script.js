let wavesurfer;

// 🔁 CHANGE THIS AFTER DEPLOY
const BACKEND_URL = "https://karaoke-production-016c.up.railway.app/";

function initWaveSurfer(url) {
    if (wavesurfer) {
        wavesurfer.destroy();
    }

    wavesurfer = WaveSurfer.create({
        container: '#waveform',
        waveColor: 'gray',
        progressColor: 'blue',
        height: 120
    });

    wavesurfer.load(url);
}

async function upload() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Upload a file first!");
        return;
    }

    document.getElementById("status").innerText = "Processing... ⏳";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${BACKEND_URL}/upload`, {
            method: "POST",
            body: formData
        });

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        initWaveSurfer(url);

        document.getElementById("status").innerText = "Done ✅";
    } catch (error) {
        document.getElementById("status").innerText = "Error ❌";
        console.error(error);
    }
}

function playPause() {
    if (wavesurfer) wavesurfer.playPause();
}

function changeSpeed(rate) {
    if (wavesurfer) wavesurfer.setPlaybackRate(rate);
}
