from db.database import Base, engine
from models.restaurant import Restaurant
from models.category import Category
from models.menu_item import MenuItem
from models.qr_code import QRCode
from models.guest_session import GuestSession

def init_db():
    Base.metadata.create_all(bind=engine)
