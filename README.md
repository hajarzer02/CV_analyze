#  CV exctrator System

##  Quick Start

### Activate venv environnement
```bash
python -m venv venv
.\venv\Scripts\activate
```
### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start REST API Server
```bash
python app.py
```
API available at `http://localhost:5000`

### 3. To view outputs
```bash
python main.py

### 4. Test with Postman
Import `postman_collection.json` or see `API_TESTING.md`

##  Project Structure

```
PFE_/
├── core/
│   └── extractor.py            # CV text extraction (PDF, DOCX, TXT)
├── cv_files/                   # Input CV files
├── outputs/                    # Analysis results (JSON)
├── app.py                      # REST API server (Flask)
├── main.py                     # Command-line interface
├── postman_collection.json     # Postman test collection
├── API_TESTING.md              # API testing guide
└── requirements.txt
```

##  Features

- **REST API**: Flask-based API for easy integration
- **Multi-format Support**: PDF, DOCX, TXT files
- **Intelligent Job Matching**: Context-aware recommendations
- **Career Advice**: Personalized development suggestions
- **Fallback System**: Works even when GPT API is unavailable
- **Postman Ready**: Complete testing collection included

##  API Endpoints

- `GET /health` - Check API status
- `POST /analyze` - Upload and analyze CV file
- `POST /analyze-text` - Analyze CV text directly



### API Testing
```bash
# Start server
python app.py

# Test endpoints
curl http://localhost:5000/health
```

### Command Line
```bash
python main.py
```

## 🔧 Configuration

- **Temperature**: 0.7 (balanced creativity/consistency)
- **Max Tokens**: 1500 (comprehensive responses)
- **Max File Size**: 16MB
- **Port**: 5000 (configurable)

## 📝 Requirements

- Python 3.8+
- Internet connection for API calls
- Flask for REST API

## 🚨 Recent Changes

- ✅ Created REST API with Flask
- ✅ Added Postman collection for testing
- ✅ Removed duplicate cv_analyzer directory
- ✅ Cleaned up unused files (test_gpt.py)
- ✅ Fixed all import dependencies
- ✅ Added comprehensive API documentation
- ✅ Integrated fallback system for GPT unavailability

