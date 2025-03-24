from abc import ABCMeta, abstractmethod
from typing import Generator

from matchescu.reference_store.id_table import IdTable

from matchescu.blocking._block import Block


class Blocker(metaclass=ABCMeta):
    def __init__(self, id_table: IdTable):
        self._id_table = id_table

    @abstractmethod
    def __call__(self) -> Generator[Block, None, None]:
        pass
