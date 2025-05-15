#!/usr/bin/env python3
"""
Download required NLTK data for the AI Financial Chatbot.
"""

import nltk

def download_nltk_data():
    """Download required NLTK data."""
    print("Downloading NLTK data...")
    
    # Download required NLTK data
    nltk.download('punkt')
    nltk.download('stopwords')
    
    print("NLTK data downloaded successfully.")

if __name__ == "__main__":
    download_nltk_data()
