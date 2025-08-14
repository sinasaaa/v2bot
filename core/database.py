# ===== IMPORTS & DEPENDENCIES =====
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# ===== DATABASE ENGINE =====
# The engine is the entry point to the database.
# We configure it with the connection URL from our settings.
# pool_pre_ping=True checks connections for liveness before using them.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True
)

# ===== SESSION MAKER =====
# A SessionLocal class is a factory for new Session objects.
# A Session is the primary interface for database operations.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===== DEPENDENCY FOR GETTING DB SESSION =====
def get_db():
    """
    A dependency function to get a database session.
    This will be used in our API routes and bot handlers to interact with the database.
    It ensures that the database session is always closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
