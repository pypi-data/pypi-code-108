from fcapsy_experiments.typicality.top_k_similarity import k_values_or_until_differs


def test_k_values_or_until_differs1():
    l1 = [1, 2, 3, 4, 4, 4, 4, 5, 6, 7]

    assert list(k_values_or_until_differs(l1, k=3)) == [1, 2, 3]


def test_k_values_or_until_differs2():
    l1 = [1, 2, 3, 4, 4, 4, 4, 5, 6, 7]

    assert list(k_values_or_until_differs(l1, k=4)) == [1, 2, 3, 4, 4, 4, 4]


def test_k_values_or_until_differs3():
    l1 = [1, 2, 3, 4, 4, 4, 4, 5, 6, 7]

    assert list(k_values_or_until_differs(l1, k=1)) == [1]


def test_k_values_or_until_differs4():
    l1 = [1, 2, 3, 4, 4, 4, 4, 5, 6, 7]

    assert list(k_values_or_until_differs(l1, k=0)) == []


def test_k_values_or_until_differs5():
    l1 = [1, 2, 3, 4, 4, 4, 4, 5, 6, 7]

    assert list(k_values_or_until_differs(l1, k=1000)) == l1
