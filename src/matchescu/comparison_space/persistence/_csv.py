from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path

import polars as pl
from matchescu.reference_store.comparison_space import (
    BinaryComparisonSpace,
    InMemoryComparisonSpace,
)
from matchescu.typing import EntityReferenceIdentifier as RefId
from polars.exceptions import NoDataError

from ._base import ComparisonSpaceReader, ComparisonSpaceWriter


@dataclass(frozen=True)
class CsvComparisonSpaceFileParams:
    has_header: bool = field(default=False)
    source_fallback: str = field(default="default")
    left_id_column: str | int = field(default=0)
    left_source_column: str | int | None = field(default=None)
    right_id_column: str | int = field(default=1)
    right_source_column: str | int | None = field(default=None)


class CsvPersistence(ComparisonSpaceReader, ComparisonSpaceWriter):
    def __init__(self, file: str | PathLike) -> None:
        self._path = Path(file)

    def read(
        self, params: CsvComparisonSpaceFileParams | None = None
    ) -> BinaryComparisonSpace:
        params = params or CsvComparisonSpaceFileParams()
        cs = InMemoryComparisonSpace()
        try:
            df = pl.read_csv(
                self._path, has_header=params.has_header, ignore_errors=True
            )
        except NoDataError:
            return cs
        col_map = {col: idx for idx, col in enumerate(df.columns)}
        left_id_idx = col_map.get(params.left_id_column, params.left_id_column)
        left_source_idx = col_map.get(
            params.left_source_column, params.left_source_column
        )
        right_id_idx = col_map.get(params.right_id_column, params.right_id_column)
        right_source_idx = col_map.get(
            params.right_source_column, params.right_source_column
        )
        for row in df.iter_rows(named=False):
            left_id = RefId(
                label=row[left_id_idx],
                source=str(
                    row[left_source_idx] if left_source_idx else params.source_fallback
                ),
            )
            right_id = RefId(
                label=row[right_id_idx],
                source=str(
                    row[right_source_idx]
                    if right_source_idx
                    else params.source_fallback
                ),
            )
            cs.put(left_id, right_id)
        return cs

    def write(self, comparison_space: BinaryComparisonSpace) -> None:
        df = pl.DataFrame(
            [
                {
                    "left_id": left.label,
                    "left_source": str(left.source),
                    "right_id": right.label,
                    "right_source": str(right.source),
                }
                for left, right in comparison_space
            ]
        )
        df.write_csv(self._path, include_header=True)
