import csv
from functools import partial
from pathlib import Path

import pytest

from matchescu.data_sources import CsvDataSource
from matchescu.extraction import (
    Traits,
    RecordExtraction,
    single_record,
)
from matchescu.reference_store.id_table._in_memory import InMemoryIdTable
from matchescu.typing import Record, DataSource, EntityReferenceIdentifier


@pytest.fixture(scope="session")
def data_dir():
    return Path(__file__).parent / "data"


@pytest.fixture
def abt_traits():
    return list(Traits().int([0]).string([1, 2]).currency([3]))


@pytest.fixture
def buy_traits():
    return list(Traits().int([0]).string([1, 2, 3]).currency([4]))


@pytest.fixture
def abt(data_dir, abt_traits) -> DataSource[Record]:
    return CsvDataSource(data_dir / "abt-buy" / "Abt.csv", abt_traits).read()


@pytest.fixture
def buy(data_dir, buy_traits) -> DataSource[Record]:
    return CsvDataSource(data_dir / "abt-buy" / "Buy.csv", buy_traits).read()


@pytest.fixture
def abt_buy_gt(
    data_dir, abt, buy
) -> set[tuple[EntityReferenceIdentifier, EntityReferenceIdentifier]]:
    with open(data_dir / "abt-buy" / "abt_buy_perfectMapping.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)
        ids = [tuple(map(int, values)) for values in reader]
    return set(
        (
            EntityReferenceIdentifier(abt_id, abt.name),
            EntityReferenceIdentifier(buy_id, buy.name),
        )
        for abt_id, buy_id in ids
    )


@pytest.fixture
def id_factory():
    return lambda rows, source: EntityReferenceIdentifier(rows[0][0], source)


@pytest.fixture
def abt_buy_id_table(abt, buy, id_factory):
    result = InMemoryIdTable()
    for source in [abt, buy]:
        refextract = RecordExtraction(
            source, partial(id_factory, source=source.name), single_record
        )
        for ref in refextract():
            result.put(ref)
    return result
