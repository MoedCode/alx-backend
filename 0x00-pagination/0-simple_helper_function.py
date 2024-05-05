#!/usr/bin/env python3

def index_range(page , page_size):
    """ Calculate the start and end indices for pagination."""
    end = page_size * page
    start = end - page_size
    return (start, end)

if __name__ == "__main__":
    res = index_range(1, 7)
    print(type(res))
    print(res)

    res = index_range(page=3, page_size=15)
    print(type(res))
    print(res)

