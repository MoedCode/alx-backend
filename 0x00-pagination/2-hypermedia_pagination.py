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
        Idx = index_range(page, page_size)
        # batch = []
        # for i in range(Idx[0], Idx[1]):
        #     batch.append(all_data[i])
        # return batch

        return [] if Idx[0] >= len(all_data) else\
            all_data[Idx[0]: Idx[1]]

    def get_hyper(self, page: int = 1, page_size: int = 10) -> List[List]:
        assert isinstance(page, int) and isinstance(page_size, int)
        assert page > 0 and page_size > 0
        all_data = self.dataset()
        """
        Returns a dictionary with the following information:

        page_size: Size of the dataset page returned.
        page: Current page number.
        data: Dataset page (same as the previous task's return).
        next_page: Number of the next page; None if no next page.
        prev_page: Number of the previous page; None if no previous page.
        total_pages: Total number of pages in the dataset.
        Args:
        page (int): Current page number.
        page_size (int): Size of each page.

        Returns:
        dict: Dictionary containing the specified key-value pairs.
        """
        data = self.get_page(page, page_size)
        total_pages = math.ceil(len(all_data)/page_size)
        next_page = page + 1 if page + 1 < total_pages else None
        prev_page = page - 1 if page - 1 >= 2 else None

        Idx = index_range(page, page_size)
        return {'page_size': page_size, 'page': page, 'data': data, 'next_page': next_page, 'prev_page': prev_page, 'total_pages': total_pages}


def index_range(page, page_size):
    """ Calculate the start and end indices for pagination."""
    end = page_size * page
    start = end - page_size
    return (start, end)


if __name__ == "__main__":

    server = Server()

    print(server.get_hyper(1, 2))
    print("---")
    print(server.get_hyper(2, 2))
    print("---")
    print(server.get_hyper(100, 3))
    print("---")
    print(server.get_hyper(3000, 100))
