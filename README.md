# AI Financial Chatbot

An intelligent chatbot for financial queries and assistance, built with FastAPI and NLP.

## Features

- Natural language processing for understanding financial queries
- Real-time stock price and market information
- Financial advice and portfolio management
- User authentication and personalized responses

## Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **NLP**: NLTK, scikit-learn, spaCy
- **Authentication**: JWT, OAuth2
- **Testing**: Pytest

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/AI-Financial-Chatbot.git
   cd AI-Financial-Chatbot
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your configuration:
   ```
   SECRET_KEY=your_secret_key
   FINANCIAL_API_KEY=your_api_key
   FINANCIAL_API_URL=https://api.example.com
   ```

### Running the Application

Start the development server:
```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

API documentation is available at http://localhost:8000/docs

### Running Tests

```
pytest
```

## Project Structure

```
├── README.md
├── .gitignore
├── requirements.txt
├── app/                # Main application package
│   ├── __init__.py
│   ├── main.py         # Entry point (FastAPI setup)
│   ├── config.py       # Configuration management
│   ├── routes/         # API route modules
│   │   └── chat.py
│   ├── nlp/            # NLP utilities and models
│   │   └── intent.py
│   ├── services/       # Business logic and integrations
│   │   └── financial_api.py
│   └── models/         # Data models and schemas
│       └── user.py
├── tests/              # Unit and integration tests
│   └── test_chat.py
└── docs/               # Project documentation
    └── architecture.md
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Financial data provided by [Example Financial API]
- NLP models trained on [Example Dataset]