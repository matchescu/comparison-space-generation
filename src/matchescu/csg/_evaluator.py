from dataclasses import dataclass

from matchescu.reference_store.comparison_space import BinaryComparisonSpace
from matchescu.typing import EntityReferenceIdentifier


@dataclass
class BlockingMetrics:
    pair_completeness: float
    pair_quality: float
    reduction_ratio: float


class BinaryComparisonSpaceEvaluator(object):
    def __init__(
        self,
        gt: set[tuple[EntityReferenceIdentifier, EntityReferenceIdentifier]],
        original_size: int,
    ):
        self.__gt = gt
        self.__size = original_size

    def __call__(self, comparison_space: BinaryComparisonSpace) -> BlockingMetrics:
        candidate_ids = set(comparison_space)
        true_positive_pairs = self.__gt.intersection(candidate_ids)
        pc = len(true_positive_pairs) / len(self.__gt) if len(self.__gt) > 0 else 0
        pq = (
            len(true_positive_pairs) / len(candidate_ids)
            if len(candidate_ids) > 0
            else 0
        )
        candidate_ratio = len(candidate_ids) / self.__size if self.__size > 0 else 0
        return BlockingMetrics(pc, pq, 1 - candidate_ratio)
