#!/usr/bin/python3
# from base_caching import BaseCaching # => 0
# import base_caching # => 1
from base_caching import *  # => 2

# x =BaseCaching() # => 0
# x =base_caching. BaseCaching() # => 1
x = BaseCaching()   # => 2
print(x.__dict__)
