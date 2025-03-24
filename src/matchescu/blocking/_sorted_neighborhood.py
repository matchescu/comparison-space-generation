from typing import Generator

from matchescu.blocking import Block
from matchescu.blocking._blocker import Blocker
from matchescu.blocking._tokenization import tokenize_reference
from matchescu.reference_store.id_table import IdTable
from matchescu.typing import EntityReference


class SortedNeighborhoodBlocker(Blocker):
    def __init__(self, id_table: IdTable, window_size: int = 4):
        super().__init__(id_table)
        self.__window_size = window_size

    def __sorted_references(self) -> list[tuple[str, EntityReference]]:
        tokenized_refs = list(
            map(lambda r: (" ".join(tokenize_reference(r)), r), self._id_table)
        )
        tokenized_refs.sort(key=lambda t: t[0])
        return tokenized_refs

    def __call__(self) -> Generator[Block, None, None]:
        sorted_refs = self.__sorted_references()
        for i in range(len(sorted_refs) - self.__window_size + 1):
            yield Block(i).extend(
                x[1].id for x in sorted_refs[i : i + self.__window_size]
            )
