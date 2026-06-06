# app/models/image_cache.py

from pydantic import BaseModel


class ImageCache(BaseModel):
    image_hash: str
    result: dict