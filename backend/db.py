"""
Database utilities for MemoriaVault.
Handles SQLite database operations and FTS5 full-text search.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json

DATABASE_PATH = "memoriavault.db"

def get_db_connection() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.
    
    Returns:
        SQLite database connection
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def init_database():
    """
    Initialize the database with required tables.
    
    This function creates:
    1. memories table: Stores memory metadata and extracted text
    2. media_files table: Stores information about uploaded files
    3. memories_fts table: FTS5 virtual table for full-text search
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                text TEXT,
                date TEXT,
                location TEXT,
                sentiment REAL DEFAULT 0.0,
                media_path TEXT NOT NULL,
                media_type TEXT NOT NULL CHECK (media_type IN ('image', 'audio')),
                person TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create media_files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size INTEGER,
                mime_type TEXT,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_id) REFERENCES memories (id) ON DELETE CASCADE
            )
        """)
        
        # Create FTS5 virtual table for full-text search
        # FTS5 is a full-text search extension for SQLite
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                title,
                text,
                person,
                content='memories',
                content_rowid='id'
            )
        """)
        
        # Create triggers to keep FTS5 table in sync with memories table
        # These triggers automatically update the search index when memories are added/updated/deleted
        
        # Trigger for INSERT
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_insert AFTER INSERT ON memories BEGIN
                INSERT INTO memories_fts(rowid, title, text, person) 
                VALUES (new.id, new.title, new.text, new.person);
            END
        """)
        
        # Trigger for UPDATE
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_update AFTER UPDATE ON memories BEGIN
                UPDATE memories_fts SET 
                    title = new.title,
                    text = new.text,
                    person = new.person
                WHERE rowid = new.id;
            END
        """)
        
        # Trigger for DELETE
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS memories_fts_delete AFTER DELETE ON memories BEGIN
                DELETE FROM memories_fts WHERE rowid = old.id;
            END
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_media_type ON memories(media_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_sentiment ON memories(sentiment)")
        
        conn.commit()
        conn.close()
        
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        raise

def create_memory(
    title: str,
    text: str = None,
    date: str = None,
    location: str = None,
    sentiment: float = 0.0,
    media_path: str = None,
    media_type: str = None,
    person: str = None
) -> int:
    """
    Create a new memory record in the database.
    
    Args:
        title: Title of the memory
        text: Extracted text content
        date: Date associated with the memory
        location: Location information
        sentiment: Sentiment score (-1.0 to 1.0)
        media_path: Path to the media file
        media_type: Type of media ('image' or 'audio')
        person: Person associated with the memory
        
    Returns:
        ID of the created memory
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memories (
                title, text, date, location, sentiment, 
                media_path, media_type, person
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, text, date, location, sentiment, media_path, media_type, person))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Memory created with ID: {memory_id}")
        return memory_id
        
    except Exception as e:
        print(f"❌ Failed to create memory: {str(e)}")
        raise

def get_memory_by_id(memory_id: int) -> Optional[Dict]:
    """
    Get a memory by its ID.
    
    Args:
        memory_id: ID of the memory to retrieve
        
    Returns:
        Memory data as a dictionary, or None if not found
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM memories WHERE id = ?
        """, (memory_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
        
    except Exception as e:
        print(f"❌ Failed to get memory: {str(e)}")
        raise

def search_memories(query: str, limit: int = 20) -> List[Dict]:
    """
    Search memories using full-text search.
    
    This function uses SQLite FTS5 to search through:
    - Memory titles
    - Extracted text content
    - Person names
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List of matching memories with snippets
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Use FTS5 to search and get snippets
        # snippet() function returns highlighted text with search terms
        cursor.execute("""
            SELECT 
                m.id,
                m.title,
                m.date,
                m.sentiment,
                m.media_type,
                m.media_path,
                snippet(memories_fts, 1, '<mark>', '</mark>', '...', 32) as title_snippet,
                snippet(memories_fts, 2, '<mark>', '</mark>', '...', 64) as text_snippet
            FROM memories_fts
            JOIN memories m ON memories_fts.rowid = m.id
            WHERE memories_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        
        results = []
        for row in cursor.fetchall():
            # Combine snippets for display
            snippet_parts = []
            if row['title_snippet']:
                snippet_parts.append(f"Title: {row['title_snippet']}")
            if row['text_snippet']:
                snippet_parts.append(f"Text: {row['text_snippet']}")
            
            snippet = " | ".join(snippet_parts) if snippet_parts else row['title']
            
            results.append({
                'id': row['id'],
                'title': row['title'],
                'snippet': snippet,
                'date': row['date'],
                'sentiment': row['sentiment'],
                'media_type': row['media_type'],
                'media_path': row['media_path']
            })
        
        conn.close()
        print(f"✅ Found {len(results)} search results for query: '{query}'")
        return results
        
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        raise

def get_all_memories(limit: int = 20, offset: int = 0) -> List[Dict]:
    """
    Get all memories with pagination.
    
    Args:
        limit: Maximum number of memories to return
        offset: Number of memories to skip
        
    Returns:
        List of memory dictionaries
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM memories 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
        
    except Exception as e:
        print(f"❌ Failed to get memories: {str(e)}")
        raise

def update_memory(memory_id: int, **kwargs) -> bool:
    """
    Update a memory record.
    
    Args:
        memory_id: ID of the memory to update
        **kwargs: Fields to update
        
    Returns:
        True if update was successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['title', 'text', 'date', 'location', 'sentiment', 'person']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return False
        
        # Add updated_at timestamp
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(memory_id)
        
        query = f"UPDATE memories SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            print(f"✅ Memory {memory_id} updated successfully")
        else:
            print(f"⚠️ No memory found with ID {memory_id}")
        
        return success
        
    except Exception as e:
        print(f"❌ Failed to update memory: {str(e)}")
        raise

def delete_memory(memory_id: int) -> bool:
    """
    Delete a memory and its associated media file.
    
    Args:
        memory_id: ID of the memory to delete
        
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get memory info before deletion
        cursor.execute("SELECT media_path FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        # Delete the memory (triggers will handle FTS5 cleanup)
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if success:
            # Try to delete the associated media file
            media_path = row['media_path']
            if media_path and os.path.exists(media_path):
                try:
                    os.remove(media_path)
                    print(f"✅ Deleted media file: {media_path}")
                except Exception as e:
                    print(f"⚠️ Could not delete media file: {str(e)}")
            
            print(f"✅ Memory {memory_id} deleted successfully")
        else:
            print(f"⚠️ No memory found with ID {memory_id}")
        
        return success
        
    except Exception as e:
        print(f"❌ Failed to delete memory: {str(e)}")
        raise

def get_database_stats() -> Dict:
    """
    Get database statistics.
    
    Returns:
        Dictionary with database statistics
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total memories count
        cursor.execute("SELECT COUNT(*) as total FROM memories")
        total_memories = cursor.fetchone()['total']
        
        # Get memories by type
        cursor.execute("SELECT media_type, COUNT(*) as count FROM memories GROUP BY media_type")
        by_type = {row['media_type']: row['count'] for row in cursor.fetchall()}
        
        # Get average sentiment
        cursor.execute("SELECT AVG(sentiment) as avg_sentiment FROM memories WHERE sentiment IS NOT NULL")
        avg_sentiment = cursor.fetchone()['avg_sentiment'] or 0.0
        
        # Get database file size
        db_size = os.path.getsize(DATABASE_PATH) if os.path.exists(DATABASE_PATH) else 0
        
        conn.close()
        
        return {
            'total_memories': total_memories,
            'by_type': by_type,
            'average_sentiment': round(avg_sentiment, 2),
            'database_size_mb': round(db_size / (1024 * 1024), 2)
        }
        
    except Exception as e:
        print(f"❌ Failed to get database stats: {str(e)}")
        return {}

# Test function for development
if __name__ == "__main__":
    print("Testing database operations...")
    
    # Initialize database
    init_database()
    
    # Test creating a memory
    memory_id = create_memory(
        title="Test Memory",
        text="This is a test memory for database testing.",
        sentiment=0.5,
        media_path="/test/path.jpg",
        media_type="image"
    )
    print(f"Created memory with ID: {memory_id}")
    
    # Test searching
    results = search_memories("test")
    print(f"Search results: {len(results)} found")
    
    # Test getting memory
    memory = get_memory_by_id(memory_id)
    print(f"Retrieved memory: {memory['title']}")
    
    # Get stats
    stats = get_database_stats()
    print(f"Database stats: {stats}")