"""
Unit tests for the upload endpoint using pytest and httpx.
Tests file upload functionality with mock data.
"""

import pytest
import httpx
import os
import tempfile
from pathlib import Path
from PIL import Image
import io

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_IMAGE_SIZE = (100, 100)
TEST_TEXT = "This is a test image for OCR testing."

@pytest.fixture
def test_image():
    """
    Create a test image with text for OCR testing.
    
    This fixture creates a simple image with text that can be used
    to test the OCR functionality of the upload endpoint.
    """
    # Create a simple test image
    img = Image.new('RGB', TEST_IMAGE_SIZE, color='white')
    
    # Add some text to the image (this won't be OCR-readable, but it's for testing)
    # In a real test, you'd use a proper image with readable text
    return img

@pytest.fixture
def test_image_file(test_image):
    """
    Create a temporary image file for testing.
    
    Returns:
        Path to temporary image file
    """
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
        test_image.save(tmp_file.name, 'JPEG')
        yield tmp_file.name
    
    # Clean up
    if os.path.exists(tmp_file.name):
        os.unlink(tmp_file.name)

@pytest.fixture
def test_audio_file():
    """
    Create a temporary audio file for testing.
    
    Returns:
        Path to temporary audio file
    """
    # Create a minimal WAV file header (44 bytes)
    wav_header = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
    wav_data = b'\x00' * 2048  # Silent audio data
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
        tmp_file.write(wav_header + wav_data)
        tmp_file.flush()
        yield tmp_file.name
    
    # Clean up
    if os.path.exists(tmp_file.name):
        os.unlink(tmp_file.name)

@pytest.mark.asyncio
async def test_upload_image_success(test_image_file):
    """
    Test successful image upload with OCR processing.
    
    This test:
    1. Uploads a test image
    2. Verifies the response format
    3. Checks that the memory was created
    """
    async with httpx.AsyncClient() as client:
        # Prepare the upload data
        with open(test_image_file, 'rb') as f:
            files = {'file': ('test_image.jpg', f, 'image/jpeg')}
            data = {
                'title': 'Test Image Memory',
                'person': 'Test Person'
            }
            
            # Make the upload request
            response = await client.post(
                f"{BASE_URL}/api/upload",
                files=files,
                data=data
            )
    
    # Verify response
    assert response.status_code == 200
    
    response_data = response.json()
    assert response_data['status'] == 'ok'
    assert 'memory' in response_data
    
    memory = response_data['memory']
    assert memory['title'] == 'Test Image Memory'
    assert memory['person'] == 'Test Person'
    assert memory['media_type'] == 'image'
    assert 'media_path' in memory
    assert 'id' in memory
    assert 'sentiment' in memory
    assert 'text' in memory

@pytest.mark.asyncio
async def test_upload_audio_success(test_audio_file):
    """
    Test successful audio upload with ASR processing.
    
    This test:
    1. Uploads a test audio file
    2. Verifies the response format
    3. Checks that the memory was created
    """
    async with httpx.AsyncClient() as client:
        # Prepare the upload data
        with open(test_audio_file, 'rb') as f:
            files = {'file': ('test_audio.wav', f, 'audio/wav')}
            data = {
                'title': 'Test Audio Memory',
                'person': 'Test Person'
            }
            
            # Make the upload request
            response = await client.post(
                f"{BASE_URL}/api/upload",
                files=files,
                data=data
            )
    
    # Verify response
    assert response.status_code == 200
    
    response_data = response.json()
    assert response_data['status'] == 'ok'
    assert 'memory' in response_data
    
    memory = response_data['memory']
    assert memory['title'] == 'Test Audio Memory'
    assert memory['person'] == 'Test Person'
    assert memory['media_type'] == 'audio'
    assert 'media_path' in memory
    assert 'id' in memory
    assert 'sentiment' in memory
    assert 'text' in memory

@pytest.mark.asyncio
async def test_upload_missing_title():
    """
    Test upload with missing title (should fail).
    """
    async with httpx.AsyncClient() as client:
        # Create a minimal test file
        test_data = b'test file content'
        
        files = {'file': ('test.txt', io.BytesIO(test_data), 'text/plain')}
        data = {
            'person': 'Test Person'
            # Missing 'title' field
        }
        
        response = await client.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
    
    # Should return 422 (Unprocessable Entity) for missing required field
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_upload_invalid_file_type():
    """
    Test upload with invalid file type (should fail).
    """
    async with httpx.AsyncClient() as client:
        # Create a text file (not supported)
        test_data = b'This is a text file, not an image or audio file.'
        
        files = {'file': ('test.txt', io.BytesIO(test_data), 'text/plain')}
        data = {
            'title': 'Test Memory',
            'person': 'Test Person'
        }
        
        response = await client.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
    
    # Should return 400 (Bad Request) for invalid file type
    assert response.status_code == 400
    
    response_data = response.json()
    assert 'detail' in response_data
    assert 'not supported' in response_data['detail'].lower()

@pytest.mark.asyncio
async def test_upload_large_file():
    """
    Test upload with file that's too large (should fail).
    
    Note: This test creates a large file in memory, so it might be slow.
    """
    async with httpx.AsyncClient() as client:
        # Create a large file (25MB + 1 byte)
        large_data = b'0' * (25 * 1024 * 1024 + 1)
        
        files = {'file': ('large_file.jpg', io.BytesIO(large_data), 'image/jpeg')}
        data = {
            'title': 'Large File Test',
            'person': 'Test Person'
        }
        
        response = await client.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
    
    # Should return 400 (Bad Request) for file too large
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_upload_without_person(test_image_file):
    """
    Test upload without person field (should succeed).
    
    The person field is optional, so this should work fine.
    """
    async with httpx.AsyncClient() as client:
        with open(test_image_file, 'rb') as f:
            files = {'file': ('test_image.jpg', f, 'image/jpeg')}
            data = {
                'title': 'Test Memory Without Person'
                # No 'person' field
            }
            
            response = await client.post(
                f"{BASE_URL}/api/upload",
                files=files,
                data=data
            )
    
    # Should succeed
    assert response.status_code == 200
    
    response_data = response.json()
    assert response_data['status'] == 'ok'
    
    memory = response_data['memory']
    assert memory['title'] == 'Test Memory Without Person'
    assert memory['person'] is None or memory['person'] == ''

@pytest.mark.asyncio
async def test_health_check():
    """
    Test the health check endpoint.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/")
    
    assert response.status_code == 200
    
    response_data = response.json()
    assert response_data['status'] == 'ok'
    assert 'MemoriaVault API is running' in response_data['message']

@pytest.mark.asyncio
async def test_search_endpoint():
    """
    Test the search endpoint.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/search?q=test")
    
    assert response.status_code == 200
    
    response_data = response.json()
    assert response_data['status'] == 'ok'
    assert 'results' in response_data
    assert isinstance(response_data['results'], list)

@pytest.mark.asyncio
async def test_search_empty_query():
    """
    Test search with empty query (should fail).
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/search?q=")
    
    # Should return 400 (Bad Request) for empty query
    assert response.status_code == 400

# Integration test that combines upload and search
@pytest.mark.asyncio
async def test_upload_and_search_integration(test_image_file):
    """
    Test the complete workflow: upload a memory and then search for it.
    
    This test:
    1. Uploads a memory
    2. Searches for it
    3. Verifies the search finds the uploaded memory
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Upload a memory
        with open(test_image_file, 'rb') as f:
            files = {'file': ('integration_test.jpg', f, 'image/jpeg')}
            data = {
                'title': 'Integration Test Memory',
                'person': 'Integration Test Person'
            }
            
            upload_response = await client.post(
                f"{BASE_URL}/api/upload",
                files=files,
                data=data
            )
        
        assert upload_response.status_code == 200
        upload_data = upload_response.json()
        memory_id = upload_data['memory']['id']
        
        # Step 2: Search for the uploaded memory
        search_response = await client.get(
            f"{BASE_URL}/api/search?q=integration"
        )
        
        assert search_response.status_code == 200
        search_data = search_response.json()
        
        # Step 3: Verify the search found our memory
        assert len(search_data['results']) > 0
        
        # Find our memory in the search results
        found_memory = None
        for result in search_data['results']:
            if result['id'] == memory_id:
                found_memory = result
                break
        
        assert found_memory is not None
        assert found_memory['title'] == 'Integration Test Memory'

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
