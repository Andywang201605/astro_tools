import astropy.units as u
from astropy.coordinates import EarthLocation
from pytz import timezone
from astroplan import Observer
import numpy as np
import matplotlib.pyplot as plt

from astroplan import FixedTarget
from collections import Sequence

from astropy.coordinates import SkyCoord
from astropy.time import Time

from matplotlib import dates
from datetime import datetime, timedelta

from bs4 import BeautifulSoup as bs
import re

class ATCA_sched:
    '''
    Read ATCA schedules from html file(s) - compatible for v2.20 ATCA observing portal
    
    Function(s):
        __init__(files)

        params:
            files (str or list): file(s) to be read
        
    Attributes:
        timezone: timezone for the schedules
        schedules: A dictionary to store all schedules information - the structure of the dictionary is organized as followed
            keys: date; 
            values: a list consists of projects/blocks in that day, for a single block - [(time_start, time_end), project_name, available]    
    '''
    def __init__(self, files):
        ### Attribute scheds - store all scheds information
        self.schedules = {}
        
        if isinstance(files, str):
            self._read_single_file(files)
        else:
            for file in files:
                self._read_single_file(file)
        
    def _read_single_file(self, filename):
        with open(filename, "r", encoding='utf-8') as f:
            text = f.read()
            
        webcontent = bs(text, 'lxml')
        portal_timezone = webcontent.find_all('button', attrs={'class':"fc-timeZone-button fc-button fc-button-primary"})[0].text
        self.timezone = portal_timezone.split(':')[1].strip()
        
        fc_head = webcontent.find_all('thead', attrs={'class':'fc-head'})[0]
        fc_body = webcontent.find_all('div', attrs={'class':'fc-content-skeleton'})[0]
        
        html_date = self._get_portal_dates(fc_head)
        portal_scheds = self._get_portal_scheds(fc_body)
        
        if len(html_date) != len(portal_scheds):
            print(f'{filename} table head and body do not match!')
            return None
        
        for date, sched_day in zip(html_date, portal_scheds):
            self.schedules[date] = self._get_portal_sched_day(sched_day)
        
        
    def _get_portal_dates(self, fc_head):
        all_ths = fc_head.find_all('th') # all_ths[0] is about format
        dates = [tag['data-date'] for tag in all_ths[1:]]
        return dates
    
    def _floathour_to_time(self, float_hour):
        return '{:0>2}:{:0>2.0f}'.format(int(float_hour), (float_hour - int(float_hour))*60)

    def _get_time_from_style(self, fc_tag, hour_height=26.4):
        pattern = re.compile(r'top: (.*)px; bottom: (.*)px;')
        px_start, px_end = pattern.findall(fc_tag['style'])[0]
        block_start = self._floathour_to_time(float(px_start)/hour_height)
        block_end = self._floathour_to_time(-float(px_end)/hour_height)
        return block_start, block_end

    def _get_portal_sched_day(self, fc_day):
        '''
        Get the schedule for one day
        '''
        formatted_sched = []
        fc_scheds = fc_day.find_all('div')
        for sched in fc_scheds:
            block_time = self._get_time_from_style(sched)
            block_disc = sched.text
            block_avai = True if 'Green' in block_disc else False
            formatted_sched.append([block_time, block_disc, block_avai])
        return formatted_sched

    def _get_portal_scheds(self, fc_body):
        portal_raw_days = fc_body.find_all('td')[1:]
        return [raw_day.find_all('div', attrs={'class':"fc-bgevent-container"})[0] for raw_day in portal_raw_days]
