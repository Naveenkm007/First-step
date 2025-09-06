# MemoriaVault Backend

A FastAPI-based backend for MemoriaVault - your personal memory digitizer. This backend handles file uploads, runs OCR/ASR locally, extracts metadata, performs sentiment analysis, and stores results in SQLite with full-text search capabilities.

## Features

- 📁 **File Upload**: Accept images (JPEG, PNG) and audio files (MP3, WAV)
- 🔍 **OCR Processing**: Extract text from images using Tesseract
- 🎵 **ASR Processing**: Transcribe audio using OpenAI Whisper
- 📊 **Sentiment Analysis**: Analyze emotional tone using TextBlob and VADER
- 🗄️ **SQLite Database**: Store memories with FTS5 full-text search
- 🔍 **Search API**: Full-text search across titles, content, and metadata
- 📸 **EXIF Extraction**: Extract date and location from image metadata
- 🌐 **CORS Enabled**: Ready for React frontend integration

## Quick Start

### Prerequisites

Before running the backend, you need to install system dependencies:

#### Windows
```bash
# Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR

# Install FFmpeg
# Download from: https://ffmpeg.org/download.html
# Add to PATH: C:\ffmpeg\bin
```

#### macOS
```bash
# Install Tesseract OCR
brew install tesseract

# Install FFmpeg
brew install ffmpeg
```

#### Ubuntu/Debian
```bash
# Install Tesseract OCR
sudo apt-get update
sudo apt-get install tesseract-ocr

# Install FFmpeg
sudo apt-get install ffmpeg
```

### Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (for sentiment analysis):
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
   ```

### Running the Server

```bash
# Start the development server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/

## API Endpoints

### Upload Memory
```bash
POST /api/upload
Content-Type: multipart/form-data

Fields:
- file: Image or audio file
- title: Memory title (required)
- person: Person name (optional)
```

**Example using curl**:
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg" \
  -F "title=My Memory" \
  -F "person=John Doe"
```

**Expected Response**:
```json
{
  "status": "ok",
  "memory": {
    "id": 123,
    "title": "My Memory",
    "text": "Extracted text from image...",
    "date": "2023-12-01",
    "location": "New York",
    "sentiment": 0.12,
    "media_path": "/media/uploads/uuid.jpg",
    "media_type": "image"
  }
}
```

### Search Memories
```bash
GET /api/search?q=search_term
```

**Example using curl**:
```bash
curl -X GET "http://localhost:8000/api/search?q=grandma" \
  -H "accept: application/json"
```

**Expected Response**:
```json
{
  "status": "ok",
  "results": [
    {
      "id": 123,
      "title": "Grandma Letter",
      "snippet": "Title: <mark>Grandma</mark> Letter | Text: Dear <mark>grandma</mark>...",
      "date": "1954-06-12",
      "sentiment": 0.8,
      "media_type": "image",
      "media_path": "/media/uploads/letter.jpg"
    }
  ]
}
```

### Get Memory by ID
```bash
GET /api/memory/{memory_id}
```

**Example using curl**:
```bash
curl -X GET "http://localhost:8000/api/memory/123" \
  -H "accept: application/json"
```

### List All Memories
```bash
GET /api/memories?limit=20&offset=0
```

## Database Schema

The backend uses SQLite with the following tables:

### memories
- `id`: Primary key
- `title`: Memory title
- `text`: Extracted text content
- `date`: Date from EXIF or user input
- `location`: Location information
- `sentiment`: Sentiment score (-1.0 to 1.0)
- `media_path`: Path to uploaded file
- `media_type`: 'image' or 'audio'
- `person`: Associated person
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### memories_fts
- FTS5 virtual table for full-text search
- Automatically synchronized with memories table via triggers

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
# Database
DATABASE_PATH=memoriavault.db

# File uploads
UPLOAD_DIR=uploads
MAX_FILE_SIZE=20971520  # 20MB in bytes

# Whisper model size (tiny, base, small, medium, large)
WHISPER_MODEL=small

# CORS origins
CORS_ORIGINS=http://localhost:3000
```

### Tesseract Configuration
If Tesseract is not in your PATH, set the environment variable:

```bash
# Windows
set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata

# macOS/Linux
export TESSDATA_PREFIX=/usr/local/share/tessdata
```

## Testing

### Run Unit Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

### Test Upload Endpoint
```bash
# Test with a sample image
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@test_image.jpg" \
  -F "title=Test Memory" \
  -F "person=Test Person"
```

### Test Search
```bash
# Test search functionality
curl -X GET "http://localhost:8000/api/search?q=test"
```

## Troubleshooting

### Common Issues

1. **Tesseract not found**:
   ```
   ERROR: Tesseract not found. Please install Tesseract OCR.
   ```
   **Solution**: Install Tesseract and add it to your PATH.

2. **FFmpeg not found**:
   ```
   ERROR: FFmpeg not found
   ```
   **Solution**: Install FFmpeg and add it to your PATH.

3. **Whisper model download fails**:
   ```
   ERROR: Failed to load Whisper model
   ```
   **Solution**: Ensure you have internet connection for first-time model download.

4. **CORS errors**:
   ```
   ERROR: CORS policy blocks request
   ```
   **Solution**: Check CORS configuration in `app.py`.

5. **File upload fails**:
   ```
   ERROR: Upload failed
   ```
   **Solution**: Check file size (max 20MB) and file type restrictions.

### Performance Tips

1. **Whisper Model Size**:
   - `tiny`: Fastest, least accurate
   - `base`: Good balance
   - `small`: Better accuracy (default)
   - `medium`: High accuracy, slower
   - `large`: Best accuracy, slowest

2. **Database Optimization**:
   - Indexes are automatically created for common queries
   - FTS5 provides fast full-text search
   - Consider SQLCipher for encrypted storage

3. **File Storage**:
   - Files are stored in `uploads/` directory
   - Consider using cloud storage for production
   - Implement file cleanup for old uploads

## Production Deployment

### Using Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Security Considerations

1. **File Upload Security**:
   - Validate file types and sizes
   - Scan for malware (consider adding ClamAV)
   - Store files outside web root

2. **Database Security**:
   - Use SQLCipher for encrypted storage
   - Implement proper backup strategies
   - Use parameterized queries (already implemented)

3. **API Security**:
   - Implement rate limiting
   - Add authentication for production use
   - Use HTTPS in production

## License

This project is part of the MemoriaVault application suite.
