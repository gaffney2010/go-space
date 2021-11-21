# This class will deal with the low-level data management, saving and loading to files.

import enum
import math
import os
import random
from typing import Iterator, List, Tuple

import attr
import glob

from go_space import exceptions

from . import datum_lib


# TODO: Maybe these should be the same?
Batch = List[datum_lib.Datum]
Data = List[datum_lib.Datum]

PAGE_SIZE = 100
PAGES_IN_MEMORY = 10


class TrainTest(enum.Enum):
    TRAIN = 1
    TEST = 2


@attr.s
class Page(object):
    page_num: int = attr.ib()
    content: Data = attr.ib()


# TODO: Clean up
class DataManager(object):
    def __init__(self, tgt_dir):
        self.page_cursor = -1
        self.entry_cursor = 0
        self.test_pages = set()
        self._page_cache = list()

        # Used in the course of generating batches
        self._read_pages = set()
        self._on_page = -1
        self._read_cursor = 0

        self.data_path = tgt_dir

        self._note_existing_pages()

    def _note_existing_pages(self) -> None:
        # Assumes files are written 1, 2, ..., n
        num_files = len(glob.glob(os.path.join(self.data_path, "*.txt")))

        self.page_cursor = num_files
        self.entry_cursor = 0
        if os.path.exists(os.path.join(self.data_path, str(self.page_cursor) + ".txt")):
            self.entry_cursor = len(self._read_page(self.page_cursor))

    def _turn_page(self) -> None:
        self.page_cursor += 1
        self.entry_cursor = 0

    def _read_page(self, page_num: int) -> Page:
        if page_num >= self.page_cursor:
            raise exceptions.DataException(f"Page {page_num} doesn't exist")
        if page_num == self.page_cursor - 1 and self.entry_cursor == 0:
            raise exceptions.DataException("DataManager in bad state 1, unexpected.")

        # Check cache first
        for page in self._page_cache:
            if page.page_num == page_num:
                return page

        # Read with an LRU cache
        page_data = list()
        with open(os.path.join(self.data_path, str(page_num) + ".txt"), "r") as f:
            for line in f.readlines():
                page_data.append(datum_lib.Datum.from_json(line))
        page = Page(page_num=page_num, content=page_data)
        self._page_cache = [page] + self._page_cache
        self._page_cache = self._page_cache[:PAGES_IN_MEMORY]
        return page

    def _read_entry(self, page_num: int, entry_num: int) -> datum_lib.Datum:
        page = self._read_page(page_num)
        if entry_num > len(page):
            raise exceptions.DataException(
                f"Trying to read entry {entry_num} off of page {page_num}, but entries only go to {len(page)}."
            )
        return page[entry_num]

    def _choose_next(self, data_split: TrainTest) -> Tuple[int, int]:
        # Pick a random page, then go through the data on that page in order.  Subject to change, I suppose.
        def choose_new_page() -> int:
            if data_split == TrainTest.TRAIN:
                if len(self._read_pages | self.test_pages) == self.page_cursor:
                    raise exceptions.DataException("Tried to read too many pages.")
            if data_split == TrainTest.TEST:
                if len(self._read_pages) == len(self.test_pages):
                    raise exceptions.DataException("Tried to read too many pages.")

            def already_read(try_page: Page) -> bool:
                return try_page in self.test_pages

            def wrong_data(try_page: Page) -> bool:
                nonlocal data_split
                if data_split == TrainTest.TRAIN:
                    return try_page in self.test_pages
                if data_split == TrainTest.TEST:
                    return try_page not in self.test_pages

            try_page = random.randint(0, self.page_cursor - 1)
            while already_read(try_page) or wrong_data(try_page):
                try_page = random.randint(0, self.page_cursor - 1)
            return try_page

        if self._on_page == -1:
            self._on_page = choose_new_page()
            self._read_cursor = 0
        if self._on_page >= len(self._read_page(self._on_page)):
            self._on_page = choose_new_page()
            self._read_cursor = 0

        result = (self._on_page, self._read_cursor)
        self._read_cursor += 1
        return result

    def size(self) -> int:
        return (self.page_cursor - 1) * PAGE_SIZE + self.entry_cursor

    def save_datum(self, datum: datum_lib.Datum) -> None:
        if self.page_cursor == -1 or self.entry_cursor == PAGE_SIZE:
            self._turn_page()

        with open(
            os.path.join(self.data_path, str(self.page_cursor) + ".txt"), "a"
        ) as f:
            f.write(datum.to_json() + "\n")
        self.entry_cursor += 1

    def train_test_split(self, portion_test: float) -> None:
        # Will split on a page level
        if len(self.test_pages) > 0:
            raise exceptions.DataException("Ran train_test_split multiple times.")
        if self.page_cursor == -1:
            raise exceptions.DataException("No data saved.")

        num_test_pages = math.ceil(self.page_cursor * portion_test)
        for page in random.sample(range(self.page_cursor), num_test_pages):
            self.test_pages.add(page)

    def get_batch(
        self, batch_size: int, data_split: TrainTest, replace: bool = True
    ) -> Batch:
        # Should be semi-random.
        if self.page_cursor == -1:
            raise exceptions.DataException("No data saved.")

        if replace:
            self._read_pages = set()
            self._on_page = -1
            self._read_cursor = 0

        result = list()
        for _ in range(batch_size):
            result.append(self._read_entry(*self._choose_next(data_split)))
        return result

    def loop_epic(self, batch_size: int, data_split: TrainTest) -> Iterator[Batch]:
        num_batches = self.size() // batch_size
        for _ in range(num_batches):
            yield self.get_batch(batch_size, data_split, replace=False)
