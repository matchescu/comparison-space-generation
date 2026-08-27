from pathlib import Path

import pytest
from matchescu.reference_store.comparison_space import InMemoryComparisonSpace
from matchescu.typing import EntityReferenceIdentifier as RefId

from matchescu.comparison_space.persistence._csv import (
    CsvComparisonSpaceFileParams,
    CsvPersistence,
)


@pytest.fixture
def csv_file(tmp_path: Path) -> Path:
    return tmp_path / "pairs.csv"


def test_write_then_read_preserves_pairs(csv_file: Path) -> None:
    cs = InMemoryComparisonSpace()
    cs.put(
        RefId(label="a1", source="src_left"),
        RefId(label="b1", source="src_right"),
    )
    cs.put(
        RefId(label="a2", source="src_left"),
        RefId(label="b2", source="src_right"),
    )

    persistence = CsvPersistence(csv_file)
    persistence.write(cs)

    params = CsvComparisonSpaceFileParams(
        has_header=True,
        left_id_column="left_id",
        left_source_column="left_source",
        right_id_column="right_id",
        right_source_column="right_source",
    )
    restored = persistence.read(params)

    original_pairs = {(x.label, x.source, y.label, y.source) for x, y in cs}
    restored_pairs = {(x.label, x.source, y.label, y.source) for x, y in restored}
    assert original_pairs == restored_pairs


def test_read_headerless_csv_with_default_params(csv_file: Path) -> None:
    csv_file.write_text("id1,id2\nid3,id4\n")

    persistence = CsvPersistence(csv_file)
    params = CsvComparisonSpaceFileParams(
        has_header=False,
        source_fallback="fallback",
    )
    cs = persistence.read(params)

    pairs = [(x.label, x.source, y.label, y.source) for x, y in cs]
    assert len(pairs) == 2
    assert ("id1", "fallback", "id2", "fallback") in pairs
    assert ("id3", "fallback", "id4", "fallback") in pairs


def test_read_empty_csv_returns_empty_space(csv_file: Path) -> None:
    csv_file.write_text("")

    persistence = CsvPersistence(csv_file)
    cs = persistence.read()

    assert list(cs) == []


def test_write_empty_comparison_space(csv_file: Path) -> None:
    cs = InMemoryComparisonSpace()

    persistence = CsvPersistence(csv_file)
    persistence.write(cs)

    content = csv_file.read_text()
    lines = [line for line in content.strip().splitlines() if line]
    assert len(lines) == 0
    assert content == "\n"


def test_written_csv_contains_expected_columns(csv_file: Path) -> None:
    cs = InMemoryComparisonSpace()
    cs.put(
        RefId(label="x", source="s1"),
        RefId(label="y", source="s2"),
    )

    persistence = CsvPersistence(csv_file)
    persistence.write(cs)

    import polars as pl

    df = pl.read_csv(csv_file)
    assert set(df.columns) == {"left_id", "left_source", "right_id", "right_source"}
    assert len(df) == 1
    row = df.row(0, named=True)
    assert row["left_id"] == "x"
    assert row["left_source"] == "s1"
    assert row["right_id"] == "y"
    assert row["right_source"] == "s2"
