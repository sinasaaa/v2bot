// ===== IMPORTS & DEPENDENCIES =====
from sqlalchemy.orm import Session
from models.user import User

# ===== CRUD FUNCTIONS FOR USER =====

def get_user_by_telegram_id(db: Session, telegram_id: int) -> User | None:
    """
    Retrieves a user from the database by their Telegram ID.
    """
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(db: Session, telegram_user, is_admin: bool = False) -> User:
    """
    Creates a new user in the database.
    """
    # Check if user already exists
    db_user = get_user_by_telegram_id(db, telegram_id=telegram_user.id)
    if db_user:
        return db_user
        
    new_user = User(
        telegram_id=telegram_user.id,
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
        username=telegram_user.username,
        is_admin=is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"✅ User {new_user.username} (ID: {new_user.telegram_id}) created in DB.")
    return new_user

def is_user_admin(db: Session, telegram_id: int) -> bool:
    """
    Checks if a user is an admin based on the database flag.
    """
    user = get_user_by_telegram_id(db, telegram_id)
    return user.is_admin if user else False
