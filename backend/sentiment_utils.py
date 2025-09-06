"""
Sentiment analysis utilities for MemoriaVault.
Analyzes the emotional tone of extracted text using TextBlob and VADER.
"""

from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Tuple
import re

# Initialize VADER sentiment analyzer
vader_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> float:
    """
    Analyze the sentiment of text and return a score between -1 and 1.
    
    This function uses two sentiment analysis methods:
    1. TextBlob: Good for general sentiment analysis
    2. VADER: Better for social media text and informal language
    
    The final score is an average of both methods.
    
    Sentiment scores:
    - 1.0: Very positive (happy, excited, love)
    - 0.0: Neutral (factual, no emotion)
    - -1.0: Very negative (sad, angry, hate)
    
    Args:
        text: Text to analyze
        
    Returns:
        Sentiment score between -1.0 and 1.0
    """
    try:
        if not text or not text.strip():
            return 0.0
        
        # Clean the text
        cleaned_text = clean_text_for_sentiment(text)
        
        if not cleaned_text:
            return 0.0
        
        # Get sentiment from TextBlob
        textblob_score = get_textblob_sentiment(cleaned_text)
        
        # Get sentiment from VADER
        vader_score = get_vader_sentiment(cleaned_text)
        
        # Average the two scores for better accuracy
        final_score = (textblob_score + vader_score) / 2
        
        # Round to 2 decimal places
        return round(final_score, 2)
        
    except Exception as e:
        print(f"❌ Sentiment analysis failed: {str(e)}")
        return 0.0

def get_textblob_sentiment(text: str) -> float:
    """
    Get sentiment score using TextBlob.
    
    TextBlob uses a simple rule-based approach and is good for:
    - General text sentiment
    - Longer documents
    - Formal language
    
    Args:
        text: Text to analyze
        
    Returns:
        Sentiment score between -1.0 and 1.0
    """
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except Exception as e:
        print(f"❌ TextBlob sentiment failed: {str(e)}")
        return 0.0

def get_vader_sentiment(text: str) -> float:
    """
    Get sentiment score using VADER (Valence Aware Dictionary and sEntiment Reasoner).
    
    VADER is particularly good for:
    - Social media text
    - Informal language
    - Text with emojis and slang
    - Short sentences
    
    Args:
        text: Text to analyze
        
    Returns:
        Sentiment score between -1.0 and 1.0
    """
    try:
        scores = vader_analyzer.polarity_scores(text)
        # VADER returns a compound score that's already normalized
        return scores['compound']
    except Exception as e:
        print(f"❌ VADER sentiment failed: {str(e)}")
        return 0.0

def clean_text_for_sentiment(text: str) -> str:
    """
    Clean text before sentiment analysis.
    
    This function:
    1. Removes extra whitespace
    2. Removes special characters that might confuse sentiment analysis
    3. Normalizes the text
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove URLs (they don't contribute to sentiment)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    text = re.sub(r'[.]{2,}', '.', text)
    
    return text.strip()

def get_sentiment_label(score: float) -> str:
    """
    Convert sentiment score to a human-readable label.
    
    Args:
        score: Sentiment score between -1.0 and 1.0
        
    Returns:
        Sentiment label
    """
    if score >= 0.6:
        return "Very Positive"
    elif score >= 0.2:
        return "Positive"
    elif score >= -0.2:
        return "Neutral"
    elif score >= -0.6:
        return "Negative"
    else:
        return "Very Negative"

def get_sentiment_emoji(score: float) -> str:
    """
    Get an emoji representing the sentiment.
    
    Args:
        score: Sentiment score between -1.0 and 1.0
        
    Returns:
        Emoji representing the sentiment
    """
    if score >= 0.6:
        return "😊"
    elif score >= 0.2:
        return "🙂"
    elif score >= -0.2:
        return "😐"
    elif score >= -0.6:
        return "😔"
    else:
        return "😢"

def analyze_sentiment_detailed(text: str) -> Dict[str, any]:
    """
    Get detailed sentiment analysis including multiple metrics.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with detailed sentiment information
    """
    try:
        if not text or not text.strip():
            return {
                'score': 0.0,
                'label': 'Neutral',
                'emoji': '😐',
                'textblob_score': 0.0,
                'vader_score': 0.0,
                'confidence': 0.0
            }
        
        cleaned_text = clean_text_for_sentiment(text)
        
        # Get individual scores
        textblob_score = get_textblob_sentiment(cleaned_text)
        vader_score = get_vader_sentiment(cleaned_text)
        
        # Calculate final score
        final_score = (textblob_score + vader_score) / 2
        
        # Calculate confidence (how much the two methods agree)
        confidence = 1.0 - abs(textblob_score - vader_score)
        
        return {
            'score': round(final_score, 2),
            'label': get_sentiment_label(final_score),
            'emoji': get_sentiment_emoji(final_score),
            'textblob_score': round(textblob_score, 2),
            'vader_score': round(vader_score, 2),
            'confidence': round(confidence, 2)
        }
        
    except Exception as e:
        print(f"❌ Detailed sentiment analysis failed: {str(e)}")
        return {
            'score': 0.0,
            'label': 'Neutral',
            'emoji': '😐',
            'textblob_score': 0.0,
            'vader_score': 0.0,
            'confidence': 0.0
        }

# Test function for development
if __name__ == "__main__":
    # Test sentiment analysis with sample texts
    test_texts = [
        "I love this app! It's amazing and makes me so happy! 😊",
        "This is okay, nothing special.",
        "I hate this. It's terrible and makes me angry! 😡",
        "The weather is nice today.",
        "I'm so excited about the new features!"
    ]
    
    print("Testing sentiment analysis...")
    for text in test_texts:
        detailed = analyze_sentiment_detailed(text)
        print(f"Text: {text}")
        print(f"Score: {detailed['score']} ({detailed['label']}) {detailed['emoji']}")
        print(f"TextBlob: {detailed['textblob_score']}, VADER: {detailed['vader_score']}")
        print(f"Confidence: {detailed['confidence']}")
        print("-" * 50)
