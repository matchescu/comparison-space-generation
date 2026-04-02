from abc import abstractmethod
from typing import Protocol

from matchescu.reference_store.comparison_space import BinaryComparisonSpace


class ComparisonSpaceReader(Protocol):
    @abstractmethod
    def read(self) -> BinaryComparisonSpace:
        raise NotImplementedError


class ComparisonSpaceWriter(Protocol):
    @abstractmethod
    def write(self, comparison_space: BinaryComparisonSpace) -> None:
        raise NotImplementedError
