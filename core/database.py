from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from core.configuration import settings

engine = create_engine(settings.DATABASE_URL,connect_args={"check_same_thread":False})

SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind = engine)
Base = declarative_base()

def get_db():
    """dependency for fastapi to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables """
    Base.metadata.create_all(bind=engine)
    print("database table created")

