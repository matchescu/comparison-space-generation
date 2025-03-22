from matchescu.blocking import Blocker
from matchescu.comparison_filtering import ComparisonFilter


class BinaryComparisonSpaceGenerator:
    def __init__(self):
        self._blockers: list[Blocker] = []
        self._filters: list[ComparisonFilter] = []
