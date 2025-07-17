from database import engine, Base
import db_models  # Ensures all models are registered

def initialize_database():
    print("🔧 Creating tables in catdams.db...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully.")

if __name__ == "__main__":
    initialize_database()
