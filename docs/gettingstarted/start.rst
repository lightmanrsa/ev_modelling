.. VencoPy getting started documentation file, created on February 11, 2020
    by Niklas Wulff
    Licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/deed.en

.. _start:

Getting Started and Tutorials
===================================

Tutorials overview
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


To get started with VencoPy a set of tutorials are provided for the user to learn about the different classes and how each of them can be customised.
The tutorials are iPythonNotebooks to be opened with Jupyter Lab and can be found in the gitlab repository.

- Tutorial 1: Showcasing run.py
- Tutorial 2: The DataParser class
- Tutorial 3: The TripDiaryBuilder class (currently this tutorial is empty, it will be complemented following upcoming developments)
- Tutorial 4: The GridModeler class
- Tutorial 5: The FlexEstimator class


Tutorials setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To start carrying out the tutorials, jupyterlab should be installed in the environment. 
If you cloned the repository doing 'pip install vencopy', the jupyterlab package will automatically be installed in your environment and you thus only need to activate your vencopy environment via the Anaconda Powershell Prompt ('conda activate vencopy').
If you want to run the tutorial in an environment, which already exists, you can first activate your desired environment ('conda activate <yur environment name>') and then install the jupyterlab package ('conda install jupyterlab').
Now that the requirements are satisfied, you can either open the jupyter notebooks with the tutorials in an IDE that supports notebooks (e.g. VSCode) or open them in browser from the Anaconda Powershell Prompt ('jupyter lab --notebook-dir='<your local path to te repository>' --browser=firefox').

