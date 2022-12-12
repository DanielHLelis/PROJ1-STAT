import scipy.stats as st
import numpy as np
from scipy.stats._discrete_distns import nbinom_gen


class tnbinom_gen(st.rv_discrete):
    """
    Slightly tweaked negative binomial to fit our problem.
    """

    def _pmf(self, k, n, s0, p):
        # Handle iterable
        if hasattr(k, '__iter__'):
            if len(k) != 1:
                return [self._pmf(j, n[i], s0[i], p[i]) for i, j in enumerate(k)]
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
                return [self._cdf(j, n[i], s0[i], p[i]) for i, j in enumerate(k)]
            else:
                k = k[0]
                n = n[0]
                s0 = s0[0]
                p = p[0]

        # Handle numeric case
        s = s0 + 1
        return st.nbinom.cdf(n * k - s, s, p)

    def _stats(self, n, s0, p):
        if hasattr(n, '__iter__'):
            if len(n) != 1:
                return [self._stats(j, s0[i], p[i]) for i, j in enumerate(n)]
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
