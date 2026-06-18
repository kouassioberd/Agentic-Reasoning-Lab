from eval.metrics import numeric_exact_match, wilson_interval


def test_numeric_exact_match_accepts_equivalent_numbers():
    assert numeric_exact_match("13.0", "13")


def test_numeric_exact_match_rejects_wrong_numbers():
    assert not numeric_exact_match("12", "13")


def test_wilson_interval_bounds():
    low, high = wilson_interval(30, 30)
    assert 0 <= low <= high <= 1

