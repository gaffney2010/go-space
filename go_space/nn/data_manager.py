# This class will deal with the low-level data management, saving and loading to files.

import enum
import math
import os
import random
from typing import Any, Iterator, List, Tuple

import attr
import glob
import numpy as np

from go_space import exceptions

from . import datum_lib


Batch = Any  # List[np.ndarray, np.ndarray]
Data = List[datum_lib.Datum]

PAGE_SIZE = 200
PAGES_IN_MEMORY = 10


class TrainTest(enum.Enum):
    TRAIN = 1
    TEST = 2


@attr.s
class Page(object):
    page_num: int = attr.ib()
    content: Data = attr.ib()

    def __len__(self) -> int:
        return len(self.content)


# TODO: Clean up
class DataManager(object):
    def __init__(self, tgt_dir):
        # TODO: Rename cursors to be include "write"
        self.page_cursor = -1
        self.entry_cursor = 0
        self.test_pages = set()
        self._page_cache = list()

        self.data_path = tgt_dir

        # Used in the course of generating batches
        self.reset()

        self._note_existing_pages()

    def _note_existing_pages(self) -> None:
        # Assumes files are written 1, 2, ..., n
        num_files = len(glob.glob(os.path.join(self.data_path, "*.txt")))

        self.page_cursor = num_files
        self.entry_cursor = 0
        if os.path.exists(os.path.join(self.data_path, str(self.page_cursor) + ".txt")):
            self.entry_cursor = len(self._read_page(self.page_cursor))

    def _read_page(self, page_num: int) -> Page:
        if page_num >= self.page_cursor:
            raise exceptions.DataException(f"Page {page_num} doesn't exist")

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
        if entry_num >= len(page):
            raise exceptions.DataException(
                f"Trying to read entry {entry_num} off of page {page_num}, but entries only go to {len(page)-1}."
            )
        return page.content[entry_num]

    def _choose_next(self, data_split: TrainTest) -> Tuple[int, int]:
        # Pick a random page, then go through the data on that page in order.  Subject to change, I suppose.
        def choose_new_page() -> int:
            if data_split == TrainTest.TRAIN:
                if len(self._read_train_pages | self.test_pages) == self.page_cursor:
                    raise exceptions.DataException("Tried to read too many pages.")
            if data_split == TrainTest.TEST:
                if len(self._read_test_pages) == len(self.test_pages):
                    raise exceptions.DataException("Tried to read too many pages.")

            def already_read(try_page: Page) -> bool:
                nonlocal data_split
                if data_split == TrainTest.TRAIN:
                    return try_page in self._read_train_pages
                if data_split == TrainTest.TEST:
                    return try_page in self._read_test_pages

            def wrong_data(try_page: Page) -> bool:
                nonlocal data_split
                if data_split == TrainTest.TRAIN:
                    return try_page in self.test_pages
                if data_split == TrainTest.TEST:
                    return try_page not in self.test_pages

            try_page = random.randint(0, self.page_cursor - 1)
            while already_read(try_page) or wrong_data(try_page):
                try_page = random.randint(0, self.page_cursor - 1)

            # Mark as read
            if data_split == TrainTest.TRAIN:
                self._read_train_pages.add(try_page)
            if data_split == TrainTest.TEST:
                self._read_test_pages.add(try_page)

            return try_page

        if self._on_page == -1:
            self._on_page = choose_new_page()
            self._read_cursor = 0
        if self._read_cursor >= len(self._read_page(self._on_page)):
            self._on_page = choose_new_page()
            self._read_cursor = 0
        
        result = (self._on_page, self._read_cursor)
        self._read_cursor += 1
        return result

    def size(self) -> int:
        return (self.page_cursor - 1) * PAGE_SIZE + self.entry_cursor

    def save_datum(self, datum: datum_lib.Datum) -> None:
        if self.page_cursor == -1 or self.entry_cursor == PAGE_SIZE:
            self.page_cursor += 1
            self.entry_cursor = 0

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
        self, batch_size: int, data_split: TrainTest, reset: bool = True
    ) -> Batch:
        # Should be semi-random.
        if self.page_cursor == -1:
            raise exceptions.DataException("No data saved.")

        if reset:
            self.reset()

        features, targets = list(), list()
        for _ in range(batch_size):
            next_datum = self._read_entry(*self._choose_next(data_split))
            features.append(next_datum.np_feature())
            targets.append(next_datum.np_target())
        return np.stack(features, axis=0), np.stack(targets, axis=0)

    def reset(self) -> None:
        """Needs to be called between looping batches"""
        print("RESET")
        self._read_train_pages = set()
        self._read_test_pages = set()
        self._on_page = -1
        self._read_cursor = 0

    def generate_batches(
        self, batch_size: int, data_split: TrainTest
    ) -> Iterator[Batch]:
        while True:
            yield self.get_batch(batch_size, data_split, reset=False)
