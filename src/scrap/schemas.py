import datetime
from pydantic import BaseModel



class PostSchema(BaseModel):
    id: int | None = None
    url: str 
    title: str
    content: str
    author: str
    published_at: datetime.datetime
    scraped_at: datetime.datetime
    
