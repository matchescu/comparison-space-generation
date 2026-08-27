import itertools
from collections.abc import Generator

from matchescu.reference_store.comparison_space import (
    BinaryComparisonSpace,
    InMemoryComparisonSpace,
)
from matchescu.typing import EntityReferenceIdentifier

from .blocking import Block, Blocker
from .filtering import ComparisonFilter


class BinaryComparisonSpaceGenerator:
    def __init__(self):
        self._blockers: list[Blocker] = []
        self._filters: list[ComparisonFilter] = []

    def add_blocker(self, blocker: Blocker) -> "BinaryComparisonSpaceGenerator":
        self._blockers.append(blocker)
        return self

    def add_filter(
        self, cmp_filter: ComparisonFilter
    ) -> "BinaryComparisonSpaceGenerator":
        self._filters.append(cmp_filter)
        return self

    @staticmethod
    def __gen_candidate_pairs(x: Block) -> Generator[tuple, None, None]:
        yield from x.candidate_pairs()

    @staticmethod
    def __gen_blocks(x: Blocker) -> Generator[Block, None, None]:
        yield from x()

    def __get_candidate_pairs(
        self,
    ) -> Generator[
        tuple[EntityReferenceIdentifier, EntityReferenceIdentifier], None, None
    ]:
        yield from itertools.chain.from_iterable(
            map(
                self.__gen_candidate_pairs,
                itertools.chain.from_iterable(map(self.__gen_blocks, self._blockers)),
            )
        )

    def __matches_all_filters(self, ids: tuple) -> bool:
        return all(f(*ids) for f in self._filters)

    def __call__(self) -> BinaryComparisonSpace:
        comparison_space = InMemoryComparisonSpace()
        candidate_generator = filter(
            self.__matches_all_filters, self.__get_candidate_pairs()
        )
        for left_id, right_id in candidate_generator:
            comparison_space.put(left_id, right_id)
        return comparison_space
