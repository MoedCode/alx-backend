#!/usr/bin/env python3
""" class FIFOCache  module
"""
from base_caching import BaseCaching


class FIFOCache(BaseCaching):
    "class FIFOCache that inherits from BaseCaching and is a caching system:"

    def __init__(self):
        super().__init__()

    def put(self, key=None, item=None):
        """Add an item to the cache if both key and item are """
        if key is None or item is None:
            return
        if len(self.cache_data) >= self.MAX_ITEMS:
            first_in = list(self.cache_data.keys())[0]
            if key not in self.cache_data:
                print("DISCARD: {}".format(first_in))
                del self.cache_data[first_in]
        self.cache_data[key] = item

    def get(self, key):
        """Retrieve an item from the cache if key exists and ."""
        if key in self.cache_data and key is not None:
            return self.cache_data[key]
        return None


if __name__ == "__main__":

    my_cache = FIFOCache()
    my_cache.put("A", "Hello")
    my_cache.put("B", "World")
    my_cache.put("C", "Holberton")
    my_cache.put("D", "School")
    my_cache.print_cache()
    my_cache.put("E", "Battery")
    my_cache.print_cache()
    my_cache.put("C", "Street")
    my_cache.print_cache()
    my_cache.put("F", "Mission")
    my_cache.print_cache()
