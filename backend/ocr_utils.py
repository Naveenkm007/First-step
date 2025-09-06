"""
OCR (Optical Character Recognition) utilities for MemoriaVault.
Handles image preprocessing and text extraction using Tesseract.
"""

import cv2
import pytesseract
import exifread
from PIL import Image
import numpy as np
from typing import Dict, Optional
import os

def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocess an image to improve OCR accuracy.
    
    This function:
    1. Converts the image to grayscale (removes color information)
    2. Applies noise reduction to clean up the image
    3. Enhances contrast to make text more readable
    4. Applies thresholding to create a black and white image
    
    Args:
        image_path: Path to the input image file
        
    Returns:
        Preprocessed image as a numpy array
    """
    try:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")
        
        # Convert to grayscale (removes color, keeps only brightness)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise (smooths out small imperfections)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding (converts to black and white)
        # This helps separate text from background
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Apply morphological operations to clean up the image
        # This removes small noise and connects broken text
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
        
    except Exception as e:
        print(f"❌ Image preprocessing failed: {str(e)}")
        # Return original image if preprocessing fails
        return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using OCR (Optical Character Recognition).
    
    This function:
    1. Preprocesses the image to improve text recognition
    2. Uses Tesseract OCR engine to extract text
    3. Cleans up the extracted text
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text as a string
    """
    try:
        print(f"🔍 Extracting text from: {image_path}")
        
        # Check if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            print("⚠️ Tesseract not found. Please install Tesseract OCR.")
            print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            print("   macOS: brew install tesseract")
            print("   Ubuntu: sudo apt-get install tesseract-ocr")
            return "OCR not available - Tesseract not installed"
        
        # Preprocess the image
        processed_image = preprocess_image(image_path)
        
        # Configure Tesseract for better accuracy
        # PSM 6: Assume a single uniform block of text
        # OEM 3: Default OCR Engine Mode
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?;:()[]{}"\' '
        
        # Extract text using Tesseract
        extracted_text = pytesseract.image_to_string(
            processed_image, 
            config=custom_config,
            lang='eng'  # English language
        )
        
        # Clean up the extracted text
        cleaned_text = clean_extracted_text(extracted_text)
        
        print(f"✅ Extracted {len(cleaned_text)} characters of text")
        return cleaned_text
        
    except Exception as e:
        print(f"❌ OCR extraction failed: {str(e)}")
        return f"Text extraction failed: {str(e)}"

def clean_extracted_text(text: str) -> str:
    """
    Clean up extracted text by removing extra whitespace and formatting.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]  # Remove empty lines
    
    # Join lines with single spaces
    cleaned = ' '.join(lines)
    
    # Remove multiple consecutive spaces
    while '  ' in cleaned:
        cleaned = cleaned.replace('  ', ' ')
    
    return cleaned.strip()

def extract_exif_data(image_path: str) -> Dict[str, Optional[str]]:
    """
    Extract EXIF metadata from an image file.
    
    EXIF (Exchangeable Image File Format) contains metadata like:
    - Date and time the photo was taken
    - Camera settings (ISO, aperture, shutter speed)
    - GPS location (if available)
    - Camera make and model
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary containing extracted metadata
    """
    try:
        print(f"📸 Extracting EXIF data from: {image_path}")
        
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
        
        exif_data = {
            'date': None,
            'location': None,
            'camera_make': None,
            'camera_model': None
        }
        
        # Extract date information
        if 'EXIF DateTimeOriginal' in tags:
            date_str = str(tags['EXIF DateTimeOriginal'])
            # Convert from "YYYY:MM:DD HH:MM:SS" to "YYYY-MM-DD"
            try:
                date_part = date_str.split(' ')[0]
                exif_data['date'] = date_part.replace(':', '-')
            except:
                exif_data['date'] = date_str
        elif 'Image DateTime' in tags:
            date_str = str(tags['Image DateTime'])
            try:
                date_part = date_str.split(' ')[0]
                exif_data['date'] = date_part.replace(':', '-')
            except:
                exif_data['date'] = date_str
        
        # Extract camera information
        if 'Image Make' in tags:
            exif_data['camera_make'] = str(tags['Image Make'])
        if 'Image Model' in tags:
            exif_data['camera_model'] = str(tags['Image Model'])
        
        # Extract GPS location (simplified)
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            try:
                lat = str(tags['GPS GPSLatitude'])
                lon = str(tags['GPS GPSLongitude'])
                exif_data['location'] = f"GPS: {lat}, {lon}"
            except:
                pass
        
        print(f"✅ Extracted EXIF data: {exif_data}")
        return exif_data
        
    except Exception as e:
        print(f"❌ EXIF extraction failed: {str(e)}")
        return {
            'date': None,
            'location': None,
            'camera_make': None,
            'camera_model': None
        }

def get_image_info(image_path: str) -> Dict[str, any]:
    """
    Get basic information about an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary containing image information
    """
    try:
        with Image.open(image_path) as img:
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_bytes': os.path.getsize(image_path)
            }
    except Exception as e:
        print(f"❌ Failed to get image info: {str(e)}")
        return {}

# Test function for development
if __name__ == "__main__":
    # Test with a sample image
    test_image = "test_image.jpg"
    if os.path.exists(test_image):
        print("Testing OCR extraction...")
        text = extract_text_from_image(test_image)
        print(f"Extracted text: {text}")
        
        print("\nTesting EXIF extraction...")
        exif = extract_exif_data(test_image)
        print(f"EXIF data: {exif}")
    else:
        print("No test image found. Place a test image as 'test_image.jpg' to test OCR.")
