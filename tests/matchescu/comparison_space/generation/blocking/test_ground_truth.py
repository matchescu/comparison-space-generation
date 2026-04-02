from typing import cast
from unittest.mock import MagicMock

import pytest

from matchescu.comparison_space.generation.blocking import Block
from matchescu.reference_store.id_table import IdTable
from matchescu.typing import EntityReferenceIdentifier as RefId

from matchescu.comparison_space.generation.blocking._ground_truth import (
    GroundTruthBlocker,
)


def _ref(source: str, key: int) -> RefId:
    return RefId(source=source, label=key)


def _make_entity_ref(ref_id: RefId):
    stub = MagicMock()
    stub.id = ref_id
    return stub


def _make_id_table(ref_ids: list[RefId]) -> IdTable:
    by_source: dict[str, list] = {}
    for rid in ref_ids:
        by_source.setdefault(rid.source, []).append(_make_entity_ref(rid))

    table = MagicMock(spec=IdTable)
    table.get_by_source.side_effect = lambda src: by_source.get(src, [])
    return cast(IdTable, cast(object, table))


def _collect_all_pairs(blocks: list[Block]) -> list[tuple[RefId, RefId]]:
    pairs = []
    for block in blocks:
        pairs.extend(block.candidate_pairs())
    return pairs


def _count_positives(pairs, ground_truth: set) -> int:
    return sum(1 for a, b in pairs if (a, b) in ground_truth or (b, a) in ground_truth)


def _count_negatives(pairs, ground_truth: set) -> int:
    return sum(
        1 for a, b in pairs if (a, b) not in ground_truth and (b, a) not in ground_truth
    )


@pytest.fixture
def two_source_refs():
    a_refs = [_ref("A", i) for i in range(10)]
    b_refs = [_ref("B", i) for i in range(10)]
    return a_refs, b_refs


@pytest.fixture
def single_source_refs():
    return [_ref("A", i) for i in range(20)]


def test_every_positive_pair_appears_in_a_block(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[0], b_refs[0]), (a_refs[1], b_refs[1])}
    all_refs = a_refs + b_refs
    table = _make_id_table(all_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=4.0)
    blocks = list(blocker())

    all_pairs = _collect_all_pairs(blocks)
    for a, b in gt:
        assert any(
            (a, b) == (x, y) or (b, a) == (x, y) for x, y in all_pairs
        ), f"Positive pair ({a}, {b}) not found in any block"


def test_blocks_contain_both_positive_refs(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[0], b_refs[0])}
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=4.0)
    blocks = list(blocker())

    assert len(blocks) == 1
    block = blocks[0]
    assert a_refs[0] in block.ref_ids
    assert b_refs[0] in block.ref_ids


def test_single_source_positive_pair_in_block(single_source_refs):
    refs = single_source_refs
    gt = {(refs[0], refs[1])}
    table = _make_id_table(refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=4.0)
    blocks = list(blocker())

    assert len(blocks) == 1
    assert refs[0] in blocks[0].ref_ids
    assert refs[1] in blocks[0].ref_ids


def test_total_pairs_do_not_exceed_max_count(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[i], b_refs[i]) for i in range(5)}
    table = _make_id_table(a_refs + b_refs)

    max_count = 10
    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=4.0, max_count=max_count)
    blocks = list(blocker())
    all_pairs = _collect_all_pairs(blocks)

    assert len(all_pairs) <= max_count


def test_default_max_count_formula(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[0], b_refs[0]), (a_refs[1], b_refs[1])}
    table = _make_id_table(a_refs + b_refs)

    ratio = 6.0
    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=ratio)
    expected_max = int(len(gt) * (1 + ratio))
    assert blocker._max_count == expected_max


def test_neg_pos_ratio_approximately_respected(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[0], b_refs[0])}
    table = _make_id_table(a_refs + b_refs)

    ratio = 6.0
    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=ratio)
    blocks = list(blocker())
    all_pairs = _collect_all_pairs(blocks)

    positives = _count_positives(all_pairs, gt)
    negatives = _count_negatives(all_pairs, gt)

    assert positives >= 1
    assert negatives <= int(ratio) * positives


def test_max_count_of_one_yields_only_positive(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[0], b_refs[0])}
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=8.0, max_count=1)
    blocks = list(blocker())

    all_pairs = _collect_all_pairs(blocks)
    assert len(all_pairs) == 1
    assert _count_positives(all_pairs, gt) == 1


def test_empty_ground_truth(two_source_refs):
    a_refs, b_refs = two_source_refs
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, [], neg_pos_ratio=4.0)
    blocks = list(blocker())
    assert blocks == []


def test_ground_truth_exhausts_source():
    """All refs in a source are true matches — no negatives available."""
    a_refs = [_ref("A", 0)]
    b_refs = [_ref("B", 0)]
    gt = {(a_refs[0], b_refs[0])}
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=8.0)
    blocks = list(blocker())

    assert len(blocks) == 1
    all_pairs = _collect_all_pairs(blocks)
    # Only the positive pair, no negatives possible
    assert len(all_pairs) == 1
    assert _count_positives(all_pairs, gt) == 1


def test_zero_neg_pos_ratio(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[0], b_refs[0])}
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=0.0)
    blocks = list(blocker())

    all_pairs = _collect_all_pairs(blocks)
    assert _count_negatives(all_pairs, gt) == 0
    assert _count_positives(all_pairs, gt) == 1


def test_max_count_zero_yields_nothing(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[0], b_refs[0])}
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=4.0, max_count=0)
    blocks = list(blocker())

    assert len(blocks) == 0


def test_overlapping_ground_truth_refs():
    """One ref appears in multiple GT pairs."""
    a0, a1 = _ref("A", 0), _ref("A", 1)
    b0 = _ref("B", 0)
    # a0 matches b0, a1 also matches b0
    gt = {(a0, b0), (a1, b0)}
    others = [_ref("A", i) for i in range(2, 8)]
    table = _make_id_table([a0, a1] + others + [b0])

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=4.0)
    blocks = list(blocker())

    # Both positive pairs must appear
    all_pairs = _collect_all_pairs(blocks)
    positives = _count_positives(all_pairs, gt)
    assert positives >= 2


def test_block_key_is_positive_pair(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[0], b_refs[0])}
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=4.0)
    blocks = list(blocker())

    assert len(blocks) == 1
    assert blocks[0].key == (a_refs[0], b_refs[0])


def test_cross_source_block_has_multiple_sources(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[0], b_refs[0])}
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=4.0)
    blocks = list(blocker())

    assert blocks[0].count_sources() == 2


def test_single_source_block_has_one_source(single_source_refs):
    refs = single_source_refs
    gt = {(refs[0], refs[1])}
    table = _make_id_table(refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=4.0)
    blocks = list(blocker())

    assert blocks[0].count_sources() == 1


def test_negatives_come_from_both_sources(two_source_refs):
    a_refs, b_refs = two_source_refs
    gt = {(a_refs[0], b_refs[0])}
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=8.0)
    blocks = list(blocker())

    block = blocks[0]
    a_side = [r for r in block.ref_ids if r.source == "A"]
    b_side = [r for r in block.ref_ids if r.source == "B"]

    # Both sides should have more than just the positive ref
    assert len(a_side) > 1, "Expected negative refs from source A"
    assert len(b_side) > 1, "Expected negative refs from source B"


def test_generator_exhaustion_across_blocks():
    a_refs = [_ref("A", i) for i in range(5)]
    b_refs = [_ref("B", i) for i in range(5)]
    gt = {(a_refs[i], b_refs[i]) for i in range(4)}
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=8.0)
    blocks = list(blocker())

    all_pairs = _collect_all_pairs(blocks)
    positives = _count_positives(all_pairs, gt)
    assert positives >= 1


def test_later_blocks_may_have_fewer_negatives():
    a_refs = [_ref("A", i) for i in range(3)]
    b_refs = [_ref("B", i) for i in range(3)]
    gt = {(a_refs[0], b_refs[0]), (a_refs[1], b_refs[1]), (a_refs[2], b_refs[2])}
    table = _make_id_table(a_refs + b_refs)

    blocker = GroundTruthBlocker(table, gt, neg_pos_ratio=8.0)
    blocks = list(blocker())

    # First block gets negatives, later blocks may not
    block_sizes = [len(b.ref_ids) for b in blocks]
    assert all(size >= 2 for size in block_sizes)


def test_all_gt_pairs_covered(abt_buy_id_table, abt_buy_gt):
    blocker = GroundTruthBlocker(abt_buy_id_table, abt_buy_gt, neg_pos_ratio=8.0)
    blocks = list(blocker())
    all_pairs = _collect_all_pairs(blocks)
    gt_set = set(abt_buy_gt)

    covered = set()
    for x, y in all_pairs:
        if (x, y) in gt_set:
            covered.add((x, y))
        elif (y, x) in gt_set:
            covered.add((y, x))

    # Every GT pair should appear in at least one block
    missing = gt_set - covered
    assert (
        len(missing) == 0
    ), f"{len(missing)} ground truth pairs not covered by any block"


def test_total_pairs_within_max_count(abt_buy_id_table, abt_buy_gt):
    ratio = 8.0
    blocker = GroundTruthBlocker(abt_buy_id_table, abt_buy_gt, neg_pos_ratio=ratio)

    blocks = list(blocker())

    all_pairs = _collect_all_pairs(blocks)
    assert len(all_pairs) <= blocker._max_count


def test_ratio_is_approximately_correct(abt_buy_id_table, abt_buy_gt):
    ratio = 8.0
    gt_set = set(abt_buy_gt)
    blocker = GroundTruthBlocker(abt_buy_id_table, abt_buy_gt, neg_pos_ratio=ratio)
    blocks = list(blocker())
    all_pairs = _collect_all_pairs(blocks)

    positives = _count_positives(all_pairs, gt_set)
    negatives = _count_negatives(all_pairs, gt_set)

    if positives > 0:
        actual_ratio = negatives / positives
        # Allow some tolerance due to generator exhaustion and rounding
        assert (
            actual_ratio <= ratio + 1.0
        ), f"Actual ratio {actual_ratio:.2f} exceeds target {ratio}"


def test_performance_blocks_generated_in_reasonable_time(abt_buy_id_table, abt_buy_gt):
    import time

    blocker = GroundTruthBlocker(abt_buy_id_table, abt_buy_gt, neg_pos_ratio=8.0)

    start = time.perf_counter()
    blocks = list(blocker())
    elapsed = time.perf_counter() - start

    # abt-buy has ~1000 GT pairs; this should complete in under 10s
    assert elapsed < 10.0, f"Blocking took {elapsed:.2f}s — too slow"
    assert len(blocks) > 0


def test_determinism_with_seed(abt_buy_id_table, abt_buy_gt):
    import random

    random.seed(42)
    blocker1 = GroundTruthBlocker(abt_buy_id_table, list(abt_buy_gt), neg_pos_ratio=4.0)
    blocks1 = list(blocker1())

    random.seed(42)
    blocker2 = GroundTruthBlocker(abt_buy_id_table, list(abt_buy_gt), neg_pos_ratio=4.0)
    blocks2 = list(blocker2())

    # With same seed and list (ordered) input, blocks should match
    assert len(blocks1) == len(blocks2)
    for b1, b2 in zip(blocks1, blocks2):
        assert b1.key == b2.key
        assert b1.ref_ids == b2.ref_ids
