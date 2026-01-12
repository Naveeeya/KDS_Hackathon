"""
Sentiment analysis module using NLTK VADER.
Provides robust polarity detection for narrative text.
"""

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentimentAnalyzer, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize NLTK resources"""
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
            
        self.sia = SentimentIntensityAnalyzer()
        
    def get_polarity(self, text: str) -> str:
        """
        Returns 'positive' or 'negative' based on VADER compound score.
        Threshold is -0.05 for negative.
        """
        scores = self.sia.polarity_scores(text)
        # Standard VADER threshold
        if scores['compound'] <= -0.05:
            return 'negative'
        return 'positive'  # Default for neutral/positive
