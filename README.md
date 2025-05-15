# AI Financial Chatbot

An intelligent chatbot for financial queries and assistance, built with FastAPI, NLP, and Supabase.

## Features

- Natural language processing for understanding financial queries
- Real-time stock price and market information
- Financial advice and portfolio management
- User authentication and personalized responses
- Chat history storage with Supabase PostgreSQL database

## Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **Database**: PostgreSQL via Supabase
- **NLP**: NLTK, scikit-learn, spaCy
- **Authentication**: JWT, OAuth2
- **Testing**: Pytest

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Supabase account (free tier available at [supabase.com](https://supabase.com))

### Supabase Setup

1. Create a new project on [Supabase](https://supabase.com)
2. Once your project is created, go to Project Settings > API to get your:
   - Project URL (SUPABASE_URL)
   - API Key (SUPABASE_KEY) - use the "anon" public key

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

4. Create a `.env` file in the root directory with your configuration (copy from `.env.example`):
   ```
   SECRET_KEY=your_secret_key
   FINANCIAL_API_KEY=your_api_key
   FINANCIAL_API_URL=https://api.example.com
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   ```

### Database Setup

Run the database setup script to create the necessary tables and a test user:

```
python scripts/setup_database.py
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
├── .env.example
├── requirements.txt
├── app/                # Main application package
│   ├── __init__.py
│   ├── main.py         # Entry point (FastAPI setup)
│   ├── config.py       # Configuration management
│   ├── db/             # Database modules
│   │   ├── __init__.py
│   │   ├── database.py # Supabase client
│   │   └── models.py   # Database operations
│   ├── routes/         # API route modules
│   │   └── chat.py
│   ├── nlp/            # NLP utilities and models
│   │   └── intent.py
│   ├── services/       # Business logic and integrations
│   │   └── financial_api.py
│   └── models/         # Data models and schemas
│       └── user.py
├── scripts/            # Utility scripts
│   └── setup_database.py # Database setup script
├── tests/              # Unit and integration tests
│   └── test_chat.py
└── docs/               # Project documentation
    └── architecture.md
```

## API Endpoints

- **POST /register**: Register a new user
- **POST /token**: Get an access token (OAuth2)
- **POST /api/v1/chat/message**: Send a message to the chatbot
- **GET /api/v1/chat/history**: Get chat history for the current user
- **GET /health**: Check API health status

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Financial data provided by [Example Financial API]
- NLP models trained on [Example Dataset]
- Database powered by [Supabase](https://supabase.com)