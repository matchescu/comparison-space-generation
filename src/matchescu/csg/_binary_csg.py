from matchescu.blocking import Blocker
from matchescu.comparison_filtering import ComparisonFilter
from matchescu.reference_store.comparison_space import BinaryComparisonSpace


class BinaryComparisonSpaceGenerator:
    def __init__(self):
        self._blockers: list[Blocker] = []
        self._filters: list[ComparisonFilter] = []

    def __call__(self) -> BinaryComparisonSpace:
        pass