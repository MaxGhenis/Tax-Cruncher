# bash commands for installing your package

git clone https://github.com/Peter-Metz/Tax-Cruncher
cd Tax-Cruncher
git checkout comp
conda install PSLmodels::taxcalc conda-forge::paramtools
pip install -e .