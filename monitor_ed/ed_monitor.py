# -*- coding: utf-8 -*-
"""
Created on Thu Mar 25 18:17:13 2021

@author: AndyWang
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from time import sleep
import pandas as pd
import numpy as np
import os
import subprocess
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

def _start_webdriver(browser, driverpath):
    '''
    Function to start a webdriver

    Parameters
    ----------
    browser : str
        Type of the browser you want to open
    driverpath : str
        Path of the driver.

    Returns
    -------
    selenium.webdriver
        Webdriver object for further usage
    '''
    
    if browser.lower() == 'edge':
        return webdriver.Edge(executable_path=driverpath)
    elif browser.lower() == 'chrome':
        return webdriver.Chrome(executable_path=driverpath)
    else:
        raise NotImplementedError(f'Code for {browser} is not implemented')
        
def _open_browser_cmd(port, cache_dir):
    '''
    Open chrome in debugging mode
    '''
    chrome_cmd = f'chrome.exe --remote-debugging-port={port} --user-data-dir="{cache_dir}"'
    subprocess.Popen(chrome_cmd)
    
def _connect_selenium(driverpath, port, cache_dir):
    '''
    connect your browser to python

    Returns
    -------
    driver: Selenium.webdriver object that is connected to your browser

    '''
    
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    
    driver = webdriver.Chrome(driverpath, options=chrome_options)
    
    return driver
        
def _find_inputbox(driver, timeout=30):
    '''
    Find inputbox element in Ed analytics page

    Parameters
    ----------
    driver : selenium.webdriver
    timeout : float/int, optional
        Timeout limit for finding the element. The default is 15.

    Raises
    ------
    TimeoutError

    Returns
    -------
    inputbox : selenium.webdriver.remote.webelement.WebElement
        Input box for searching.

    '''
    tstart = datetime.now()
    
    while True:
        # break out the loop if 
        # 1) find the element successfully
        # 2) reach the time limit
        try:
            inputbox = driver.find_element_by_tag_name('input')
            return inputbox
        except:
            tnow = datetime.now()
            if (tnow - tstart).total_seconds() > timeout:
                raise TimeoutError('Check out your connection!')
            sleep(1)
            
def _search_tut(inputbox, tutcode):
    '''
    Searching tut in Ed analytics page

    Parameters
    ----------
    inputbox : selenium.webdriver.remote.webelement.WebElement
        Webelement for input box
    tutcode : str
        tutorial for searching.

    Returns
    -------
    None.
    '''
    inputbox.clear()
    inputbox.send_keys(tutcode)
    
def _get_header_use(thtag):
    '''
    Get header attribute from usetag

    Parameters
    ----------
    thtag : bs4.element.Tag
        Table header tag.

    Returns
    -------
    str
        header attribute.

    '''
    usetag = thtag.findAll('use')
    if len(usetag) == 0:
        return '#'
    return usetag[0].attrs['xlink:href']

def _get_tdstatus(tdtag):
    '''
    Get table cell content or status (for questions)

    Parameters
    ----------
    tdtag : bs4.element.Tag
        table cell tag.

    Returns
    -------
    str
        table cell content or status.
    '''
    text = tdtag.text
    if text:
        if text != '\u200b':
            return text
    if 'class' in tdtag.attrs:
        cellclass = tdtag.attrs['class']
        if len(cellclass) > 1:
            return cellclass[1].split('-')[-1]
    return ''
    
def _get_tdlink(tdtag):
    atags = tdtag.findAll('a')
    if len(atags) > 0:
        return 'https://edstem.org{}'.format(atags[0].attrs['href'])
    return 'N/A'

def _get_analytics_table(driver):
    '''
    Get analytics table from driver

    Parameters
    ----------
    driver : selenium.webdriver
        Driver that opens Ed analytics page.

    Returns
    -------
    analytics_df : pandas.DataFrame
        DataFrame for analytics table.
    colattrs : list
        A list of column's attribute.

    '''
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.findAll('table', attrs={'class':"lesson-analytics-table"})[0]
    ### get header and body tag
    thead = table.findAll('thead')[0]
    tbody = table.findAll('tbody')[0]
    ### extract info from html to list 
    ### (Note: pandas.read_html doesn't work for this case)
    # header
    header = []
    colattrs = []

    for thtag in thead.findAll('th'):
        header.append(thtag.text.strip())
        colattrs.append(_get_header_use(thtag))
    # body
    tablecells = []
    tablehtmls = []

    trtags = tbody.findAll('tr')
    for trtag in trtags:
        rowcells = []
        rowhtmls = []
        tdtags = trtag.findAll('td')
        for tdtag in tdtags:
            rowcells.append(_get_tdstatus(tdtag))
            rowhtmls.append(_get_tdlink(tdtag))
        tablecells.append(rowcells)
        tablehtmls.append(rowhtmls)
        
    analytics_df = pd.DataFrame(tablecells, columns=header)
    analytics_html = pd.DataFrame(tablehtmls, columns=header)
    
    return analytics_df, analytics_html, colattrs

def _check_search_loaded(driver, tutcode):
    df, _, _ = _get_analytics_table(driver)
    tutcol = df['Tutorial'].apply(lambda x:x.lower())
    if (tutcol != tutcode.lower()).sum() > 0:
        return False
    return True

def _get_online_students(analytics_df):
    '''
    Get students that are online
    '''
    opened_count = (analytics_df.iloc[:, 3:] != 'unopened').sum(axis=1)
    return opened_count > 0

def _get_code_cols(colattrs):
    '''
    Get columns for code only
    '''
    code_check = []
    for attr in colattrs:
        if attr == '#lesson-slide-code' or attr == '#lesson-slide-postgres':
            code_check.append(True)
        else:
            code_check.append(False)
    return code_check

def _prepare_code_plotting(analytics_df, colattrs):
    good_stu = _get_online_students(analytics_df)
    code_check = _get_code_cols(colattrs)
    cleaned_df = analytics_df.loc[good_stu, code_check]
    ### preparing statistics
    ### We use .iloc here to avoid same question in one week
    stats = {'completed':[], 
             'attempted':[], 
             'opened':[], 
             'unopened':[],
            }
    for colidx in range(cleaned_df.shape[1]):
        colseries = cleaned_df.iloc[:,colidx]
        for status in stats:
            stats[status].append((colseries == status).sum())
    
    colnames = cleaned_df.columns.tolist()
    ### return values
    return stats, colnames

def _plot_code_status(stats, colnames):
    fig = plt.figure(figsize=(12, len(colnames)/2))
    ax = fig.add_subplot(111)

    ypos = range(len(colnames),0,-1)
    left = np.zeros(len(colnames))
    statuses = ['completed', 'attempted', 'opened', 'unopened']
    barcolor = {'completed':'green',
                'attempted':'orange',
                'opened':'yellow',
                'unopened':'white'
               }

    for status in statuses:
        ax.barh(ypos, stats[status], left=left, 
                color=barcolor[status],
                label=status,
                edgecolor='black'
               )
        left = np.add(left, stats[status])

    ax.set_yticks(ypos)
    ax.set_yticklabels(colnames, fontsize=15)
    ax.set_ylim(0.5, len(colnames)+0.5)

    xlim_max = 5 * ((int(left[0]) // 5) + 1)
    ax.set_xticks(range(0, xlim_max+1, 5))
    ax.set_xlim(0, xlim_max)

    ax.grid(axis='x', linestyle='--')
    
    fig.savefig('Class_status.png', bbox_inches='tight', dpi=100)
    plt.close()

### for printing
def _get_value_rowcol(df, value):
    rowcols = []
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            if df.iloc[i, j] == value:
                rowcols.append((i, j))
    return rowcols

def _print_new_attempted(analytics_df, analytics_html, rowcols):
    print('NEW ATTEMPTS'.center(70, '*'))
    for row, col in rowcols:
        print('{} attempted {}!\n{}\n'.format(analytics_df.iloc[row, 0], 
                                            analytics_df.columns[col],
                                            analytics_html.iloc[row, col]
                                            ))
    print('*'*70)
    
def _print_gone_attempted(analytics_df, rowcols):
    print('THESE ATTEMPTS ARE GONE'.center(70, '*'))
    for row, col in rowcols:
        print('{} finished {}!'.format(analytics_df.iloc[row, 0],
                                       analytics_df.columns[col]))
    print('*'*70)
    
def _print_old_attempted(analytics_df, analytics_html, rowcols):
    print('OLD ATTEMPTS'.center(70, '*'))
    for row, col in rowcols:
        print('{} is still trying {}!\n{}\n'.format(analytics_df.iloc[row, 0], 
                                                  analytics_df.columns[col],
                                                  analytics_html.iloc[row, col]
                                                  ))
    print('*'*70)
    
def _compare_analytics_dfs(analytics_df, analytics_html, oldpath='./old_analytics_df.pickle'):
    if not os.path.exists(oldpath):
        rowcols = _get_value_rowcol(analytics_df, 'attempted')
        _print_gone_attempted(analytics_df, [])
        _print_old_attempted(analytics_df, analytics_html, [])
        _print_new_attempted(analytics_df, analytics_html, rowcols)
    else:
        old_analytics_df = pd.read_pickle(oldpath)
        oldatttab = old_analytics_df == 'attempted'
        changetab = analytics_df != old_analytics_df
        newatttab = analytics_df == 'attempted'
        ### attempts gone
        goneatt_ = (oldatttab & changetab)
        rowcols = _get_value_rowcol(goneatt_, True)
        _print_gone_attempted(analytics_df, rowcols)
        ### old attempts
        oldatt_ = (oldatttab & newatttab)
        rowcols = _get_value_rowcol(oldatt_, True)
        _print_old_attempted(analytics_df, analytics_html, rowcols)
        ### new attempts
        newatt_ = (newatttab & changetab)
        rowcols = _get_value_rowcol(newatt_, True)
        _print_new_attempted(analytics_df, analytics_html, rowcols)
    analytics_df.to_pickle(oldpath)
    
def _check_login(driver):
    if 'Log in to continue' in driver.page_source:
        return True
    return False

def _manually_check():
    ### read settings
    with open('./setup.py') as fp:
        code = fp.read()
    exec(code, globals())
    
    if os.path.exists(OLDPICKLEPATH):
        os.remove(OLDPICKLEPATH)
    ### start!
    if not OPEN_WITH_CACHE:
        driver = _start_webdriver(BROWSER, DRIVERPATH)
    elif BROWSER.lower() == 'chrome':
        _open_browser_cmd(PORT, CACHE_DIR)
        driver = _connect_selenium(DRIVERPATH, PORT, CACHE_DIR)
    else:
        raise NotImplementedError('NOT IMPLEMENTED')
        
    driver.get(EDURL)
    wait = input('Please wait till the webpage responds!')
    while _check_login(driver):
        status_code = input('Please Log in Ed first!!!'.center(70, '+'))
        
    print(f'The Tutorial Code is {TUTCODE}')
    # tutnew = input("Input the new TUTCODE if it is not correct, or press enter")
    # if tutnew:
    #     TUTCODE = tutnew
    ### starting the loop!
    break_sign = ''
    while break_sign != 'q':
        driver.refresh()
        inputbox = _find_inputbox(driver)
        _search_tut(inputbox, TUTCODE)
        
        ### get analytics dataframe
        while not _check_search_loaded(driver, TUTCODE):
            sleep(1)
        analytics_df, analytics_html, colattrs = _get_analytics_table(driver)
        stats, colnames = _prepare_code_plotting(analytics_df, colattrs)
        _plot_code_status(stats, colnames)
        _compare_analytics_dfs(analytics_df, analytics_html, OLDPICKLEPATH)
        
        break_sign = input('Type "q" to quit! Press Enter to continue! ')
        print('\n\n')
    
    driver.quit()
    if CLEAN:
        os.remove(OLDPICKLEPATH)
        os.remove('./Class_status.png')
        
    print('Thanks for using!'.center(70, '-'))
    
if __name__ == '__main__':
    # pass
    _manually_check()