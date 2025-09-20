# Automated Resume Relevance Check System

## Innomatics Research Labs - Enterprise Solution

A comprehensive AI-powered resume evaluation system designed to automate the recruitment process for Innomatics Research Labs across Hyderabad, Bangalore, Pune, and Delhi NCR locations.

## 🚀 Features

### Core Functionality
- **AI-Powered Resume Parsing**: Supports PDF, DOC, DOCX, and TXT formats with intelligent text extraction
- **Job Description Analysis**: Advanced keyword extraction and skill requirement analysis
- **Relevance Scoring**: Sophisticated 0-100 scoring system with detailed breakdowns
- **Personalized Feedback**: AI-generated improvement suggestions for candidates
- **Batch Processing**: Handle thousands of resumes efficiently
- **Real-time Dashboard**: Comprehensive analytics and monitoring

### Technical Features
- **Multi-format Support**: PDF, DOC, DOCX, TXT resume parsing
- **AI Integration**: OpenAI GPT models for intelligent analysis
- **Scalable Architecture**: Built with Flask and SQLAlchemy
- **RESTful API**: Complete API for system integration
- **Role-based Access**: Admin, Recruiter, Mentor, and Student roles
- **Security**: Comprehensive validation and security measures

## 📋 Requirements

### System Requirements
- Python 3.8+
- PostgreSQL 12+ (or SQLite for development)
- Redis 6+ (for caching and background tasks)
- 4GB+ RAM
- 10GB+ storage

### Python Dependencies
- Flask 2.3.3
- SQLAlchemy 2.0.21
- OpenAI 1.3.0
- scikit-learn 1.3.2
- NLTK 3.8.1
- spaCy 3.7.2
- PyPDF2 3.0.1
- python-docx 0.8.11

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd automated-resume-relevance-check
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 5. Environment Configuration
```bash
cp env.example .env
# Edit .env with your configuration
```

### 6. Database Setup
```bash
# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 7. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection string | `sqlite:///resume_evaluator.db` |
| `OPENAI_API_KEY` | OpenAI API key | Required for AI features |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `UPLOAD_FOLDER` | File upload directory | `uploads` |
| `MAX_CONTENT_LENGTH` | Maximum file size | `16777216` (16MB) |

### Database Configuration

#### SQLite (Development)
```python
DATABASE_URL=sqlite:///resume_evaluator.db
```

#### PostgreSQL (Production)
```python
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

## 📊 Usage

### 1. User Registration
- Navigate to `/auth/register`
- Create accounts for different user roles:
  - **Admin**: Full system access
  - **Recruiter**: Job and evaluation management
  - **Mentor**: Student guidance and feedback
  - **Student**: Resume upload and feedback viewing

### 2. Job Description Management
- Create job descriptions with detailed requirements
- System automatically analyzes and extracts skills
- Set priority levels and deadlines

### 3. Resume Upload and Parsing
- Upload resumes in supported formats
- AI automatically extracts candidate information
- Parsing confidence scores provided

### 4. Resume Evaluation
- Match resumes against job descriptions
- Get detailed relevance scores (0-100)
- Receive fit verdicts (High/Medium/Low)
- Access personalized feedback for candidates

### 5. Batch Processing
- Upload multiple resumes at once
- Evaluate against single or multiple jobs
- Export results for further analysis

## 🔌 API Usage

### Authentication
```bash
# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Resume Upload
```bash
# Upload resume
curl -X POST http://localhost:5000/api/resumes \
  -H "Authorization: Bearer <token>" \
  -F "file=@resume.pdf"
```

### Create Evaluation
```bash
# Evaluate resume against job
curl -X POST http://localhost:5000/api/evaluations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"resume_id": 1, "job_id": 1}'
```

### Batch Evaluation
```bash
# Batch evaluate multiple resumes
curl -X POST http://localhost:5000/api/batch/evaluate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"job_id": 1, "resume_ids": [1, 2, 3, 4, 5]}'
```

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   REST API      │    │   Admin Panel   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Flask Application │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Resume Parser   │    │ Job Analyzer    │    │ Relevance Scorer│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │  (PostgreSQL)   │
                    └─────────────────┘
```

### Database Schema

- **Users**: User management and authentication
- **JobDescriptions**: Job requirements and criteria
- **Resumes**: Parsed resume data and metadata
- **Evaluations**: Resume-job matching results
- **Feedback**: Personalized improvement suggestions

## 🔒 Security Features

- **Input Validation**: Comprehensive validation for all inputs
- **File Security**: Malicious content detection
- **SQL Injection Protection**: Parameterized queries
- **XSS Prevention**: Input sanitization
- **CSRF Protection**: Token-based protection
- **Role-based Access**: Granular permission system

## 📈 Performance

### Scalability
- **Concurrent Processing**: Handle multiple evaluations simultaneously
- **Background Tasks**: Celery for long-running operations
- **Caching**: Redis for improved performance
- **Database Optimization**: Indexed queries and connection pooling

### Monitoring
- **Health Checks**: System status monitoring
- **Logging**: Comprehensive logging system
- **Metrics**: Performance metrics collection
- **Error Tracking**: Detailed error reporting

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_resume_parser.py
```

### Test Coverage
- Unit tests for all services
- Integration tests for API endpoints
- End-to-end tests for complete workflows
- Performance tests for scalability

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t resume-evaluator .

# Run container
docker run -p 5000:5000 resume-evaluator
```

### Production Deployment
1. Set up PostgreSQL database
2. Configure Redis for caching
3. Set up reverse proxy (Nginx)
4. Configure SSL certificates
5. Set up monitoring and logging
6. Deploy with Gunicorn

## 📝 API Documentation

### Endpoints

#### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout

#### Jobs
- `GET /api/jobs` - List jobs
- `POST /api/jobs` - Create job
- `GET /api/jobs/{id}` - Get job details

#### Resumes
- `GET /api/resumes` - List resumes
- `POST /api/resumes` - Upload resume
- `GET /api/resumes/{id}` - Get resume details

#### Evaluations
- `GET /api/evaluations` - List evaluations
- `POST /api/evaluations` - Create evaluation
- `GET /api/evaluations/{id}` - Get evaluation details
- `POST /api/batch/evaluate` - Batch evaluation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

### v1.0.0 (Current)
- Initial release
- Core resume parsing and evaluation
- AI-powered scoring system
- Web dashboard and API
- Multi-role user management

## 📞 Contact

**Innomatics Research Labs**
- Website: [innomatics.in](https://innomatics.in)
- Email: support@innomatics.in
- Phone: +91-XXXXXXXXXX

---

**Built with ❤️ for Innomatics Research Labs**
