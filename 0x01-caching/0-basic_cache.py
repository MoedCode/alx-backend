#!/usr/bin/env python3
""" BasicCache module
"""
from base_caching import BaseCaching


class BasicCache(BaseCaching):
    """BasicCache class inherits from BaseCaching and represents a caching system with no limit.  """

    def put(self, key, item):
        """Add an item to the cache if both key and item are not None."""
        if key is not None and item is not None:
            self.cache_data[key] = item
        return

    def get(self, key):
        """Retrieve an item from the cache if key exists and its value is not None."""
        if key in self.cache_data and key is not None:
            return self.cache_data[key]
        return None
