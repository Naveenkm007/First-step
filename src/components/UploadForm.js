import React, { useState } from 'react';
import './UploadForm.css';

function UploadForm({ onMemoryUploaded }) {
  // State for form data and UI feedback
  const [formData, setFormData] = useState({
    file: null,
    title: '',
    person: ''
  });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Allowed file types and size limit
  const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'audio/mp3', 'audio/wav'];
  const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20MB in bytes

  // Function to validate file before upload
  const validateFile = (file) => {
    if (!file) {
      return 'Please select a file';
    }

    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'Please select a valid file type (JPEG, PNG, MP3, or WAV)';
    }

    if (file.size > MAX_FILE_SIZE) {
      return 'File size must be less than 20MB';
    }

    return null;
  };

  // Function to handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    const validationError = validateFile(file);
    
    if (validationError) {
      setError(validationError);
      setFormData(prev => ({ ...prev, file: null }));
    } else {
      setError('');
      setFormData(prev => ({ ...prev, file }));
    }
  };

  // Function to handle form input changes
  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Function to handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();
    
    // Validate form
    if (!formData.file) {
      setError('Please select a file');
      return;
    }

    if (!formData.title.trim()) {
      setError('Please enter a title');
      return;
    }

    // Clear previous messages
    setError('');
    setSuccess('');

    // Create form data for upload
    const uploadData = new FormData();
    uploadData.append('file', formData.file);
    uploadData.append('title', formData.title.trim());
    if (formData.person.trim()) {
      uploadData.append('person', formData.person.trim());
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 200);

      // Make API call to backend
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: uploadData
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      if (result.status === 'ok') {
        setSuccess('Memory uploaded successfully!');
        onMemoryUploaded(result.memory);
        
        // Reset form
        setFormData({ file: null, title: '', person: '' });
        document.getElementById('file-input').value = '';
      } else {
        throw new Error(result.message || 'Upload failed');
      }

    } catch (error) {
      console.error('Upload error:', error);
      setError(error.message || 'Failed to upload memory. Please try again.');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="upload-form">
      <form onSubmit={handleSubmit} className="form">
        {/* File Input */}
        <div className="form-group">
          <label htmlFor="file-input" className="file-label">
            📁 Choose File
          </label>
          <input
            id="file-input"
            type="file"
            accept=".jpg,.jpeg,.png,.mp3,.wav"
            onChange={handleFileChange}
            disabled={isUploading}
            className="file-input"
          />
          {formData.file && (
            <p className="file-info">
              Selected: {formData.file.name} ({(formData.file.size / 1024 / 1024).toFixed(2)} MB)
            </p>
          )}
        </div>

        {/* Title Input */}
        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            id="title"
            type="text"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            placeholder="Enter memory title..."
            disabled={isUploading}
            required
            className="text-input"
          />
        </div>

        {/* Person Input */}
        <div className="form-group">
          <label htmlFor="person">Person (optional)</label>
          <input
            id="person"
            type="text"
            name="person"
            value={formData.person}
            onChange={handleInputChange}
            placeholder="Who is this memory about?"
            disabled={isUploading}
            className="text-input"
          />
        </div>

        {/* Upload Progress */}
        {isUploading && (
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="progress-text">Uploading... {uploadProgress}%</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="message error">
            ❌ {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="message success">
            ✅ {success}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isUploading || !formData.file || !formData.title.trim()}
          className="submit-button"
        >
          {isUploading ? 'Uploading...' : 'Upload Memory'}
        </button>
      </form>
    </div>
  );
}

export default UploadForm;
