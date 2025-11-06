from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from .config import settings


DATABASE_URL = (
    f"mysql+mysqlconnector://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
)


engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()


def init_db(engine_):
    from . import models
    metadata.create_all(bind=engine_)