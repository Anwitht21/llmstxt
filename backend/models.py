from pydantic import BaseModel, HttpUrl

class CrawlRequest(BaseModel):
    url: HttpUrl
    maxPages: int = 50
    descLength: int = 500
