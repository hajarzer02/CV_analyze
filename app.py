import os
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from cv_extractor_cli import CVExtractor

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'cv_files'

import os
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from cv_extractor_cli import CVExtractor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'cv_files'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

extractor = CVExtractor()

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

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

if __name__ == '__main__':
    print("Starting Simple CV Extraction API...")
    app.run(debug=True, host='0.0.0.0', port=5000)