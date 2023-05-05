import pytest
import numpy as np
from tuben import tuben

def test_tuben_init():
    tub = tuben()
    assert tub.method == 'determinant'
    assert tub.maxnrformants == 4
    assert tub.fs == 16000
    assert tub.topfreq == 8000
    assert tub.c == 35300
    assert len(tub.F) == tub.topfreq - 1

def test_set_tube():
    tub = tuben()
    tub.set_tube([2, 2, 2, 2], [2, 2, 2, 2])
    assert tub.L == [2, 2, 2, 2]
    assert tub.A == [2, 2, 2, 2]
    assert not tub.updated

def test_get_formants():
    tub = tuben()
    L = [2, 6, 6, 2]
    A = [2, 5, 0.2, 2]
    fmt, Y = tub.get_formants(L, A)
    assert len(fmt) == tub.maxnrformants
    assert len(Y) == tub.topfreq - 1
    assert isinstance(fmt, np.ndarray)
    assert isinstance(Y, np.ndarray)

def test_wormfrek_det_vec():
    tub = tuben(method='determinant')
    L = [0, 2, 6, 6, 2]
    A = [1, 2, 5, 0.2, 2]
    Y = tub._wormfrek_det_vec(L, A)
    assert len(Y) == tub.topfreq - 1
    assert isinstance(Y, np.ndarray)

def test_wormfrek_phase_vec():
    tub = tuben(method='phase')
    L = [0, 2, 6, 6, 2]
    A = [1, 2, 5, 0.2, 2]
    Y = tub._wormfrek_phase_vec(L, A)
    assert len(Y) == tub.topfreq - 1
    assert isinstance(Y, np.ndarray)

@pytest.mark.parametrize("L,A", [
    ([2, 6, 6, 2], [2, 5, 0.2, 2]),
    ([4, 4, 4, 4], [2, 2, 2, 2]),
])
def test_formant_frequencies(L, A):
    tub = tuben()
    fmt, Y = tub.get_formants(L, A)
    assert len(fmt) == tub.maxnrformants
    assert len(Y) == tub.topfreq - 1
    assert isinstance(fmt, np.ndarray)
    assert isinstance(Y, np.ndarray)
    for f in fmt:
        assert f > 0
