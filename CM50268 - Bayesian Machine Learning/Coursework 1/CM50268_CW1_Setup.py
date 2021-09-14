#
# CM50268_CW1_Setup
#
# Support code for Coursework 1 :: Bayesian Linear Regression
#
import numpy as np
from scipy import stats, spatial


class DataGenerator:

    """Generate data for simple prediction modelling
    - this is a sine wave with a blank region"""

    def __init__(self, noise=0.25, rs=4):
        # Ensure different random seeds for the data sets
        self._States = {'TRAIN': 0+rs, 'VALIDATION': 1+rs, 'TEST': 2+rs}
        #
        self.xmin = 0
        self.xmax = 2.5 * np.pi
        self._noise_std = noise

    # Private
    # 
    def _make_data_test(self, name, N, noise_std=0.0):
        # The full sine wave
        x = np.linspace(self.xmin, self.xmax, N).reshape((N, 1))
        t = np.sin(x)
        if noise_std:
            state = self._States[name]
            t += stats.norm.rvs(size=(N, 1), scale=noise_std,
                                random_state=state)
        #
        return x, t

    def _make_data(self, name, N, noiseStd=0.0):
        # Portions of the sine wave
        start = [0.25*np.pi, 6]
        width = [0.6*np.pi, 0.4*np.pi]
        K = len(start)
        Nper = int(N/K)
        x = np.empty(0)
        for k in range(K):
            xk = np.linspace(start[k], start[k]+width[k], Nper)
            x = np.append(x, xk)
        x = x.reshape((N, 1))
        t = np.sin(x)
        if noiseStd:
            state = self._States[name]
            t += stats.norm.rvs(size=(N, 1), scale=noiseStd,
                                random_state=state)
        #
        return x, t

    # Public interface
    # 
    def get_data(self, name, N):
        name = name.upper()
        if name == 'TRAIN':
            return self._make_data(name, N, self._noise_std)
        elif name == 'VALIDATION':
            return self._make_data(name, N, self._noise_std)
        elif name == 'TEST':
            return self._make_data_test(name, N, 0)
        else:
            raise ValueError('Invalid data set name')


class RBFGenerator:

    """Generate Gaussian RBF basis matrices"""

    def __init__(self, Centres, width=1, bias=False):
        self._r = width
        self._M = len(Centres)
        self._Cent = Centres.reshape((self._M, 1))
        self._bias = bias
        if bias:
            self._M += 1

    def evaluate(self, X):
        N = len(X)
        PHI = np.exp(-spatial.distance.cdist(X, self._Cent, metric="sqeuclidean")
                     / (self._r**2))
        if self._bias:
            PHI = np.hstack((np.ones((N, 1)), PHI))
        #
        return PHI


def error_rms(t, y):
    """Compute RMS error for a prediction vector"""
    err = np.sqrt(np.mean((y - t) ** 2))
    return err
