#!/usr/bin/env python3
"""
    index_range function file for pagination
"""
import csv
import math
from typing import List


class Server:
    """Server class to paginate a database of popular baby names.
    """
    DATA_FILE = "Popular_Baby_Names.csv"

    def __init__(self):
        self.__dataset = None

    def index_range(self, page, page_size):
        """ Calculate the start and end indices for pagination."""
        end = page_size * page
        start = end - page_size
        return (start, end)

    def dataset(self) -> List[List]:
        """Cached dataset
        """
        if self.__dataset is None:
            with open(self.DATA_FILE) as f:
                reader = csv.reader(f)
                dataset = [row for row in reader]
            self.__dataset = dataset[1:]

        return self.__dataset

    def get_page(self, page: int = 1, page_size: int = 10) -> List[List]:
        """
            Finds the correct indexes to paginate dataset correctly
            and return the appropriate page of the dataset
            Args:
                page: int
                page_size: int
            Return:
                List[List]:
        """

        assert isinstance(page, int) and isinstance(page_size, int)
        assert page > 0 and page_size > 0
        all_data = self.dataset()
        Idx = self.index_range(page, page_size)
        return [] if Idx[0] >= len(all_data) else\
            all_data[Idx[0]: Idx[1]]


'''
    def get_page(self, page: int = 1, page_size: int = 10) -> List[List]:
        if not isinstance(page, int) or not isinstance(page_size, int):
            return TypeError("Page and page_size must be integers")
        if page < 0 or page_size < 0:
            return ValueError("Page and page_size must be greater than or equal to 0")
        if page == 0 or page_size == 0:
            return ValueError("Page and page_size must be greater than 0")

        Idx = self.index_range(page, page_size)
        print(Idx)
        all_data = self.dataset()
        j = 0
        concern_data = []
        for i in range(Idx[0], Idx[1]):
            concern_data[j] = all_data[i][:]
            j += 1
        return concern_data
'''
if __name__ == "__main__":

    Server = __import__('1-simple_pagination').Server

    server = Server()

    try:
        should_err = server.get_page(-10, 2)
    except AssertionError:
        print("AssertionError raised with negative values")

    try:
        should_err = server.get_page(0, 0)
    except AssertionError:
        print("AssertionError raised with 0")

    try:
        should_err = server.get_page(2, 'Bob')
    except AssertionError:
        print("AssertionError raised when page and/or page_size are not ints")
    print(server.get_page(1, 3))
    print(server.get_page(3, 2))
    print(server.get_page(3000, 100))
