from sqlalchemy import Column, String, Text, Integer, DateTime

from src.database import Base


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    url = Column(String(164), nullable=False, unique=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(126), nullable=False)
    published_at = Column(DateTime, nullable=False)
    scraped_at = Column(DateTime, nullable=False)


