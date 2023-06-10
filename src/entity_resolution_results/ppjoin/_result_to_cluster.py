from abstractions.data_structures import Clustering, FeatureInfo


def _exclude_columns(row: list, excluded: set[int]) -> list:
    return [item for index, item in enumerate(row) if index not in excluded]


def _normalize_feature_info(info: list[list]) -> list[list]:
    result = []
    if info is None:
        return result
    for cluster in info:
        added_cluster = []
        for idx, feature in enumerate(cluster):
            added_feature = feature
            if not isinstance(feature, FeatureInfo):
                added_feature = FeatureInfo(name=str(feature), ordinal=idx)
            added_cluster.append(added_feature)
        result.append(added_cluster)
    return result


def ppjoin_result_to_cluster(
    results: list[tuple[list, list, float]],
    feature_info: list[list] = None,
) -> Clustering:
    return Clustering(
        feature_info=_normalize_feature_info(feature_info),
        clustered_rows=[
            [cluster_a, cluster_b]
            for cluster_a, cluster_b, _ in results
        ],
    )
