# VencoPy Readme file
- Author: Niklas Wulff
- Contact: niklas.wulff@dlr.de
- Version: 0.0.8 (pre-release)

## Description
A data process tool offering hourly demand and flexibility profiles for future electric vehicle fleets in an aggregated manner.

## Codestyle 
We use PEP-8, with the exception of lowerCamelCase for method and variable names as well as UpperCamelCase for classes

## Install instructions
Clone VencoPy to a folder of your wish typing ::

git clone https://gitlab.com/dlr-ve/vencopy.git

Install using the environment management system conda, open the conda console navigate to your VencoPy folder and run the following commands::

conda env create -f requirements.yml

An environment named "VencoPy_preRelease" will be created. Activate by entering::

conda activate VencoPy_preRelease 

In the same folder, run VencoPy by typing ::

python venco_main.py


## Documentation
A public documentation is hosted on readthedocs here: https://vencopy.readthedocs.io/en/latest/

Alternatively, you can build a docu from a conda bash with an activated VencoPy environment typing::

sphinx-build -b html ./source/ ./build/
