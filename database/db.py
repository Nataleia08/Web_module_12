import configparser
import pathlib

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

file_config = pathlib.Path(__file__).parent.joinpath('config.ini')
config = configparser.ConfigParser()
config.read(file_config)

username = config.get("DEV_DB", "USER")
password = config.get("DEV_DB", "PASSWORD")
domain = config.get("DEV_DB", "DOMAIN")
port = config.get("DEV_DB", "PORT")
database = config.get("DEV_DB", "DB_NAME")

url = f"postgresql://{username}:{password}@{domain}:{port}/{database}"

engine = create_engine(url, echo = True)
DBSession = sessionmaker(autocommit= False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    session = DBSession()
    try:
        yield session
    finally:
        session.close()
