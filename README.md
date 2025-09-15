# CV Analysis & Job Recommendation System

A comprehensive system for analyzing CVs and providing AI-powered job recommendations using LLaMA models.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL (for full functionality)
- Git

### 1. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Environment Variables (.env):**
```env
DATABASE_URL=postgresql://username:password@localhost:5432/cv_analysis
SECRET_KEY=your-secret-key-change-this-in-production-make-it-long-and-random
ACCESS_TOKEN_EXPIRE_MINUTES=30
TOGETHER_API_KEY=your_together_api_key
HF_API_KEY=your_huggingface_api_key
```

**Create admin user (first time setup):**
```bash
cd backend
python create_admin_user.py
```

**Start the backend:**
```bash
# From project root (recommended)
python start_backend.py

# From backend directory
cd backend
python run_backend.py

# Simple Flask API (from backend directory)
cd backend
python app.py
```

### 2. AI Service Setup

```bash
cd ai-service
pip install -r requirements.txt
```

The AI service is automatically imported by the backend.

### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

## 🔧 Services

### Backend (Port 5000/8000)
- **Flask API** (`app.py`): Simple CV analysis without database
- **FastAPI** (`main.py`): Full-featured API with database, job matching, recommendations
- **Database**: PostgreSQL with SQLAlchemy ORM
- **File Processing**: PDF, DOCX, TXT support

### AI Service
- **LLaMA Integration**: Together AI and Hugging Face models
- **Job Matching**: AI-powered candidate-job matching
- **Recommendations**: Intelligent job recommendations

### Frontend (Port 3000)
- **React Application**: Modern UI with French localization
- **Dashboard**: Candidate management and job matching
- **Upload**: Drag-and-drop CV upload
- **Profile**: Detailed candidate profiles with recommendations

## 📊 Features

### CV Analysis
- ✅ PDF, DOCX, TXT file support
- ✅ Contact information extraction
- ✅ Skills and experience parsing
- ✅ Education and project extraction
- ✅ Professional summary generation

### Job Matching
- ✅ AI-powered candidate-job matching
- ✅ Missing skills identification
- ✅ Match percentage scoring
- ✅ Bulk candidate comparison

### Job Recommendations
- ✅ LLaMA-powered recommendations
- ✅ Skills-based suggestions
- ✅ Career path recommendations
- ✅ Industry-specific advice

### User Interface
- ✅ Modern, responsive design
- ✅ French language support
- ✅ Real-time upload progress
- ✅ Interactive dashboards
- ✅ Mobile-friendly interface

### Authentication & Security
- ✅ JWT-based authentication
- ✅ User registration and login
- ✅ Password hashing with bcrypt
- ✅ Protected API endpoints
- ✅ Remember me functionality
- ✅ Secure token management

## 🐳 Docker Support

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🔍 API Endpoints

### Simple API (Flask)
- `GET /health` - Health check
- `POST /analyze` - Analyze CV file
- `POST /analyze-text` - Analyze CV text

### Full API (FastAPI)

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - User logout

#### CV Management (Protected)
- `GET /candidates` - List all candidates
- `POST /upload-cv` - Upload and analyze CV
- `GET /candidate/{id}` - Get candidate details
- `POST /recommend/{id}` - Generate recommendations
- `POST /match-job` - Match candidates to job
- `PATCH /candidate/{id}/status` - Update candidate status
- `DELETE /candidates/{id}` - Delete candidate

## 🛠️ Development

### Adding New Features
1. **Backend**: Add endpoints in `backend/main.py`
2. **AI Service**: Add models/logic in `ai-service/`
3. **Frontend**: Add components in `frontend/src/`

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Testing
```bash
# Backend tests
cd backend
python test_system.py

# Frontend tests
cd frontend
npm test
```

## 📝 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `TOGETHER_API_KEY`: Together AI API key
- `HF_API_KEY`: Hugging Face API key
- `TOGETHER_MODEL`: Model name (default: meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo)

### Frontend Configuration
- Update `frontend/src/services/api.js` for API endpoints
- Modify `frontend/tailwind.config.js` for styling
- Edit `frontend/src/` components for UI changes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed description
4. Contact the development team

---

**Happy coding! 🚀**