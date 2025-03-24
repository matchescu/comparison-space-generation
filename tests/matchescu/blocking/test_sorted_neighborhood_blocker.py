import pytest

from matchescu.blocking._sorted_neighborhood import SortedNeighborhoodBlocker


@pytest.fixture
def sn_blocker(abt_buy_id_table):
    return SortedNeighborhoodBlocker(abt_buy_id_table, window_size=4)


def test_abt_buy_blocking_no_data_loss(sn_blocker, abt, buy):
    blocks = list(sn_blocker())
    all_ids = set(identifier for block in blocks for identifier in block)
    assert len(all_ids) == len(abt) + len(buy)
