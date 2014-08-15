from critical_difference.plot import merge_nonsignificant_cliques
from random import shuffle


def test_merge_cliques():
    # these should not be merged
    insignificant = [(0, 1), (1, 2)]
    assert merge_nonsignificant_cliques(insignificant) == insignificant

    # these are all together
    insignificant = [(0, 1), (1, 2), (0, 2)]
    for i in range(20):
        shuffle(insignificant)
        assert merge_nonsignificant_cliques(insignificant) == [(0, 2)]