"""
Financial API service for the AI Financial Chatbot.
Handles interactions with external financial data APIs.
"""

import logging
import json
from typing import Dict, Any, Optional, List
import httpx
import re

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class FinancialService:
    """
    Service for interacting with financial APIs and generating responses.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Initialize the financial service.
        
        Args:
            api_key: API key for the financial data provider
            api_url: Base URL for the financial data API
        """
        self.api_key = api_key or settings.FINANCIAL_API_KEY
        self.api_url = api_url or settings.FINANCIAL_API_URL
        
        # Stock symbol regex pattern
        self.symbol_pattern = re.compile(r'\b[A-Z]{1,5}\b')
    
    async def get_data(self, intent: str, message: str, context: Dict = None) -> Dict:
        """
        Get financial data based on the user's intent and message.
        
        Args:
            intent: The classified intent of the user's message
            message: The user's message
            context: Additional context for the request
            
        Returns:
            Dict: The retrieved financial data
        """
        try:
            if intent == "stock_price":
                return await self._get_stock_price(message)
            elif intent == "market_info":
                return await self._get_market_info()
            elif intent == "financial_advice":
                return self._get_financial_advice(message)
            else:
                return {}
        except Exception as e:
            logger.error(f"Error getting financial data: {str(e)}")
            return {"error": str(e)}
    
    async def _get_stock_price(self, message: str) -> Dict:
        """
        Get stock price data for a symbol mentioned in the message.
        
        Args:
            message: The user's message
            
        Returns:
            Dict: Stock price data
        """
        # Extract potential stock symbols from the message
        symbols = self.symbol_pattern.findall(message)
        
        # If no symbols found, look for company names
        if not symbols:
            # This would be more sophisticated in a real implementation
            common_companies = {
                "apple": "AAPL",
                "microsoft": "MSFT",
                "amazon": "AMZN",
                "google": "GOOGL",
                "tesla": "TSLA"
            }
            
            message_lower = message.lower()
            for company, symbol in common_companies.items():
                if company in message_lower:
                    symbols = [symbol]
                    break
        
        if not symbols:
            return {"error": "No stock symbol found in the message"}
        
        # Use the first symbol found (in a real app, might ask for clarification)
        symbol = symbols[0]
        
        # In a real implementation, this would call an actual API
        # For now, return mock data
        mock_data = {
            "symbol": symbol,
            "price": 150.25,
            "change": 2.5,
            "change_percent": 1.7,
            "volume": 1500000,
            "timestamp": "2023-05-01T16:00:00Z"
        }
        
        logger.info(f"Retrieved stock price for {symbol}")
        return mock_data
    
    async def _get_market_info(self) -> Dict:
        """
        Get general market information.
        
        Returns:
            Dict: Market information data
        """
        # In a real implementation, this would call an actual API
        # For now, return mock data
        mock_data = {
            "indices": [
                {"name": "S&P 500", "value": 4200.50, "change_percent": 0.8},
                {"name": "Dow Jones", "value": 33500.25, "change_percent": 0.5},
                {"name": "NASDAQ", "value": 14200.75, "change_percent": 1.2}
            ],
            "market_status": "open",
            "trending_sectors": [
                {"name": "Technology", "change_percent": 1.5},
                {"name": "Healthcare", "change_percent": 0.7},
                {"name": "Energy", "change_percent": -0.3}
            ],
            "timestamp": "2023-05-01T16:00:00Z"
        }
        
        logger.info("Retrieved market information")
        return mock_data
    
    def _get_financial_advice(self, message: str) -> Dict:
        """
        Generate financial advice based on the user's message.
        
        Args:
            message: The user's message
            
        Returns:
            Dict: Financial advice data
        """
        # In a real implementation, this might use a more sophisticated NLP model
        # For now, return generic advice
        
        # Detect some common financial advice topics
        message_lower = message.lower()
        
        if "retire" in message_lower or "retirement" in message_lower:
            advice_type = "retirement"
            advice = "For retirement planning, consider a diversified portfolio with a mix of stocks and bonds. The general rule is to subtract your age from 110 to get the percentage to allocate to stocks."
        elif "invest" in message_lower and ("beginner" in message_lower or "start" in message_lower):
            advice_type = "beginner_investing"
            advice = "For beginners, consider starting with index funds which provide broad market exposure with lower fees. Establish an emergency fund before investing."
        elif "dividend" in message_lower:
            advice_type = "dividend_investing"
            advice = "Dividend investing can provide regular income. Look for companies with a history of stable or increasing dividend payments and reasonable payout ratios."
        else:
            advice_type = "general"
            advice = "It's important to have a diversified portfolio that aligns with your risk tolerance and financial goals. Consider consulting with a financial advisor for personalized advice."
        
        return {
            "type": advice_type,
            "advice": advice,
            "disclaimer": "This is general advice and not personalized to your specific financial situation."
        }
    
    def generate_response(self, intent: str, message: str, data: Dict = None) -> str:
        """
        Generate a natural language response based on intent and data.
        
        Args:
            intent: The classified intent
            message: The user's original message
            data: The retrieved financial data
            
        Returns:
            str: The generated response
        """
        if data and "error" in data:
            return f"I'm sorry, I couldn't get that information. {data['error']}"
        
        if intent == "stock_price" and data:
            return f"The current price of {data['symbol']} is ${data['price']:.2f}, which is {data['change_percent']:.1f}% {('up' if data['change'] > 0 else 'down')} today."
        
        elif intent == "market_info" and data:
            indices = data.get("indices", [])
            if indices:
                index_info = f"The {indices[0]['name']} is currently at {indices[0]['value']:.2f}, {indices[0]['change_percent']:.1f}% {('up' if indices[0]['change_percent'] > 0 else 'down')}."
                return f"Here's the latest market information: {index_info} The market is currently {data.get('market_status', 'unknown')}."
            return "I couldn't find specific market information at the moment."
        
        elif intent == "financial_advice" and data:
            return f"{data['advice']} {data['disclaimer']}"
        
        elif intent == "greeting":
            return "Hello! I'm your financial assistant. How can I help you with your financial questions today?"
        
        elif intent == "goodbye":
            return "Goodbye! Feel free to come back if you have more financial questions."
        
        else:
            return "I'm not sure how to respond to that. Could you try rephrasing your question about financial matters?"
