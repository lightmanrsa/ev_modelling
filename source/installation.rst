.. VencoPy installation documentation file, created on February 11, 2020
    by Niklas Wulff
    Licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/deed.en

.. _installation:

Installation and Set-up
===================================


This part of the documentation holds a step-by-step installation guide for VencoPy. 

1.  Set-up your environment. For this, open a console, navigate to the folder of your VencoPy repo and
    carry out one of the two below::
        
        conda create --name <env> 
        conda activate <env>
    
    Navigate to your checked out repository and then type in::
        
        conda install --file <requirements.txt>
    
2.  Configure your config files and set correct links. 
    You will find your config file in your repo under /config/VencoPy_conf.yaml Therein, you have to link to all folders
    and input files. Some folders that are in your repo are given relative, others are given absolute. Input filenames
    have to be given. 
    Additionally you have to set the link to your config file in venco_main.py (basically the first thing that is done 
    after imports). 

3.  You're now ready to run VencoPy for the first time by running::
        
        python venco_main.py

4.  Have fun calculating electric vehicle flexibility!