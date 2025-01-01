from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app, db, User  # Import the app configuration and models

def test_database_connection():
    try:
        # Use the same database URI from the app configuration
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test connection by trying to query users
        user_count = session.query(User).count()
        print(f"Successfully connected to the database. Current user count: {user_count}")
        
        # Close the session
        session.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == '__main__':
    test_database_connection()
