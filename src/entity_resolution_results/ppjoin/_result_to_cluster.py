from abstractions.data_structures import Clustering


def ppjoin_result_to_cluster(results: list[tuple[list, list, float]]) -> Clustering:
    return Clustering.from_nested_lists([
            [cluster_a, cluster_b]
            for cluster_a, cluster_b, _ in results
        ],
    )
