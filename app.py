from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import base64

app = Flask(__name__)
CORS(app, resources={
    r"/save_text": {"origins": ["http://127.0.0.1:5500"]},
    r"/save_voice": {"origins": ["http://127.0.0.1:5500"]},
    r"/delete_history": {"origins": ["http://127.0.0.1:5500"]},
    r"/assistant_response": {"origins": ["http://127.0.0.1:5500"]}
}, supports_credentials=True)


# Configure paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOICES_DIR = os.path.join(BASE_DIR, 'voices')
MSGS_FILE = os.path.join(BASE_DIR, 'MSGs.txt')

# Create required directories
os.makedirs(VOICES_DIR, exist_ok=True)
if not os.path.exists(MSGS_FILE):
    open(MSGS_FILE, 'w').close()

@app.route('/')
def serve_index():
    return send_from_directory('templates', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/save_text', methods=['POST'])
def save_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text parameter'}), 400

        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Empty text content'}), 400

        with open(MSGS_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp}: {text}\n")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_voice', methods=['POST'])
def save_voice():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'Empty audio file'}), 400

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        filepath = os.path.join(VOICES_DIR, filename)
        audio_file.save(filepath)

        return jsonify({
            'status': 'success',
            'filename': filename
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_history', methods=['POST'])
def delete_history():
    try:
        # Delete voice recordings
        for filename in os.listdir(VOICES_DIR):
            file_path = os.path.join(VOICES_DIR, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)

        # Clear text messages
        open(MSGS_FILE, 'w').close()

        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5500')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)