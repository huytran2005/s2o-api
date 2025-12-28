from db.database import Base, engine
from models.restaurant import Restaurant
from models.category import Category
from models.menu_item import MenuItem


def init_db():
    Base.metadata.create_all(bind=engine)
