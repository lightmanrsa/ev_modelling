.. VencoPy installation documentation file, created on February 11, 2020
    by Niklas Wulff
    Licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/deed.en

.. _installation:

Installation and Set-up
===================================


Requirements and boundary conditions
------------------------------------------------

VencoPy runs on Unix and Windows-based operating systems. It requires an installed version of python and the package, dependency and environment management tool conda as well as access to the internet for setting up the environment (downloading the required packages). An installation of the versioning software git is helpful especially if you want to contribute to the software. VencoPy is consistent with the software application class 1 of the DLR software categorization. Versioning is based on major, minor and fix (X.Y.Z) changes versioning system via git-labels.

This part of the documentation holds a step-by-step installation guide for VencoPy. 

1.  Get the VencoPy codebase. The easiest way is via git (after navigating to the folder you want to clone VencoPy to)::

        git clone https://gitlab.dlr.de/vencopy/vencopy.git
        
2.  Set-up your environment. For this, open a conda-console (such as the anaconda prompt), navigate to the folder of your VencoPy repo and
    enter the following command::
        
        conda create --file <requirementsFile.yml>
        conda activate <VencoPy_preRelease>
    
3.  Optional: Configure your config files if you want to use absolute links. This is only needed if you want to reference your own
    local data or want to post-process VencoPy results and write them to a model input folder somewhere on your drive.
    You will find your config file in your repo under :file:`./config/config.yaml`. Input filenames have to be set, with the default being set to an exemplary pre-processed file of ~17000 trips of German car drivers. 

4.  You're now ready to run VencoPy for the first time by typing::
        
        python venco_main.py

    Your results are stored in :file:`./output/dailyTimeseries/` and :file:`./output/plots/`.
    
    
5.  Have fun calculating electric vehicle flexibility!