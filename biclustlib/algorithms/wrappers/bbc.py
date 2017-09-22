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

from ._base import BaseExecutableWrapper
from ...models import Bicluster, Biclustering
from os.path import dirname, join

import numpy as np
import re
import os

class BayesianBiclustering(ExecutableWrapper):
    """Bayesian BiClustering (BBC)

    BBC assumes the plaid model and uses a Gibbs sampling procedure for its statistical inference.

    This class is a simple wrapper for the executable obtained after compiling the C code
    provided by the original authors of this algorithm (available in http://www.people.fas.harvard.edu/~junliu/BBC/).
    The binaries contained in this package were compiled for the x86_64 architecture.

    Reference
    ---------
    Gu, J., and Liu, J. S. (2008). Bayesian biclustering of gene expression data. BMC genomics, 9(1), S4.

    Parameters
    ----------
    num_biclusters : int, default: 10
        Number of biclusters to be found.

    normalization : str, default: 'iqrn'
        Normalization method used by the algorithm. Must be one of ('iqrn', 'sqrn', 'csn', 'rsn')
        (see http://www.people.fas.harvard.edu/~junliu/BBC/BBC_manual.pdf for details).

    alpha : float, default: 90.0
        Alpha value for the normalization step (used only when normalization is
        'iqrn' or 'sqrn').

    tmp_dir : str, default: '.bbc_tmp'
        Temporary directory to save the outputs generated by BBC's executable.
    """

    def __init__(self, num_biclusters=10, normalization='iqrn', alpha=90, tmp_dir='.bbc_tmp'):
        module_dir = dirname(__file__)

        exec_comm = join(module_dir, 'bin', 'BBC') + \
                    ' -i {_data_filename}' + \
                    ' -k {num_biclusters}' + \
                    ' -o {_output_filename}' + \
                    ' -n {normalization}' + \
                    ' -r {alpha}'

        super().__init__(exec_comm, tmp_dir=tmp_dir)

        self.num_biclusters = num_biclusters
        self.normalization = normalization
        self.alpha = alpha

    def _parse_output(self):
        biclusters = []

        if os.path.exists(self._output_filename):
            with open(self._output_filename, 'r') as f:
                content = f.read()
                biclusters_str = re.split('bicluster[0-9]+\n', content)

                bic_str = biclusters_str.pop(0)
                bic = float(bic_str.rstrip().split('\t')[-1].split()[1])

                for b_str in biclusters_str:
                    rows_str, cols_str = b_str.split('col\t')

                    rows_str = rows_str.split('\n')[2:-1]
                    rows = np.array([int(x.split('\t')[0]) - 1 for x in rows_str])

                    cols_str = cols_str.split('\n')[1:-1]
                    cols = np.array([int(x.split('\t')[0]) - 1 for x in cols_str])

                    biclusters.append(Bicluster(rows, cols))

        return Biclustering(biclusters)

    def _validate_parameters(self):
        if self.num_biclusters <= 0:
            raise ValueError("num_biclusters must be > 0, got {}".format(self.num_biclusters))

        norm = ('iqrn', 'sqrn', 'csn', 'rsn')

        if self.normalization not in norm:
            raise ValueError("normalization must be one of {}, got {}".format(norm, self.normalization))

        if self.alpha <= 0.0 or self.alpha >= 100.0:
            raise ValueError("alpha must be > 0 and < 100, got {}".format(self.alpha))
