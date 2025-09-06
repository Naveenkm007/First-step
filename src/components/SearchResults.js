import React, { useState } from 'react';
import './SearchResults.css';

function SearchResults({ onSearchResults, isSearching, setIsSearching }) {
  // State for search input and results
  const [searchQuery, setSearchQuery] = useState('');
  const [error, setError] = useState('');

  // Function to handle search input changes
  const handleInputChange = (event) => {
    setSearchQuery(event.target.value);
    setError('');
  };

  // Function to handle search form submission
  const handleSearch = async (event) => {
    event.preventDefault();
    
    // Validate search query
    if (!searchQuery.trim()) {
      setError('Please enter a search term');
      return;
    }

    // Clear previous error
    setError('');
    setIsSearching(true);

    try {
      // Make API call to search endpoint
      const response = await fetch(
        `http://localhost:8000/api/search?q=${encodeURIComponent(searchQuery.trim())}`
      );

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      if (result.status === 'ok') {
        onSearchResults(result.results);
      } else {
        throw new Error(result.message || 'Search failed');
      }

    } catch (error) {
      console.error('Search error:', error);
      setError(error.message || 'Failed to search memories. Please try again.');
      onSearchResults([]); // Clear results on error
    } finally {
      setIsSearching(false);
    }
  };

  // Function to handle clear search
  const handleClearSearch = () => {
    setSearchQuery('');
    setError('');
    onSearchResults([]);
  };

  return (
    <div className="search-results">
      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={searchQuery}
            onChange={handleInputChange}
            placeholder="Search your memories..."
            disabled={isSearching}
            className="search-input"
          />
          
          <button
            type="submit"
            disabled={isSearching || !searchQuery.trim()}
            className="search-button"
          >
            {isSearching ? '🔍' : '🔍'}
          </button>
          
          {searchQuery && (
            <button
              type="button"
              onClick={handleClearSearch}
              disabled={isSearching}
              className="clear-button"
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>

        {/* Loading indicator */}
        {isSearching && (
          <div className="search-loading">
            <div className="loading-spinner"></div>
            <span>Searching...</span>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="search-error">
            ❌ {error}
          </div>
        )}

        {/* Search tips */}
        <div className="search-tips">
          <p>💡 Search by title, content, person, or date</p>
        </div>
      </form>
    </div>
  );
}

export default SearchResults;
