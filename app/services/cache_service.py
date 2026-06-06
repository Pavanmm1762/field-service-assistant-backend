# app/services/cache_service.py

class CacheService:

    def __init__(self):
        self.cache = {}

    def get(self, image_hash: str):
        return self.cache.get(image_hash)

    def set(self, image_hash: str, result: dict):
        self.cache[image_hash] = result


cache_service = CacheService()