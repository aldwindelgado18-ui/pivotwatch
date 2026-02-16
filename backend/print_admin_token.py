from app.models.base import SessionLocal
from app.models.user import User
from app.core.security import create_access_token


def print_token():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.plan == 'admin').first()
        if not admin:
            print('No admin user found')
            return
        token = create_access_token({'sub': str(admin.id), 'email': admin.email})
        print(token)
    finally:
        db.close()

if __name__ == '__main__':
    print_token()
