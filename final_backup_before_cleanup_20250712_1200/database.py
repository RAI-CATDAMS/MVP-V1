import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CATDAMS DATABASE URL ===
# Use environment variables for database configuration
DB_SERVER = os.getenv("AZURE_SQL_SERVER", "catdamsadmin.database.windows.net")
DB_NAME = os.getenv("AZURE_SQL_DATABASE", "catdamsadmin")
DB_USER = os.getenv("AZURE_SQL_USERNAME", "catdamsadmin")
DB_PASSWORD = os.getenv("AZURE_SQL_PASSWORD", "Chloe310$$")

DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}:1433/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server"

# Fallback to local SQLite if Azure SQL is not configured
if not all([DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD]):
    print("[WARNING] Azure SQL credentials not found, using local SQLite database")
    DATABASE_URL = "sqlite:///./catdams.db"

# === SQLAlchemy Engine ===
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    future=True
)

# === Session Factory (Thread-Safe) ===
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

# === Declarative Base Class for Models ===
Base = declarative_base()

# === Function to Retrieve a Database Session ===
def get_db_session():
    return SessionLocal()

# Backward compatibility alias
def get_db():
    """Backward compatibility alias for get_db_session"""
    return get_db_session()
