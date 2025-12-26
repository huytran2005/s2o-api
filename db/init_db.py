from db.database import Base, engine

from models.restaurant import Restaurant

def init_db():
    Base.metadata.create_all(bind=engine)
