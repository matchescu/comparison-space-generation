from entity_resolution_results.ppjoin import transform_result


def test_cluster_from_empty_results():
    clustering = transform_result(set())

    assert len(clustering.clustered_rows) == 0
    assert len(clustering.feature_info) == 0


def test_cluster_from_single_result_without_feature_info():
    clustering = transform_result({((0, "a", "b"), (1, "a", "c"), 0.25)})

    assert len(clustering.feature_info) == 0
    assert len(clustering.clustered_rows) == 1
    assert clustering.clustered_rows == [
        (("a", "b"), ("a", "c"))
    ]
