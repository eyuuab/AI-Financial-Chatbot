"""
Intent classification module for the AI Financial Chatbot.
Analyzes user messages to determine their intent.
"""

import os
import logging
import re
from typing import Tuple, List, Dict, Optional, Callable
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Simple tokenizer and stopwords as fallback
SIMPLE_STOPWORDS = set([
    'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
    'which', 'this', 'that', 'these', 'those', 'then', 'just', 'so', 'than',
    'such', 'both', 'through', 'about', 'for', 'is', 'of', 'while', 'during',
    'to', 'from', 'in', 'on', 'at', 'by', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up',
    'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
    'don', 'should', 'now', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
    'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
    'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
    'they', 'them', 'their', 'theirs', 'themselves', 'am', 'is', 'are', 'was',
    'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
    'did', 'doing'
])

def simple_tokenize(text: str) -> List[str]:
    """Simple tokenizer that splits on non-alphanumeric characters."""
    return [token.lower() for token in re.findall(r'\w+', text)]

# Try to import NLTK, but use simple tokenizer if not available
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords

    # Ensure NLTK resources are downloaded
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')

        # Use NLTK tokenizer and stopwords
        tokenizer: Callable = word_tokenize
        stop_words: List[str] = stopwords.words('english')
        logger.info("Using NLTK tokenizer and stopwords")

    except LookupError:
        # Try to download NLTK data
        try:
            nltk.download('punkt')
            nltk.download('stopwords')
            tokenizer = word_tokenize
            stop_words = stopwords.words('english')
            logger.info("Downloaded NLTK data, using NLTK tokenizer and stopwords")
        except Exception as e:
            # Fall back to simple tokenizer
            logger.warning(f"Could not download NLTK data: {str(e)}")
            tokenizer = simple_tokenize
            stop_words = list(SIMPLE_STOPWORDS)
            logger.info("Using simple tokenizer and stopwords")

except ImportError:
    # Fall back to simple tokenizer
    logger.warning("NLTK not available, using simple tokenizer and stopwords")
    tokenizer = simple_tokenize
    stop_words = list(SIMPLE_STOPWORDS)

class IntentClassifier:
    """
    Intent classification for financial chatbot messages.
    Uses a simple ML model to classify user intents.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the intent classifier.

        Args:
            model_path: Path to the saved model file
        """
        self.model_path = model_path or settings.NLP_MODEL_PATH
        self.model = None
        self.intents = [
            "stock_price",
            "market_info",
            "financial_advice",
            "portfolio_management",
            "general_question",
            "greeting",
            "goodbye",
            "unknown"
        ]

        # Try to load the model if it exists
        self._load_model()

        # If model doesn't exist, train a simple one
        if self.model is None:
            self._train_default_model()

    def _load_model(self) -> None:
        """Load the model from disk if it exists."""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded intent classification model from {self.model_path}")
            else:
                logger.warning(f"Model file not found at {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")

    def _train_default_model(self) -> None:
        """Train a simple default model with example phrases."""
        logger.info("Training default intent classification model")

        # Example training data
        training_data = [
            # stock_price intent
            ("What's the current price of Apple stock?", "stock_price"),
            ("How much is MSFT trading for?", "stock_price"),
            ("Tell me the stock price of Amazon", "stock_price"),

            # market_info intent
            ("How is the market performing today?", "market_info"),
            ("What's the current state of the S&P 500?", "market_info"),
            ("Tell me about today's market trends", "market_info"),

            # financial_advice intent
            ("Should I invest in tech stocks?", "financial_advice"),
            ("What's a good investment strategy for retirement?", "financial_advice"),
            ("How should I diversify my portfolio?", "financial_advice"),

            # portfolio_management intent
            ("Show me my portfolio performance", "portfolio_management"),
            ("What's my current balance?", "portfolio_management"),
            ("How are my investments doing?", "portfolio_management"),

            # general_question intent
            ("What is a stock?", "general_question"),
            ("Explain what a bond is", "general_question"),
            ("How do dividends work?", "general_question"),

            # greeting intent
            ("Hello", "greeting"),
            ("Hi there", "greeting"),
            ("Good morning", "greeting"),

            # goodbye intent
            ("Goodbye", "goodbye"),
            ("Bye", "goodbye"),
            ("See you later", "goodbye"),
        ]

        # Prepare data
        X = [item[0] for item in training_data]
        y = [item[1] for item in training_data]

        # Create and train the model
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(tokenizer=tokenizer, stop_words=stop_words)),
            ('clf', MultinomialNB())
        ])

        self.model.fit(X, y)

        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)

        logger.info(f"Trained and saved default model to {self.model_path}")

    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classify the intent of a user message.

        Args:
            text: The user's message

        Returns:
            Tuple[str, float]: The predicted intent and confidence score
        """
        if self.model is None:
            logger.warning("Model not loaded, returning default intent")
            return "unknown", 0.0

        # Make prediction
        intent = self.model.predict([text])[0]

        # Get confidence (probability of the predicted class)
        try:
            proba = self.model.predict_proba([text])[0]
            confidence = max(proba)
        except:
            # If probabilities aren't available
            confidence = 0.7  # Default confidence

        logger.info(f"Classified '{text}' as '{intent}' with confidence {confidence:.2f}")
        return intent, float(confidence)
