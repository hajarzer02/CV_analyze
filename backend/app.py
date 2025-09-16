import os
import sys
import json
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from cv_extractor_cli import CVExtractor

load_dotenv()

# Get the path to the React build folder
REACT_BUILD_PATH = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build')

app = Flask(__name__, static_folder=REACT_BUILD_PATH, static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Enable CORS for all routes with proper OPTIONS handling
# Allow all origins for development (including ngrok)
CORS(app, 
     origins=["*"],  # Allow all origins for development
     methods=["*"],
     allow_headers=["*"],
     supports_credentials=True
)

extractor = CVExtractor()

# Serve favicon specifically
@app.route('/favicon.ico')
def favicon():
    favicon_path = os.path.join(REACT_BUILD_PATH, 'favicon.ico')
    if os.path.exists(favicon_path):
        return send_file(favicon_path, mimetype='image/x-icon')
    else:
        return jsonify({"error": "Favicon not found"}), 404

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/analyze', methods=['POST'])
def analyze_cv():
    if 'cv_file' not in request.files:
        return jsonify({"error": "No CV file provided"}), 400
    file = request.files['cv_file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not supported. Use PDF, DOCX, or TXT"}), 400
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        result = extractor.extract_cv_data(filepath)
        os.remove(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/analyze-text', methods=['POST'])
def analyze_cv_text():
    data = request.get_json()
    if not data or 'cv_text' not in data:
        return jsonify({"error": "No CV text provided"}), 400
    try:
        temp_filename = "temp_cv.txt"
        temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        with open(temp_filepath, 'w', encoding='utf-8') as f:
            f.write(data['cv_text'])
        result = extractor.extract_cv_data(temp_filepath)
        os.remove(temp_filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'txt'}

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    # If the path is an API route, let Flask handle it
    if path.startswith('api/') or path.startswith('auth/') or path in ['health', 'analyze', 'analyze-text']:
        return jsonify({"error": "API route not found"}), 404
    
    # If the path is a static file, serve it
    if path and os.path.exists(os.path.join(REACT_BUILD_PATH, path)):
        return send_from_directory(REACT_BUILD_PATH, path)
    
    # For all other routes (React routing), serve index.html
    return send_file(os.path.join(REACT_BUILD_PATH, 'index.html'))

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

if __name__ == '__main__':
    print("Starting Flask server with React frontend...")
    print(f"React build path: {REACT_BUILD_PATH}")
    print("API routes available at /api/...")
    print("Frontend available at /")
    app.run(debug=True, host='0.0.0.0', port=5000)