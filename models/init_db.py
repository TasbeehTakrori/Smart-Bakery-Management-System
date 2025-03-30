from models import Base
from config import engine

def init_db():
    Base.metadata.create_all(bind=engine)
