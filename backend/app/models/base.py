from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Ensure all model modules are imported so mappers are registered
from . import user as _user  # noqa: F401
from . import company as _company  # noqa: F401
from . import snapshot as _snapshot  # noqa: F401
from . import change as _change  # noqa: F401
from . import notification as _notification  # noqa: F401

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()