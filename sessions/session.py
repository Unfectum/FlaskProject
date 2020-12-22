from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.model import User, Request, Course

engine = create_engine('postgresql://postgres:1234@localhost:5432/Flask_db')
Session = sessionmaker(bind=engine)
session = Session()


session.commit()
