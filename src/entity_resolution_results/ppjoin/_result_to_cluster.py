from abstractions.data_structures import Clustering


def _exclude_columns(row: tuple, excluded: set[int]) -> tuple:
    return tuple(item for index, item in enumerate(row) if index not in excluded)


def ppjoin_result_to_cluster(results: set[tuple[tuple, tuple, float]], exclude: list[int] = None) -> Clustering:
    exclude = exclude or [0]
    result = []
    for cluster_a, cluster_b, _ in results:
        x = _exclude_columns(cluster_a, set(exclude))
        y = _exclude_columns(cluster_b, set(exclude))
        result.append((x, y))
    return Clustering(
        feature_info=[],
        clustered_rows=result,
    )
