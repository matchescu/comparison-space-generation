from abstractions.data_structures import Clustering, FeatureInfo


def _exclude_columns(row: tuple, excluded: set[int]) -> tuple:
    return tuple(item for index, item in enumerate(row) if index not in excluded)


def _normalize_feature_info(info: list[tuple]) -> list[tuple]:
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
        result.append(tuple(added_cluster))
    return result


def ppjoin_result_to_cluster(
    results: set[tuple[tuple, tuple, float]],
    feature_info: list[tuple] = None,
    exclude: list[int] = None
) -> Clustering:
    exclude = exclude or [0]
    result = []
    for cluster_a, cluster_b, _ in results:
        x = _exclude_columns(cluster_a, set(exclude))
        y = _exclude_columns(cluster_b, set(exclude))
        result.append((x, y))
    return Clustering(
        feature_info=_normalize_feature_info(feature_info),
        clustered_rows=result,
    )
