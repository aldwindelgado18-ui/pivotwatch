from app.models.base import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash, create_access_token
from datetime import datetime
import uuid

users = [
    {"email": "admin@example.com", "password": "adminpass", "name": "Admin", "plan": "admin"},
    {"email": "enterprise1@example.com", "password": "enterprisepass", "name": "Enterprise One", "plan": "enterprise"},
    {"email": "enterprise2@example.com", "password": "enterprisepass", "name": "Enterprise Two", "plan": "enterprise"},
    {"email": "user1@example.com", "password": "userpass", "name": "User One", "plan": "free"},
]

def seed():
    db = SessionLocal()
    try:
        for u in users:
            existing = db.query(User).filter(User.email == u['email']).first()
            if existing:
                print(f"Skipping existing user: {u['email']}")
                continue
            user = User(
                id=uuid.uuid4(),
                email=u['email'],
                password_hash=get_password_hash(u['password']),
                name=u['name'],
                plan=u['plan']
            )
            db.add(user)
        db.commit()
        print("✅ Seeded users")
    finally:
        db.close()

if __name__ == '__main__':
    seed()
