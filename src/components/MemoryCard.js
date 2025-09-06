import React from 'react';
import './MemoryCard.css';

function MemoryCard({ memory }) {
  // Function to format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'No date';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  // Function to get sentiment emoji and color
  const getSentimentDisplay = (sentiment) => {
    if (sentiment === null || sentiment === undefined) {
      return { emoji: '😐', text: 'Neutral', color: '#666' };
    }
    
    if (sentiment > 0.3) {
      return { emoji: '😊', text: 'Positive', color: '#4CAF50' };
    } else if (sentiment < -0.3) {
      return { emoji: '😔', text: 'Negative', color: '#F44336' };
    } else {
      return { emoji: '😐', text: 'Neutral', color: '#666' };
    }
  };

  // Function to truncate text for display
  const truncateText = (text, maxLength = 150) => {
    if (!text) return 'No text extracted';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  // Function to get media icon based on type
  const getMediaIcon = (mediaType) => {
    switch (mediaType) {
      case 'image':
        return '🖼️';
      case 'audio':
        return '🎵';
      default:
        return '📄';
    }
  };

  // Function to handle view button click
  const handleView = () => {
    // In a real app, this would open a detailed view or modal
    alert(`Viewing memory: ${memory.title}\n\nFull text: ${memory.text || 'No text available'}`);
  };

  const sentimentDisplay = getSentimentDisplay(memory.sentiment);

  return (
    <div className="memory-card">
      {/* Header with thumbnail and basic info */}
      <div className="card-header">
        <div className="thumbnail">
          {memory.media_type === 'image' ? (
            <img 
              src={`http://localhost:8000${memory.media_path}`} 
              alt={memory.title}
              className="thumbnail-image"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
          ) : null}
          <div 
            className="thumbnail-icon"
            style={{ display: memory.media_type === 'image' ? 'none' : 'block' }}
          >
            {getMediaIcon(memory.media_type)}
          </div>
        </div>
        
        <div className="card-info">
          <h3 className="card-title">{memory.title}</h3>
          <div className="card-meta">
            <span className="date">📅 {formatDate(memory.date)}</span>
            {memory.location && (
              <span className="location">📍 {memory.location}</span>
            )}
          </div>
        </div>
      </div>

      {/* Extracted text content */}
      <div className="card-content">
        <p className="extracted-text">
          {truncateText(memory.text)}
        </p>
      </div>

      {/* Sentiment and action */}
      <div className="card-footer">
        <div className="sentiment">
          <span 
            className="sentiment-emoji"
            style={{ color: sentimentDisplay.color }}
            title={`Sentiment: ${sentimentDisplay.text} (${memory.sentiment})`}
          >
            {sentimentDisplay.emoji}
          </span>
          <span className="sentiment-text">{sentimentDisplay.text}</span>
        </div>
        
        <button 
          className="view-button"
          onClick={handleView}
          title="View full memory"
        >
          👁️ View
        </button>
      </div>
    </div>
  );
}

export default MemoryCard;
