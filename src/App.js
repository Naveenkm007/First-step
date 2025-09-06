import React, { useState } from 'react';
import UploadForm from './components/UploadForm';
import SearchResults from './components/SearchResults';
import MemoryCard from './components/MemoryCard';
import './App.css';

function App() {
  // State to manage uploaded memories and search results
  const [memories, setMemories] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);

  // Function to add a new memory after successful upload
  const handleMemoryUploaded = (newMemory) => {
    setMemories(prevMemories => [newMemory, ...prevMemories]);
  };

  // Function to handle search results
  const handleSearchResults = (results) => {
    setSearchResults(results);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>📚 MemoriaVault</h1>
        <p>Your personal memory digitizer</p>
      </header>

      <main className="app-main">
        {/* Upload Section */}
        <section className="upload-section">
          <h2>Upload Memory</h2>
          <UploadForm onMemoryUploaded={handleMemoryUploaded} />
        </section>

        {/* Search Section */}
        <section className="search-section">
          <h2>Search Memories</h2>
          <SearchResults 
            onSearchResults={handleSearchResults}
            isSearching={isSearching}
            setIsSearching={setIsSearching}
          />
        </section>

        {/* Display Section */}
        <section className="display-section">
          {searchResults.length > 0 ? (
            <>
              <h2>Search Results</h2>
              <div className="memory-grid">
                {searchResults.map(memory => (
                  <MemoryCard key={memory.id} memory={memory} />
                ))}
              </div>
            </>
          ) : (
            <>
              <h2>Recent Memories</h2>
              <div className="memory-grid">
                {memories.map(memory => (
                  <MemoryCard key={memory.id} memory={memory} />
                ))}
              </div>
              {memories.length === 0 && (
                <p className="empty-state">No memories uploaded yet. Upload your first memory above!</p>
              )}
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
