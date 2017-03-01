"""
    biclustlib: A Python library of biclustering algorithms and evaluation measures.
    Copyright (C) 2017  Victor Alexandre Padilha

    This file is part of biclustlib.

    biclustlib is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    biclustlib is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from ._base import BaseBiclusteringAlgorithm
from ..models import Bicluster, Biclustering
from sklearn.preprocessing import scale
from scipy.stats import norm
from operator import itemgetter

import bottleneck as bn
import numpy as np

class LargeAverageSubmatrices(BaseBiclusteringAlgorithm):
    """Large Average Submatrices (LAS)

    LAS searches for submatrices by optimizing a significance score that trades off between
    submatrix size and average value.

    Reference
    ----------
    Shabalin, A. A., Weigman, V. J., Perou, C. M., and Nobel, A. B. (2009). Finding large
    average submatrices in high dimensional data. The Annals of Applied Statistics, 3(3):
    985-1012.

    Parameters
    ----------
    num_biclusters : int, default: 10
        Number of biclusters to be found.

    score_threshold : float, default: 1.0
        Significance score threshold.

    randomized_searches : int, default: 1000
        Number of executions of the search procedure for each bicluster.

    transform : bool, default: False
        If True, applies the transformation f(x) = sign(x) * log(1 + |x|) to each entry of the
        input dataset before performing the algorithm (recommended by the original authors for
        datasets that exhibit heavy tails).
    """

    def __init__(self, num_biclusters=10, score_threshold=1.0, randomized_searches=1000, transform=False):
        self.num_biclusters = num_biclusters
        self.score_threshold = score_threshold
        self.randomized_searches = randomized_searches
        self.transform = transform

    def run(self, data):
        """Compute biclustering.

        Parameters
        ----------
        data : numpy.ndarray
        """
        self._validate_parameters()

        data = scale(data)

        if self.transform:
            data = np.sign(data) * np.log(1 + np.abs(data))
            data = scale(data)

        biclusters = []

        for i in range(self.num_biclusters):
            best, avg, score = max((self._find_bicluster(data) for i in range(self.randomized_searches)), key=itemgetter(-1))

            if score < self.score_threshold:
                break

            data[np.ix_(best.rows, best.cols)] -= avg
            biclusters.append(best)

        return Biclustering(biclusters)

    def _find_bicluster(self, data):
        """The basic bicluster search procedure. Each run of this method returns a submatrix
        that is a local maximum of the score function adopted.
        """
        b = self._find_constrained_bicluster(data)
        return self._improve_bicluster(data, b)

    def _find_constrained_bicluster(self, data):
        """Find a k x l bicluster."""
        num_rows, num_cols = data.shape
        k = np.random.choice(np.arange(1, int(np.ceil(num_rows / 2))))
        l = np.random.choice(np.arange(1, int(np.ceil(num_cols / 2))))
        cols = np.random.choice(num_cols, l, replace=False)

        old_avg, avg = -1.0, 0.0

        while not np.isclose(old_avg, avg):
            old_avg = avg

            row_sums = np.sum(data[:, cols], axis=1)
            rows = bn.argpartition(row_sums, num_rows - k)[-k:] # this is usually faster than rows = np.argsort(row_sums)[-k:]

            col_sums = np.sum(data[rows, :], axis=0)
            cols = bn.argpartition(col_sums, num_cols - l)[-l:] # this is usually faster than cols = np.argsort(col_sums)[-l:]

            avg = np.mean(data[np.ix_(rows, cols)])

        return Bicluster(rows, cols)

    def _improve_bicluster(self, data, b):
        """Relaxes the k x l bicluster constraint in order to maximize the score function locally."""
        num_rows, num_cols = data.shape
        old_score, score = -1.0, 0.0

        row_range = np.arange(1, num_rows + 1)
        col_range = np.arange(1, num_cols + 1)

        row_log_combs = self._log_combs(num_rows)[1:] # self._log_combs(num_rows)[1:] discards the case where the bicluster has 0 rows
        col_log_combs = self._log_combs(num_cols)[1:] # self._log_combs(num_cols)[1:] discards the case where the bicluster has 0 columns

        while not np.isclose(old_score, score):
            old_score = score

            row_sums = np.sum(data[:, b.cols], axis=1)
            order = np.argsort(-row_sums)
            row_cumsum = np.cumsum(row_sums[order])
            row_scores = self._scores(row_range, len(b.cols), row_cumsum, row_log_combs, col_log_combs)
            rmax = np.argmax(row_scores) # searches for the number of rows that maximizes the score
            b.rows = order[:rmax+1]

            col_sums = np.sum(data[b.rows, :], axis=0)
            order = np.argsort(-col_sums)
            col_cumsum = np.cumsum(col_sums[order])
            col_scores = self._scores(col_range, len(b.rows), col_cumsum, col_log_combs, row_log_combs)
            cmax = np.argmax(col_scores) # searches for the number of columns that maximizes the score
            b.cols = order[:cmax+1]

            avg = col_cumsum[cmax] / b.area
            score = col_scores[cmax]

        return b, avg, score

    def _scores(self, range_, k, cumsum, m_log_combs, n_log_combs):
        """Calculates the score function for all possible numbers of rows (or columns)."""
        avgs = cumsum / (range_ * k)
        log_probs = norm.logcdf(-avgs * np.sqrt(range_ * k))
        return - log_probs - m_log_combs - n_log_combs[k-1]

    def _log_combs(self, n):
        """Calculates the log of n choose k for k ranging from 0 to n."""
        log_facts = self._cum_log_factorial(n)
        return log_facts[n] - (log_facts + log_facts[::-1])

    def _cum_log_factorial(self, n):
        """Calculates the log of the factorials from 0 to n."""
        log_cumsum = np.cumsum(np.log(np.arange(1, n + 1)))
        return np.append(0, log_cumsum) # 0 because log 0! = log 1 = 0, so this array will have size n + 1

    def _validate_parameters(self):
        if self.num_biclusters <= 0 or self.randomized_searches <= 0:
            raise ValueError("'num_biclusters' and 'randomized_searches' must be greater than zero")

    def _validate_data(self):
        """LAS does not require any data validation step."""
        pass
