from time import monotonic


class TTLCache:
    def __init__(self, ttl_seconds=60):
        self.ttl_seconds = ttl_seconds
        self._items = {}

    def get(self, key, factory):
        now = monotonic()
        item = self._items.get(key)
        if item and item[0] > now:
            return item[1]
        value = factory()
        self._items[key] = (now + self.ttl_seconds, value)
        return value

    def clear(self):
        self._items.clear()


public_cache = TTLCache(ttl_seconds=90)
