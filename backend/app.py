"""
MemoriaVault FastAPI Backend
A personal memory digitizer that processes images and audio files.
"""

import os
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from db import get_db_connection, init_database, create_memory, get_memory_by_id, search_memories
from ocr_utils import extract_text_from_image, extract_exif_data
from asr_utils import transcribe_audio
from sentiment_utils import analyze_sentiment

# Create FastAPI app instance
app = FastAPI(
    title="MemoriaVault API",
    description="Personal memory digitizer with OCR and ASR capabilities",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files to serve uploaded media
app.mount("/media", StaticFiles(directory="uploads"), name="media")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables when the app starts."""
    init_database()
    print("✅ Database initialized successfully")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "MemoriaVault API is running!", "status": "ok"}

@app.post("/api/upload")
async def upload_memory(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    person: Optional[str] = Form(None)
):
    """
    Upload and process a memory file (image or audio).
    
    This endpoint:
    1. Validates the uploaded file
    2. Saves it to the uploads directory
    3. Processes the file (OCR for images, ASR for audio)
    4. Extracts metadata (EXIF for images)
    5. Analyzes sentiment of extracted text
    6. Stores everything in the database
    """
    try:
        # Validate file type
        if not file.content_type:
            raise HTTPException(status_code=400, detail="File type not detected")
        
        # Check if it's an image or audio file
        is_image = file.content_type.startswith('image/')
        is_audio = file.content_type.startswith('audio/')
        
        if not (is_image or is_audio):
            raise HTTPException(
                status_code=400, 
                detail="Only image (JPEG, PNG) and audio (MP3, WAV) files are supported"
            )
        
        # Generate safe filename
        file_extension = Path(file.filename).suffix.lower()
        safe_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"📁 File saved: {file_path}")
        
        # Process the file based on type
        extracted_text = ""
        extracted_date = None
        extracted_location = None
        
        if is_image:
            print("🖼️ Processing image with OCR...")
            # Extract text using OCR (Optical Character Recognition)
            extracted_text = extract_text_from_image(str(file_path))
            
            # Extract EXIF metadata (date, location from camera)
            exif_data = extract_exif_data(str(file_path))
            extracted_date = exif_data.get('date')
            extracted_location = exif_data.get('location')
            
        elif is_audio:
            print("🎵 Processing audio with ASR...")
            # Extract text using ASR (Automatic Speech Recognition)
            extracted_text = await transcribe_audio(str(file_path))
        
        # Analyze sentiment of extracted text
        print("😊 Analyzing sentiment...")
        sentiment_score = analyze_sentiment(extracted_text) if extracted_text else 0.0
        
        # Store in database
        print("💾 Storing in database...")
        memory_id = create_memory(
            title=title,
            text=extracted_text,
            date=extracted_date,
            location=extracted_location,
            sentiment=sentiment_score,
            media_path=f"/media/uploads/{safe_filename}",
            media_type="image" if is_image else "audio",
            person=person
        )
        
        # Return success response
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "memory": {
                    "id": memory_id,
                    "title": title,
                    "text": extracted_text,
                    "date": extracted_date,
                    "location": extracted_location,
                    "sentiment": sentiment_score,
                    "media_path": f"/media/uploads/{safe_filename}",
                    "media_type": "image" if is_image else "audio"
                }
            }
        )
        
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        # Clean up file if it was saved but processing failed
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/memory/{memory_id}")
async def get_memory(memory_id: int):
    """
    Get a specific memory by ID.
    
    Returns the memory details including the media URL.
    """
    try:
        memory = get_memory_by_id(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "memory": memory
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Get memory error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve memory: {str(e)}")

@app.get("/api/search")
async def search_memory(q: str):
    """
    Search memories using full-text search.
    
    Uses SQLite FTS5 (Full-Text Search) to find memories containing the search term.
    Returns snippets of matching text with context.
    """
    try:
        if not q.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        results = search_memories(q.strip())
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "results": results
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/memories")
async def list_memories(limit: int = 20, offset: int = 0):
    """
    List all memories with pagination.
    
    Returns a list of memories ordered by creation date (newest first).
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, text, date, location, sentiment, media_path, media_type, created_at
            FROM memories 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        memories = []
        for row in cursor.fetchall():
            memories.append({
                "id": row[0],
                "title": row[1],
                "text": row[2],
                "date": row[3],
                "location": row[4],
                "sentiment": row[5],
                "media_path": row[6],
                "media_type": row[7],
                "created_at": row[8]
            })
        
        conn.close()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "memories": memories,
                "count": len(memories)
            }
        )
        
    except Exception as e:
        print(f"❌ List memories error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list memories: {str(e)}")

if __name__ == "__main__":
    # Run the FastAPI server
    print("🚀 Starting MemoriaVault API server...")
    print("📖 API docs available at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
