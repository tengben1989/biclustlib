# biclustlib

biclustlib is a Python library of biclustering algorithms, evaluation measures and datasets distributed under the GPLv3 license.

## Installation

TO DO

## Dependencies

See requirements.txt.

## Citing
If you use biclustlib in a scientific publication, we would appreciate citations of our paper where this library was first mentioned and used.

To cite biclustlib use: Padilha, V. A. & Campello, R. J. G. B. (2017). A systematic comparative evaluation of biclustering techniques. *BMC Bioinformatics*, 18(1):55.

For TeX/LaTeX:

    @article{padilha2017,
      title={A systematic comparative evaluation of biclustering techniques},
      author={Padilha, Victor A and Campello, Ricardo J G B},
      journal={BMC Bioinformatics},
      volume={18},
      number={1},
      pages={55},
      year={2017},
      publisher={BioMed Central}
    }

## Available algorithms

### Python implementations

* [Bi-Correlation Clustering Algorithm (BCCA)](https://academic.oup.com/bioinformatics/article/25/21/2795/227776/Bi-correlation-clustering-algorithm-for);
* [Bit-Pattern Biclustering Algorithm (BiBit)](https://academic.oup.com/bioinformatics/article/27/19/2738/231788/A-biclustering-algorithm-for-extracting-bit);
* [Cheng and Church's Algorithm (CCA)](https://www.researchgate.net/profile/George_Church/publication/2329589_Biclustering_of_Expression_Data/links/550c04030cf2063799394f5e.pdf);
* [Large Average Submatrices (LAS)](http://www.jstor.org/stable/30242874?seq=1#page_scan_tab_contents);
* [Plaid](http://www.sciencedirect.com/science/article/pii/S0167947304000295);
* [Conserved Gene Expression Motifs (xMOTIFs)](https://books.google.com.br/books?hl=pt-BR&lr=&id=5_fRL7rSSX0C&oi=fnd&pg=PA77&dq=extracting+conserved+gene+expression+motifs&ots=I7pzAch3Oq&sig=3BfxcMpfy4lHyD74xBCoSK-PhFo#v=onepage&q&f=false);

### Wrappers for publicly available software

* [BayesianBiClustering (BBC)](https://bmcgenomics.biomedcentral.com/articles/10.1186/1471-2164-9-S1-S4) (wrapper for the executable of the [authors' original implementation](http://www.people.fas.harvard.edu/~junliu/BBC/));
* [Factor Analysis for Bicluster Acquisition (FABIA)](https://academic.oup.com/bioinformatics/article/26/12/1520/287036/FABIA-factor-analysis-for-bicluster-acquisition) (wrapper for the [fabia package](https://github.com/bioinf-jku/pyfabia));
* [Order-Preserving Submatrix (OPSM)](http://online.liebertpub.com/doi/abs/10.1089/10665270360688075) (wrapper for the [BicAT](http://people.ee.ethz.ch/~sop/bicat/) software);
* [QUalitative BIClustering (QUBIC)](https://academic.oup.com/nar/article/37/15/e101/2409951/QUBIC-a-qualitative-biclustering-algorithm-for) (wrapper for the executable of the [authors' original implementation](http://csbl.bmb.uga.edu/~maqin/bicluster/));
* [Spectral Biclustering](http://genome.cshlp.org/content/13/4/703.short) (wrapper for the [scikit-learn package](http://scikit-learn.org/stable/modules/generated/sklearn.cluster.bicluster.SpectralBiclustering.html) implementation);

All the original codes are already available with biclustlib and are compiled for the x86_64 architecture.

## Available data collections

* *Saccharomyces cerevisiae* microarray dataset from [Tavazoie et al. (1999)](http://www.alterlab.org/teaching/BIOEN3070/papers/Tavazoie_1999.pdf) which was used in [(Cheng and Church, 2000)](https://www.researchgate.net/profile/George_Church/publication/2329589_Biclustering_of_Expression_Data/links/550c04030cf2063799394f5e.pdf);
* *Saccharomyces cerevisiae* and *Arabidopsis thaliana* microarray datasets used in [(Prelić et al. (2006))](https://academic.oup.com/bioinformatics/article/22/9/1122/200492/A-systematic-comparison-and-evaluation-of);
* Benchmark of 17 *Saccharomyces cerevisiae* microarray datasets compiled and preprocessed by [Jaskowiak et al. (2013)](http://ieeexplore.ieee.org/abstract/document/6461019/);
* Benchmark of 35 cancer microarray datasets compiled and preprocessed by [Souto et al. (2008)](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-9-497);

## Example of use

```python
import numpy as np

from biclustlib.algorithms import ChengChurchAlgorithm
from biclustlib.datasets import load_yeast_tavazoie

# load yeast data used in the original Cheng and Church's paper
data = load_yeast_tavazoie().values

# missing value imputation suggested by Cheng and Church
missing = np.where(data < 0.0)
data[missing] = np.random.randint(low=0, high=800, size=len(missing[0]))

# creating an instance of the ChengChurchAlgorithm class and running with the parameters of the original study
cca = ChengChurchAlgorithm(num_biclusters=100, msr_threshold=300.0, multiple_node_deletion_threshold=1.2)
biclustering = cca.run(data)
print(biclustering)
```

## License (GPLv3)
    biclustlib: A Python library of biclustering algorithms and evaluation measures.
    Copyright (C) 2017  Victor Alexandre Padilha

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
