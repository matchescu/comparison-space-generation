import pytest

from matchescu.blocking._lsh import LSHBlocker


@pytest.fixture
def lsh_blocker(abt_buy_id_table):
    return LSHBlocker(abt_buy_id_table, threshold=0.3)


def test_abt_buy_blocking_no_data_loss(lsh_blocker, abt, buy):
    blocks = list(lsh_blocker())
    all_ids = set(identifier for block in blocks for identifier in block)
    assert len(all_ids) == len(abt) + len(buy)
