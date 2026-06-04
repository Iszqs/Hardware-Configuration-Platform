from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'hardware.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)

    if not db_has_data():
        db = SessionLocal()
        try:
            cat_motor = Category(id=1, label='立三电机')
            db.add(cat_motor)
            db.flush()
            db.add_all([
                DeviceType(id=1, label='35电机', category_id=1),
                DeviceType(id=2, label='57电机', category_id=1),
            ])
            db.commit()
        finally:
            db.close()

def db_has_data():
    from .models import Category
    db = SessionLocal()
    count = db.query(Category).count()
    db.close()
    return count > 0
