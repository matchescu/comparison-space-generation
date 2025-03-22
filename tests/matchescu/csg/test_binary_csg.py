from unittest.mock import MagicMock, call

import pytest

from matchescu.blocking import Blocker, Block
from matchescu.comparison_filtering import ComparisonFilter
from matchescu.csg._binary_csg import BinaryComparisonSpaceGenerator
from matchescu.references import EntityReference
from matchescu.typing import EntityReferenceIdentifier


def _id(label, source):
    return EntityReferenceIdentifier(label, source)


def _ref(label, source):
    return EntityReference(_id(label, source), {"id": label})


@pytest.fixture
def csg():
    return BinaryComparisonSpaceGenerator()


def _new_blocker(blocker_no=1, blocks=None):
    mock = MagicMock(name=f"BlockerMock{blocker_no}", spec=Blocker)
    mock.return_value = blocks or []
    return mock


@pytest.fixture
def blocker():
    return _new_blocker()


def _new_filter(result):
    mock = MagicMock(name="ComparisonFilter", spec=ComparisonFilter)
    mock.return_value = result
    return mock


@pytest.fixture
def cmp_filter(request):
    return _new_filter(request.param if hasattr(request, "param") else False)


def test_add_blocker_uses_blocker(csg, blocker):
    csg.add_blocker(blocker)

    space = csg()

    assert len(space) == 0
    assert blocker.call_args_list == [call()]


@pytest.mark.parametrize(
    "block_refs,expected_ids",
    [
        ([_ref(1, "a"), _ref(2, "a")], [(_id(1, "a"), _id(2, "a"))]),
        (
            [_ref(1, "a"), _ref(2, "a"), _ref(3, "a")],
            [
                (_id(1, "a"), _id(2, "a")),
                (_id(1, "a"), _id(3, "a")),
                (_id(2, "a"), _id(3, "a")),
            ],
        ),
        (
            [_ref(1, "a"), _ref(1, "b"), _ref(2, "b")],
            [
                (_id(1, "a"), _id(1, "b")),
                (_id(1, "a"), _id(2, "b")),
            ],
        ),
    ],
)
def test_single_blocker_single_block(csg, blocker, block_refs, expected_ids):
    blocker.return_value = [Block("test-key").extend(block_refs)]
    csg.add_blocker(blocker)

    space = csg()

    assert list(space) == expected_ids


def test_single_blocker_multiple_blocks(csg, blocker):
    blocker.return_value = [
        Block("block1").extend([_ref(1, "a"), _ref(2, "a")]),
        Block("block2").extend([_ref(1, "b"), _ref(2, "b")]),
    ]
    csg.add_blocker(blocker)

    space = csg()

    assert len(space) == 2


def test_multiple_blockers(csg):
    blocker1 = _new_blocker(1, [Block("block1").extend([_ref(1, "a"), _ref(2, "a")])])
    blocker2 = _new_blocker(1, [Block("block2").extend([_ref(1, "b"), _ref(2, "b")])])
    csg.add_blocker(blocker1).add_blocker(blocker2)

    space = csg()

    assert blocker1.call_count == 1
    assert blocker2.call_count == 1
    assert len(space) == 2


@pytest.mark.parametrize(
    "cmp_filter,expected_len", [(True, 1), (False, 0)], indirect=["cmp_filter"]
)
def test_single_filter(csg, cmp_filter, expected_len):
    csg.add_blocker(
        _new_blocker(1, [Block("block1").extend([_ref(1, "a"), _ref(2, "a")])])
    )
    csg.add_filter(cmp_filter)

    space = csg()

    assert cmp_filter.call_count == 1
    assert len(space) == expected_len


@pytest.mark.parametrize(
    "filter1,filter2", [(True, False), (False, True), (False, False)]
)
def test_filters_act_cumulatively(csg, filter1, filter2):
    csg.add_blocker(
        _new_blocker(1, [Block("block1").extend([_ref(1, "a"), _ref(2, "a")])])
    )
    csg.add_filter(_new_filter(filter1))
    csg.add_filter(_new_filter(filter2))

    space = csg()

    assert len(space) == 0
