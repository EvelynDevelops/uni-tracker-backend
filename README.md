# Uni Tracker Backend

Unified Tracker Backend Service based on FastAPI

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Service

### Development Mode
```bash
python main.py
```

### Using uvicorn
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

After starting the service, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
uni-tracker-backend/
├── main.py              # FastAPI application main file
├── requirements.txt     # Python dependencies
├── README.md           # Project documentation
└── db/                 # Database related files
    ├── initializeDatabase.sql    # Database initialization script
    ├── db_session.py            # Database session management
    ├── orm_db_manager.py        # ORM database manager
    └── orms/                    # ORM models
        └── __init__.py          # ORM models package
``` 