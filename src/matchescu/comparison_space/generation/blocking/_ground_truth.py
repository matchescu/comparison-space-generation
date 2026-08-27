from collections.abc import Generator, Iterable
from random import shuffle

from matchescu.reference_store.id_table import IdTable
from matchescu.typing import EntityReferenceIdentifier as RefId

from matchescu.comparison_space.generation.blocking import Block, Blocker


class GroundTruthBlocker(Blocker):
    def __init__(
        self,
        id_table: IdTable,
        ground_truth: Iterable[tuple[RefId, RefId]],
        neg_pos_ratio: float = 8.0,
        max_count: int | None = None,
    ) -> None:
        super().__init__(id_table)
        self._ground_truth = set(ground_truth)
        self._neg_pos_ratio = neg_pos_ratio
        self._max_count = (
            max_count
            if max_count is not None
            else int(len(self._ground_truth) * (1 + self._neg_pos_ratio))
        )

    def _is_true_match(self, x: RefId, y: RefId) -> bool:
        return (x, y) in self._ground_truth or (y, x) in self._ground_truth

    def _get_by_source(self, src: str) -> Generator[RefId, None, None]:
        source_refs = list(self._id_table.get_by_source(src))
        shuffle(source_refs)
        yield from (x.id for x in source_refs)

    def __call__(self) -> Generator[Block, None, None]:
        total_pairs = 0
        per_source_refs = {}
        max_pairs = self._max_count

        def _add_negs(
            blk: Block, x: RefId, compl: RefId, budget: int, n_other: int
        ) -> tuple[int, int]:
            nonlocal total_pairs
            nonlocal per_source_refs

            ret_refs, ret_pairs = 0, n_other
            # lazily cache ref IDs per source
            per_source_refs[x.source] = per_source_refs.get(
                x.source, list(self._get_by_source(x.source))
            )
            for rid in per_source_refs[x.source]:
                if total_pairs >= max_pairs:
                    break
                if rid == x or self._is_true_match(rid, compl):
                    continue
                blk.append(rid)
                ret_refs += 1
                ret_pairs += n_other
                total_pairs += n_other
                if ret_pairs >= budget:
                    break
            return ret_refs, ret_pairs

        for a, b in self._ground_truth:
            if total_pairs >= max_pairs:
                break

            remaining_slots = max_pairs - total_pairs
            if remaining_slots < 1:
                break

            max_negatives = min(int(self._neg_pos_ratio), remaining_slots - 1)
            if max_negatives < 0:
                continue

            # ref IDs from a.source are required in both paths - lazily cache it
            per_source_refs[a.source] = per_source_refs.get(
                a.source, list(self._get_by_source(a.source))
            )
            block = Block(key=(a, b))
            block.append(a).append(b)
            total_pairs += 1

            if a.source != b.source:
                a_refs, a_pairs = _add_negs(block, a, b, max_negatives // 2, 1)
                _add_negs(block, b, a, max_negatives - a_pairs, 1 + a_refs)
            else:
                # a and b are in the current block
                current_size = 2
                added_pairs = 0
                for ref_id in per_source_refs[a.source]:
                    if added_pairs > max_negatives or total_pairs >= max_pairs:
                        break
                    if (
                        ref_id in (a, b)
                        or self._is_true_match(ref_id, a)
                        or self._is_true_match(ref_id, b)
                    ):
                        continue

                    new_pairs = current_size
                    if added_pairs + new_pairs > max_negatives:
                        break

                    block.append(ref_id)
                    added_pairs += new_pairs
                    total_pairs += new_pairs
                    current_size += 1

            yield block
