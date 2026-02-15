from sqlalchemy.orm import Session
from app.models.user import User

def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, hashed_password: str) -> User:
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def set_role(db: Session, email: str, role: str) -> User | None:
    user = get_by_email(db, email)
    if not user:
        return None
    user.role = role
    db.commit()
    db.refresh(user)
    return user
