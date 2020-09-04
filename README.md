# VencoPy Readme file
- Author: Niklas Wulff
- Contact: niklas.wulff@dlr.de
- Version: 0.0.8 (pre-release)

Description
A data process tool offering hourly demand and flexibility profiles for future electric vehicle fleets in an aggregated manner.

Codestyle 
We use PEP-8 
Exception is that we use lower camel case for method and variable names

Install instructions
Install using the environment management system conda, open the conda console in your vencopy folder and run the following commands

conda create -n [NAME] python=3.7 
[confirm]
conda activate [NAME]
conda install --file requirementsPreRelease.txt

Documentation
Build docu from a conda bash with activated environment typing

sphinx-build -b html ./source/ ./build/
