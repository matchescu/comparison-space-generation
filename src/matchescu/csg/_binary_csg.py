import itertools
from typing import Generator

from matchescu.blocking import Blocker
from matchescu.comparison_filtering import ComparisonFilter
from matchescu.reference_store.comparison_space import (
    BinaryComparisonSpace,
    InMemoryComparisonSpace,
)
from matchescu.reference_store.id_table import IdTable
from matchescu.typing import EntityReferenceIdentifier


class BinaryComparisonSpaceGenerator:
    def __init__(self):
        self._blockers: list[Blocker] = []
        self._filters: list[ComparisonFilter] = []

    def add_blocker(self, blocker: Blocker) -> "BinaryComparisonSpaceGenerator":
        self._blockers.append(blocker)
        return self

    def __get_candidate_pairs(
        self,
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        yield from itertools.chain.from_iterable(
            map(
                lambda x: x.candidate_pairs(),
                itertools.chain.from_iterable(map(lambda x: x(), self._blockers)),
            )
        )

    def __call__(self) -> BinaryComparisonSpace:
        comparison_space = InMemoryComparisonSpace()
        for left_id, right_id in self.__get_candidate_pairs():
            comparison_space.put(left_id, right_id)
        return comparison_space
