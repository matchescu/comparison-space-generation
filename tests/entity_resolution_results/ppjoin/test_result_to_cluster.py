from entity_resolution_results.ppjoin import transform_result


def test_cluster_from_empty_results():
    clustering = transform_result([])

    assert len(clustering.clustered_rows) == 0
    assert len(clustering.feature_info) == 0


def test_basic_clustering_from_single_result():
    clustering = transform_result([(["a", "b"], ["a", "c"], 0.25)])

    assert len(clustering.feature_info) == 0
    assert len(clustering.clustered_rows) == 1
    assert clustering.clustered_rows == [
        [["a", "b"], ["a", "c"]]
    ]


def test_basic_clustering_from_single_result_with_custom_feature_info():
    clustering = transform_result(
        [(["a", "b"], ["a", "c"], 0.25)],
        feature_info=[["id", "value"], ["id", "size"]]
    )

    assert len(clustering.feature_info) == 2
    actual_feature_info = list(
        tuple(item.name for item in cluster)
        for cluster in clustering.feature_info
    )
    assert actual_feature_info == [("id", "value"), ("id", "size")]
    assert len(clustering.clustered_rows) == 1
    assert clustering.clustered_rows == [
        [["a", "b"], ["a", "c"]]
    ]
