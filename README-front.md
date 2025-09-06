# MemoriaVault Frontend

A modern React single-page application for MemoriaVault - your personal memory digitizer. Upload images and audio files, extract text, and search through your memories with ease.

## Features

- 📁 **File Upload**: Upload images (JPEG, PNG) or audio files (MP3, WAV) with titles and person tags
- 🔍 **Smart Search**: Search through your memories by title, content, person, or date
- 📊 **Sentiment Analysis**: View sentiment scores for your memories
- 📱 **Mobile-Friendly**: Responsive design that works on all devices
- ⚡ **Real-time Progress**: Upload progress indicators and loading states
- 🎨 **Modern UI**: Clean, intuitive interface with smooth animations

## Quick Start

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. **Create a new React app** (if starting from scratch):
   ```bash
   npx create-react-app memoriavault-frontend
   cd memoriavault-frontend
   ```

2. **Replace the default files** with the provided components:
   - Copy all files from the `src/` directory
   - Replace `src/App.js`, `src/index.js`, and add the component files

3. **Install dependencies** (if needed):
   ```bash
   npm install
   ```

4. **Start the development server**:
   ```bash
   npm start
   ```

5. **Open your browser** and navigate to `http://localhost:3000`

## Project Structure

```
src/
├── App.js                 # Main application component
├── App.css               # Main app styles
├── index.js              # Application entry point
├── index.css             # Global styles
└── components/
    ├── UploadForm.js     # File upload component
    ├── UploadForm.css    # Upload form styles
    ├── MemoryCard.js     # Memory display component
    ├── MemoryCard.css    # Memory card styles
    ├── SearchResults.js  # Search functionality
    └── SearchResults.css # Search component styles
```

## API Integration

### Backend Endpoints

The frontend communicates with the backend at `http://localhost:8000`:

#### Upload Endpoint
- **URL**: `POST /api/upload`
- **Content-Type**: `multipart/form-data`
- **Fields**: `file`, `title`, `person` (optional)

**Example Request**:
```javascript
const formData = new FormData();
formData.append('file', selectedFile);
formData.append('title', 'Grandma Letter');
formData.append('person', 'Grandma');
```

**Expected Response**:
```json
{
  "status": "ok",
  "memory": {
    "id": 123,
    "title": "Grandma Letter",
    "text": "Dear... (extracted text)",
    "date": "1954-06-12",
    "location": "Bengaluru",
    "sentiment": 0.12,
    "media_path": "/media/uploads/letter1.jpg",
    "media_type": "image"
  }
}
```

#### Search Endpoint
- **URL**: `GET /api/search?q=search_term`
- **Method**: GET

**Example Request**:
```javascript
fetch('http://localhost:8000/api/search?q=grandma')
```

**Expected Response**:
```json
{
  "status": "ok",
  "results": [
    {
      "id": 123,
      "title": "Grandma Letter",
      "snippet": "Dear... (text snippet)",
      "date": "1954-06-12"
    }
  ]
}
```

## CORS Configuration

**Important**: The backend must be configured to allow CORS requests from the frontend.

### Backend CORS Setup (FastAPI example):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## File Validation

The frontend includes client-side validation:

- **Allowed file types**: JPEG, JPG, PNG, MP3, WAV
- **Maximum file size**: 20MB
- **Required fields**: File and title
- **Optional fields**: Person tag

## Component Architecture

### App.js
- Main application component that manages global state
- Handles memory uploads and search results
- Renders the three main sections: upload, search, and display

### UploadForm.js
- Handles file selection and form submission
- Includes client-side validation and progress tracking
- Manages upload state and error handling

### MemoryCard.js
- Displays individual memory items
- Shows thumbnails, extracted text, metadata, and sentiment
- Handles view functionality

### SearchResults.js
- Manages search input and API calls
- Displays search results and loading states
- Includes search tips and error handling

## Styling

- **CSS Modules**: Each component has its own CSS file
- **Responsive Design**: Mobile-first approach with breakpoints
- **Modern UI**: Clean design with gradients, shadows, and smooth transitions
- **Accessibility**: Proper contrast ratios and keyboard navigation

## Development Notes

- Uses functional components with React hooks
- No external UI libraries (pure CSS)
- Fetch API for HTTP requests
- Error boundaries and loading states
- Form validation and user feedback

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend CORS is configured for `http://localhost:3000`
2. **File Upload Fails**: Check file size (max 20MB) and type restrictions
3. **Search Not Working**: Verify backend search endpoint is running
4. **Images Not Loading**: Check media path configuration in backend

### Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Production Build

To create a production build:

```bash
npm run build
```

This creates an optimized build in the `build/` folder that can be served by any static file server.

## License

This project is part of the MemoriaVault application suite.
