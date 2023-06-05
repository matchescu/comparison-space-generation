from entity_resolution_results.ppjoin import transform_result


def test_cluster_from_empty_results():
    clustering = transform_result(set())

    assert len(clustering.clustered_rows) == 0
    assert len(clustering.feature_info) == 0


def test_basic_clustering_from_single_result():
    clustering = transform_result({((0, "a", "b"), (1, "a", "c"), 0.25)})

    assert len(clustering.feature_info) == 0
    assert len(clustering.clustered_rows) == 1
    assert clustering.clustered_rows == [
        (("a", "b"), ("a", "c"))
    ]


def test_basic_clustering_from_single_result_with_custom_exclusion_list():
    clustering = transform_result({((0, "a", "b"), (1, "a", "c"), 0.25)}, exclude=[1])

    assert len(clustering.feature_info) == 0
    assert len(clustering.clustered_rows) == 1
    assert clustering.clustered_rows == [
        ((0, "b"), (1, "c"))
    ]
