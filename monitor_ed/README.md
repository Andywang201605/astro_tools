## Scripts for monitoring Ed

This code is used for monitoring Ed (at least for me)

### Usage
1. Change parameters in `setup.py`.
  - `OPEN_WITH_CACHE`: use browser cache to launch the browser (if you have logged in in the test environment already, you don't need to log in again)
  - `BROWSER`: which browser to use (suggest to use `chrome`)
  - `DRIVERPATH`: path for browser driver
  - `PORT`: the port you want to launch browser at (use this param only if `OPEN_WITH_CACHE` is True and `BROWSER` is chrome)
  - `CACHE_DIR`: directory to put all browser data (use this param only if `OPEN_WITH_CACHE` is True and `BROWSER` is chrome)
  - `EDURL`: url for Ed analytics page
  - `TUTCODE`: tutorial code for your tut
  - `OLDPICKLEPATH`: path for saving the previous analytics page (should ended with `.pickle`)
  - `CLEAN`: True if you want to clean all files created during the process

2. run `python ed_monitor.py`.
3. Wait till the webpage responds and then press ENTER. Due to our setting, you need to log in Ed everytime you run the script (if `OPEN_WITH_CACHE` is False).
4. You can check online students progress by opening `./Class_status.png` and check new attempts by notice in cmd
5. For simplicity, you can check webpage `./monitor.html`
6. Press Enter to continue (i.e.: refresh and get new status for the class); press 'q' to quit

2021-Mar-31
