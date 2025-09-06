"""
ASR (Automatic Speech Recognition) utilities for MemoriaVault.
Handles audio transcription using OpenAI Whisper.
"""

import whisper
import os
import asyncio
from typing import Optional
import tempfile
import shutil

# Global variable to store the loaded Whisper model
_whisper_model = None

def load_whisper_model(model_size: str = "small") -> whisper.Whisper:
    """
    Load the Whisper model for speech recognition.
    
    Whisper is an open-source speech recognition system that can:
    - Transcribe speech in multiple languages
    - Handle various audio formats
    - Work offline (no internet required)
    
    Model sizes available:
    - tiny: Fastest, least accurate
    - base: Good balance of speed and accuracy
    - small: Better accuracy, slower
    - medium: High accuracy, slower
    - large: Best accuracy, slowest
    
    Args:
        model_size: Size of the Whisper model to load
        
    Returns:
        Loaded Whisper model
    """
    global _whisper_model
    
    if _whisper_model is None:
        try:
            print(f"🔄 Loading Whisper model '{model_size}'...")
            _whisper_model = whisper.load_model(model_size)
            print(f"✅ Whisper model '{model_size}' loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {str(e)}")
            print("💡 Make sure you have enough disk space and internet connection for first-time download")
            raise
    
    return _whisper_model

async def transcribe_audio(audio_path: str, model_size: str = "small") -> str:
    """
    Transcribe audio file to text using Whisper.
    
    This function:
    1. Loads the Whisper model (if not already loaded)
    2. Processes the audio file
    3. Extracts spoken text
    4. Returns the transcribed text
    
    Args:
        audio_path: Path to the audio file
        model_size: Size of Whisper model to use
        
    Returns:
        Transcribed text as a string
    """
    try:
        print(f"🎵 Transcribing audio: {audio_path}")
        
        # Check if audio file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load the Whisper model
        model = load_whisper_model(model_size)
        
        # Run transcription in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: model.transcribe(audio_path)
        )
        
        # Extract the transcribed text
        transcribed_text = result["text"].strip()
        
        print(f"✅ Transcribed {len(transcribed_text)} characters of text")
        return transcribed_text
        
    except Exception as e:
        print(f"❌ Audio transcription failed: {str(e)}")
        return f"Transcription failed: {str(e)}"

def get_audio_info(audio_path: str) -> dict:
    """
    Get basic information about an audio file.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Dictionary containing audio file information
    """
    try:
        file_size = os.path.getsize(audio_path)
        file_extension = os.path.splitext(audio_path)[1].lower()
        
        return {
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'file_extension': file_extension,
            'file_name': os.path.basename(audio_path)
        }
    except Exception as e:
        print(f"❌ Failed to get audio info: {str(e)}")
        return {}

def validate_audio_file(audio_path: str) -> bool:
    """
    Validate that the audio file can be processed.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        True if file is valid, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.exists(audio_path):
            return False
        
        # Check file size (max 25MB for Whisper)
        file_size = os.path.getsize(audio_path)
        max_size = 25 * 1024 * 1024  # 25MB
        
        if file_size > max_size:
            print(f"⚠️ Audio file too large: {file_size / (1024*1024):.1f}MB (max 25MB)")
            return False
        
        # Check file extension
        valid_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg']
        file_extension = os.path.splitext(audio_path)[1].lower()
        
        if file_extension not in valid_extensions:
            print(f"⚠️ Unsupported audio format: {file_extension}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Audio validation failed: {str(e)}")
        return False

def preprocess_audio(audio_path: str) -> str:
    """
    Preprocess audio file if needed (convert format, normalize, etc.).
    
    For now, this is a placeholder. In a production system, you might:
    - Convert audio to a standard format (WAV)
    - Normalize audio levels
    - Remove background noise
    - Split long audio files
    
    Args:
        audio_path: Path to the input audio file
        
    Returns:
        Path to the processed audio file (same as input for now)
    """
    # For now, just return the original path
    # In the future, you could add audio preprocessing here
    return audio_path

# Test function for development
if __name__ == "__main__":
    # Test with a sample audio file
    test_audio = "test_audio.mp3"
    if os.path.exists(test_audio):
        print("Testing audio transcription...")
        import asyncio
        
        async def test_transcription():
            text = await transcribe_audio(test_audio)
            print(f"Transcribed text: {text}")
        
        asyncio.run(test_transcription())
    else:
        print("No test audio found. Place a test audio file as 'test_audio.mp3' to test ASR.")
        print("Supported formats: MP3, WAV, M4A, FLAC, OGG")
