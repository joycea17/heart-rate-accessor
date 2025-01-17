from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import cv2
import numpy as np
from scipy.signal import find_peaks

app = Flask(__name__)
CORS(app)

fps = 30
green_channel_values = []
duration = 10  # seconds

def extract_green_channel_realtime(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    green_channel = rgb_frame[:, :, 1]
    avg_green_intensity = np.mean(green_channel)
    return avg_green_intensity

def calculate_heartbeat_realtime(green_channel_values, fps):
    if len(green_channel_values) < fps * 5:
        return None
    normalized_signal = (green_channel_values - np.mean(green_channel_values)) / np.std(green_channel_values)
    peaks, _ = find_peaks(normalized_signal, distance=fps * 0.6)
    if len(peaks) > 1:
        peak_intervals = np.diff(peaks) / fps
        bpm = 60 / np.mean(peak_intervals)
        if 50 <= bpm <= 150:  # Filter out unrealistic values
            return round(bpm)
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    file = request.files['video_frame'].read()
    np_img = np.frombuffer(file, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    avg_green = extract_green_channel_realtime(frame)
    green_channel_values.append(avg_green)

    if len(green_channel_values) > fps * duration:
        green_channel_values.pop(0)

    bpm = calculate_heartbeat_realtime(green_channel_values, fps)
    return jsonify({"bpm": bpm if bpm else "Calculating..."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
