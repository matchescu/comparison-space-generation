from collections.abc import Iterable
from typing import Generator, cast

from datasketch import MinHash, MinHashLSH

from matchescu.blocking import Block
from matchescu.blocking._blocker import Blocker
from matchescu.blocking._tokenization import tokenize_reference
from matchescu.reference_store.id_table import IdTable
from matchescu.typing import EntityReference, EntityReferenceIdentifier


class LSHBlocker(Blocker):
    def __init__(
        self,
        id_table: IdTable,
        threshold: float = 0.5,
        num_perm: int = 128,
        bands: int = 16,
    ):
        super().__init__(id_table)
        self.__sim_threshold = threshold  # Similarity threshold for LSH
        self.__num_perm = num_perm  # Number of permutations for MinHash
        self.__num_bands = bands  # Number of bands for LSH bucketing
        self.__lsh = MinHashLSH(
            threshold=self.__sim_threshold, num_perm=self.__num_perm
        )

    def __compute_minhash(self, tokens: Iterable[str]) -> MinHash:
        """Compute MinHash signature for a set of tokens."""
        m = MinHash(num_perm=self.__num_perm)
        m.update_batch(map(lambda t: t.encode("utf-8"), tokens))
        return m

    def __add_entity(self, ref: EntityReference) -> None:
        """Add an entity with tokenized attributes to LSH."""
        minhash = self.__compute_minhash(tokenize_reference(ref))
        self.__lsh.insert(ref.id, minhash)

    def __call__(self) -> Generator[Block, None, None]:
        for ref in self._id_table:
            self.__add_entity(ref)

        for ref in self._id_table:
            block_key = self.__compute_minhash(tokenize_reference(ref))
            neighbor_ids = self.__lsh.query(block_key)
            yield Block(key=block_key).extend(
                cast(EntityReferenceIdentifier, x) for x in neighbor_ids
            )
