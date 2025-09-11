# CV Analysis & Job Recommendation System

A full-stack application that extracts information from CVs and provides AI-powered job recommendations using LLaMA 3.

## 🚀 Features

- **CV Upload & Processing**: Support for PDF, DOCX, DOC, and TXT files
- **Intelligent Data Extraction**: Automatically extracts contact info, skills, education, experience, and more
- **AI-Powered Recommendations**: Uses LLaMA 3 API to generate personalized job recommendations
- **Modern Web Interface**: React frontend with TailwindCSS for a beautiful user experience
- **Database Storage**: PostgreSQL integration for persistent data storage

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Relational database
- **SQLAlchemy**: ORM for database operations
- **PyMuPDF**: PDF text extraction
- **python-docx**: DOCX file processing

### Frontend
- **React 18**: Modern React with hooks
- **TailwindCSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **React Dropzone**: File upload with drag & drop

### AI Integration
- **LLaMA 3 API**: For generating job recommendations
- **Dummy Fallback**: Works without API key for testing

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- npm or yarn

## 🚀 Quick Start

### 1. Clone and Setup Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql://user:password@localhost:5432/cvdb
# LLAMA3_API_KEY=your_api_key_here
# LLAMA3_API_URL=https://api.example.com/llama3

# Create PostgreSQL database
createdb cvdb

# Run the FastAPI server
python main.py
```

### 2. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the React development server
npm start
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
CV_analyze/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database models and configuration
│   ├── models.py               # Pydantic models
│   ├── llama_service.py        # LLaMA 3 integration
│   ├── cv_extractor_cli.py     # CV extraction logic
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   └── App.js             # Main app component
│   └── package.json           # Node.js dependencies
├── uploads/                   # Uploaded CV files
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/cvdb
LLAMA3_API_KEY=your_llama3_api_key
LLAMA3_API_URL=https://api.example.com/llama3
```

### Database Schema

The application creates two main tables:

```sql
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    phone TEXT,
    location TEXT,
    raw_cv_path TEXT,
    extracted_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE job_recommendations (
    id SERIAL PRIMARY KEY,
    candidate_id INT REFERENCES candidates(id),
    recommendations JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 📚 API Endpoints

### Upload CV
```http
POST /upload-cv
Content-Type: multipart/form-data

file: [CV file]
```

### Get Candidate
```http
GET /candidate/{id}
```

### Generate Recommendations
```http
POST /recommend/{id}
```

### Get All Candidates
```http
GET /candidates
```

## 🎯 Usage

1. **Upload CV**: Go to the Upload page and drag & drop or select a CV file
2. **View Dashboard**: See all uploaded candidates with their basic information
3. **View Profile**: Click on a candidate to see detailed extracted information
4. **Generate Recommendations**: Use the AI-powered recommendation system to get job suggestions

## 🤖 AI Integration

The system integrates with LLaMA 3 API for generating job recommendations. If no API key is provided, it falls back to dummy recommendations for testing purposes.

### LLaMA 3 Prompt

The system sends candidate data to LLaMA 3 with this prompt:

```
You are an assistant that recommends job roles based on CV data.
Here is the candidate profile (JSON):
{candidate_json}

Return 3-5 job titles suitable for this candidate with a one-sentence explanation each in JSON format.
```

## 🧪 Testing

### Backend Testing
```bash
# Run FastAPI server
python main.py

# Test API endpoints
curl -X POST "http://localhost:8000/upload-cv" -F "file=@sample_cv.pdf"
```

### Frontend Testing
```bash
cd frontend
npm start
# Open http://localhost:3000
```

## 🚀 Deployment

### Backend Deployment
1. Set up PostgreSQL database
2. Configure environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run with: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Frontend Deployment
1. Build the React app: `npm run build`
2. Serve the `build` folder with a web server
3. Update API URL in production

## 🔒 Security Notes

- Store API keys securely in environment variables
- Validate file uploads on both frontend and backend
- Implement proper error handling and logging
- Consider rate limiting for API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the console logs for errors
3. Ensure all environment variables are set correctly
4. Verify database connection and permissions