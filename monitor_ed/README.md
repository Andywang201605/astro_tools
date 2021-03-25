## Scripts for monitoring ED

This code is used for monitoring Ed (at least for me)

### Usage
1. Change parameters in `setup.py`.
  - BROWSER: which browser to use (suggest to use `chrome`)
  - DRIVERPATH: path for browser driver
  - EDURL: url for Ed analytics page
  - TUTCODE: tutorial code for your tut
  - OLDPICKLEPATH: path for saving the previous analytics page (should ended with `.pickle`)
  - CLEAN: True if you want to clean all files created during the process

2. run `python ed_monitor.py`.
3. Wait till the webpage responds and then press ENTER. Due to our setting, you need to log in Ed everytime you run the script.
4. You can check online students progress by opening `./Class_status.png` and check new attempts by notice in cmd
5. Press Enter to continue (i.e.: refresh and get new status for the class); press 'q' to quit

2021-Mar-26
