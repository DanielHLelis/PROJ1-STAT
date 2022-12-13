import scipy.stats as st
import numpy as np
from scipy.stats._discrete_distns import nbinom_gen

from typing import List, Union


def _try_get(it: Union[List[Union[int, float]], int, float], idx: int):
    if hasattr(it, '__len__'):
        if idx < len(it):
            return it[idx]
        return it[0]
    return it


class tnbinom_gen(st.rv_discrete):
    """
    Slightly tweaked negative binomial to fit our problem.
    """

    def _pmf(self, k, n, s0, p):
        # Handle iterable
        if hasattr(k, '__iter__'):
            if len(k) != 1:
                return [self._pmf(j, _try_get(n, i), _try_get(s0, i), _try_get(p, i)) for i, j in enumerate(k)]
            else:
                k = k[0]
                n = n[0]
                s0 = s0[0]
                p = p[0]

        # Handle numeric case
        s = s0 + 1
        return sum(st.nbinom.pmf(np.arange(n * (k - 1) + 1, n * k + 1) - s, s, p))

    def _cdf(self, k, n, s0, p):
        # Handle iterable
        if hasattr(k, '__iter__'):
            if len(k) != 1:
                return [self._cdf(j, _try_get(n, i), _try_get(s0, i), _try_get(p, i)) for i, j in enumerate(k)]
            else:
                k = k[0]
                n = n[0]
                s0 = s0[0]
                p = p[0]

        # Handle numeric case
        s = s0 + 1
        return st.nbinom.cdf(n * k - s, s, p)

    def _ppf(self, q, n, s0, p):
        if hasattr(q, '__iter__'):
            if len(q) != 1:
                return [self._ppf(j, _try_get(n, i), _try_get(s0, i), _try_get(p, i)) for i, j in enumerate(q)]
            else:
                q = q[0]
                n = n[0]
                s0 = s0[0]
                p = p[0]

        # Handle numeric case
        s = s0 + 1
        return (st.nbinom.ppf(q, s, p) + s) / n

    def _stats(self, n, s0, p):
        if hasattr(n, '__iter__'):
            if len(n) != 1:
                return [self._stats(j, _try_get(s0, i), _try_get(p, i)) for i, j in enumerate(n)]
            else:
                n = n[0]
                s0 = s0[0]
                p = p[0]

        # Handle numeric case
        mean = st.nbinom.stats(s0 + 1, p)[0]

        mean += (s0 + 1)
        mean /= n

        # Not sure about variance
        return mean, mean / p, None, None


tnbinom = tnbinom_gen(name='tnbinom')


class WrappedPPF:
    """Wrapped PPF function used for Q-Q Plot (runs faster, same result)"""

    def __init__(self, n, s, p):
        self.n = n
        self.s = s + 1
        self.p = p

    def ppf(self, q):
        return (st.nbinom.ppf(q, self.s, self.p) + self.s) / self.n
