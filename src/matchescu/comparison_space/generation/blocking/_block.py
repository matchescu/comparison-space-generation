import itertools
from dataclasses import dataclass, field
from typing import Any, Iterator, Iterable

from matchescu.typing import EntityReferenceIdentifier


@dataclass(frozen=True, eq=True)
class Block:
    key: Any = field(init=True, repr=True, hash=True, compare=True)
    ref_ids: list[EntityReferenceIdentifier] = field(
        init=False, repr=False, hash=False, compare=False, default_factory=list
    )

    def __post_init__(self):
        if self.key is None or str(self.key).strip() == "":
            raise ValueError("invalid blocking key")

    def __iter__(self) -> Iterator[EntityReferenceIdentifier]:
        return iter(self.ref_ids)

    def append(self, ref_id: EntityReferenceIdentifier) -> "Block":
        self.ref_ids.append(ref_id)
        return self

    def extend(self, ref_ids: Iterable[EntityReferenceIdentifier]) -> "Block":
        self.ref_ids.extend(ref_ids)
        return self

    def count_sources(self) -> int:
        sources = set(ref_id.source for ref_id in self.ref_ids)
        return len(sources)

    def candidate_pairs(
        self, generate_deduplication_pairs: bool = True
    ) -> Iterator[tuple[EntityReferenceIdentifier, EntityReferenceIdentifier]]:
        by_source = {
            source: list(ids)
            for source, ids in itertools.groupby(
                self.ref_ids, key=lambda ref_id: ref_id.source
            )
        }
        n_sources = len(by_source)
        if n_sources < 1:
            yield from ()
        elif n_sources < 2 and generate_deduplication_pairs:
            for pair in itertools.combinations(self.ref_ids, 2):
                yield pair
        else:
            sources = list(by_source.keys())
            for a, b in itertools.combinations(sources, 2):
                for prod in itertools.product(by_source[a], by_source[b]):
                    yield prod
