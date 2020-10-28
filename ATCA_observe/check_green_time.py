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
    ATCA_sched(files)
    
    Read ATCA schedules from html file(s) - compatible for v2.20 ATCA observing portal
    
    params:
    ---------
    files (str or list): file(s) to be read
    
    example:
    ---------
    sched = ATCA_sched(['./test/Week1.html', './test/Week2.html'])
        
    attributes:
    ---------
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
        '''
        Function to read a single html file to self.schedules
        '''
        
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
        '''
        get dates from html files (table head)
        '''
        all_ths = fc_head.find_all('th') # all_ths[0] is about format
        dates = [tag['data-date'] for tag in all_ths[1:]]
        return dates
    
    def _floathour_to_time(self, float_hour):
        '''
        covert a float number to hour:minute format (e.g.: 1.5 -> 01:30)
        '''
        return '{:0>2}:{:0>2.0f}'.format(int(float_hour), (float_hour - int(float_hour))*60)

    def _get_time_from_style(self, fc_tag, hour_height=26.4):
        '''
        get block starting and ending time from html tag
        
        Notes:
            In the html file, each hour represents 26.4 pixels
        '''
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
        '''
        get all raw html schedules from table body
        '''
        portal_raw_days = fc_body.find_all('td')[1:]
        return [raw_day.find_all('div', attrs={'class':"fc-bgevent-container"})[0] for raw_day in portal_raw_days]

    
class ATCA_obs:
    '''
    ATCA_obs(targets, tzinfo='Australia/Sydney', portal_htmls=[])
    
    Help with schedule the observation
    
    params:
    --------
    targets (FixTarget or list): a single FixTarget or a list of FixTarget Objects
    tzinfo (str): The timezone of the observer (check `pytz.all_timezones` for all acceptable timezones)
    portal_htmls (list): If provided, load the ATCA schedule from the webpages. an empty list by default
    
    example:
    --------
    import astropy.units as u
    from astroplan import FixedTarget
    from astropy.coordinates import SkyCoord
    from datetime import datetime, timedelta
    
    portal_htmls = ['./test/Week1.html', './test/Week2.html']
    target = [FixedTarget(name='src1', coord=SkyCoord(233.3333,-66.6666,unit=u.deg)),
              FixedTarget(name='src2', coord=SkyCoord(66.6666,-23.3333,unit=u.deg))]
    t = datetime.fromisoformat('2020-10-28')
    obs = ATCA_obs(target, tzinfo='Australia/Sydney', portal_htmls=portal_htmls)
    
    fig, ax = obs.plot_target_altitude_with_schedule(t, duration=timedelta(days=10), dateformat='%D-%H:%M')
    fig, ax = obs.plot_single_observability_heatmap(t, days=7, target_index=0)

    
    attributes:
    --------
    targets: a list of FixedTarget objects need to be observed
    calibrator: a list of FixedTarget objects
    observer: an Observer object for ATCA
    utcoffset: a timedelta object shows the offset between the timezone of the observer and UTC
    tzinfo: timezone for the observer
    portal_sched: the formatted schedule from portal_htmls - created from ATCA_sched.schedules
    portal_utcoffset: a timedelta object shows the offset between the timezone of the ATCA schedule and UTC
    portal_tz: ATCA portal timezone
    
    functions:
    --------
    plot_target_altitude: plot targets altitude vs time
    plot_target_altitude_with_schedule: plot targets altitude vs time, with green time shaded in green
    plot_single_observability_heatmap: plot observability for a single source in a heatmap
    
    '''
    def __init__(self, targets, tzinfo='Australia/Sydney', portal_htmls=[]):
        ### target and calibrators
        if not isinstance(targets, Sequence):
            targets = [targets]
            
        self.targets = targets
        self.calibrator = [FixedTarget(name='1934-638', coord=SkyCoord('19h39m25.026s -63d42m45.63s')),
                           FixedTarget(name='0823-500', coord=SkyCoord('08h25m26.869s -50d10m38.49s'))]
        ### observer
        ATCA_loc = (149.5501388*u.deg,-30.3128846*u.deg,237*u.m)
        location = EarthLocation.from_geodetic(*ATCA_loc)

        self.observer = Observer(name='ATCA',
                                 location=location,
                                 timezone=timezone('Australia/Sydney'))
        time_now = datetime.now(timezone(tzinfo))
        self.utcoffset = time_now.utcoffset()
        self.tzinfo = tzinfo
        
        if len(portal_htmls) == 0:
            self.portal_tz = None
            self.portal_sched = None
        else:
            atca_scheds = ATCA_sched(portal_htmls)
            self.portal_tz = atca_scheds.timezone
            self.portal_sched = atca_scheds.schedules
            
            ### portal utcoffset
            portal_now = datetime.now(timezone(self.portal_tz))
            self.portal_utcoffset = portal_now.utcoffset()
        
    def plot_target_altitude(self, start_time, duration=timedelta(days=1), horizon=12, dateformat='%H:%M', **style_kwargs):
        '''
        plot_target_altitude(start_time, duration=timedelta(days=1), horizon=12, dateformat='%H:%M', **style_kwargs)
        
        plot targets altitude vs time
        
        params:
        --------
        start_time (datetime.datetime): the time to start the plot
        duration (datetime.timedelta): the length of the plot, 1 day by default
        horizon (int or float): telescope horizon in degree, 12 by default
        dateformat (str): time label formatting, "%H:%M" by default
        style_kwargs: arguments passed to matplotlib.pyplot.plot_date()
        
        returns:
        --------
        fig, ax
        '''
        ### plot style
        if style_kwargs is None:
            style_kwargs = {}
        style_kwargs = dict(style_kwargs)
        style_kwargs.setdefault('linestyle', '-')
        style_kwargs.setdefault('linewidth', 2)
        style_kwargs.setdefault('fmt', '-')
        ### convert time to series of time
        time_num = (duration.days + 1)*1000 + 1
        time_series = start_time + np.linspace(0,1,time_num)*duration
        ### covert times to UTC to calculate the alt/az
        time_utcs = time_series - self.utcoffset
        
        fig = plt.figure(figsize=(8*duration.total_seconds()/(24*3600), 6))
        ax = fig.add_subplot(111)
        
        for target in self.targets:
            alts = self.observer.altaz(time_utcs, target).alt.value
            if target.name:
                ax.plot_date(time_series, alts, label=target.name, **style_kwargs)
            else:
                ax.plot_date(time_series, alts, **style_kwargs)
                
        for calibrator in self.calibrator:
            alts = self.observer.altaz(time_utcs, calibrator).alt.value
            if calibrator.name == '1934-638':
                ax.plot_date(time_series, alts, label=calibrator.name, fmt='black', lw=3, ls=':')
            else:
                ax.plot_date(time_series, alts, label=calibrator.name, fmt='black', lw=1, ls=':')
                
        ax.axhline(y=horizon, color='red', ls=':', lw=2)
                
        date_formatter = dates.DateFormatter(dateformat)
        ax.xaxis.set_major_formatter(date_formatter)
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        
        ax.set_xlim(dates.date2num(time_series[0]), dates.date2num(time_series[-1]))
        
        ax.set_ylim(0,90)
        ax.legend()
        
        ax.set_xlabel(f'TIME FROM {start_time.year}-{start_time.month}-{start_time.day} [{self.tzinfo}]')
                
        return fig, ax
    
    def plot_target_altitude_with_schedule(self, start_time, duration=timedelta(days=1), horizon=12, dateformat='%H:%M', **style_kwargs):
        '''
        plot_target_altitude_with_schedule(start_time, duration=timedelta(days=1), horizon=12, dateformat='%H:%M', **style_kwargs)
        
        plot targets altitude vs time, with green time shaded in green
        
        params:
        --------
        start_time (datetime.datetime): the time to start the plot
        duration (datetime.timedelta): the length of the plot, 1 day by default
        horizon (int or float): telescope horizon in degree, 12 by default
        dateformat (str): time label formatting, "%H:%M" by default
        style_kwargs: arguments passed to matplotlib.pyplot.plot_date()
        
        returns:
        --------
        fig, ax
        '''
        if not self.portal_sched:
            return self.plot_target_altitude(start_time, duration, horizon, dateformat, **style_kwargs)
        
        fig, ax = self.plot_target_altitude(start_time, duration, horizon, dateformat, **style_kwargs)
        
        ### convert time to series of time
        time_num = (duration.days + 1)*1000 + 1
        time_series = start_time + np.linspace(0,1,time_num)*duration
        
        ### read schedules
        for obs_day in self.portal_sched:
            for project_row in self.portal_sched[obs_day]:
                if project_row[-1]:
                    block_start = datetime.fromisoformat(obs_day) + timedelta(hours=float(project_row[0][0].split(':')[0]),
                                                                              minutes=float(project_row[0][0].split(':')[1]))
                    block_start = block_start + self.utcoffset - self.portal_utcoffset
                    
                    block_end = datetime.fromisoformat(obs_day) + timedelta(hours=float(project_row[0][1].split(':')[0]),
                                                                            minutes=float(project_row[0][1].split(':')[1]))
                    block_end = block_end + self.utcoffset - self.portal_utcoffset
                    
                    ax.axvspan(xmin=dates.date2num(block_start), xmax=dates.date2num(block_end),
                               color='green', alpha=0.1)
                    
        ax.set_xlim(dates.date2num(time_series[0]), dates.date2num(time_series[-1]))
                    
        return fig, ax
    
    def _greentime_bool(self, time):
        '''
        _greentime_bool(time)
        
        check if time is in during the green time slot
        
        params:
        --------
        time (datetime.datetime): the time to be checked
        
        returns:
        --------
        None if there is no schedule file for that day; True if it is in the green time slot; False if not
        '''
        if not self.portal_sched:
            return None
        
        ### transfer time to portal timezone
        time = time - self.utcoffset + self.portal_utcoffset
        
        time_date = f'{time.year}-{time.month:0>2}-{time.day:0>2}'
        if time_date not in self.portal_sched:
            return None
        
        for project in self.portal_sched[time_date]:
            project_start = datetime.fromisoformat(time_date) + timedelta(hours=float(project[0][0].split(':')[0]),
                                                                          minutes=float(project[0][0].split(':')[1]))
            project_end = datetime.fromisoformat(time_date) + timedelta(hours=float(project[0][1].split(':')[0]),
                                                                        minutes=float(project[0][1].split(':')[1]))
            if time >= project_start and time < project_end:
                if project[-1]:
                    return True
                return False
            
        return None
    
    def plot_single_observability_heatmap(self, start_time, days=7, target_index=0, horizon=12):
        '''
        plot_single_observability_heatmap(start_time, days=7, target_index=0, horizon=12)
        
        plot observability for a single source in a heatmap - we consider two factors: one is green time constrain, the other is altitude constrain
        
        params:
        --------
        start_time (datetime.datetime): time to start the plot. MAKE SURE start at 00:00 or there will be a bug
        days (int): number of days to plot, 7 by default
        target_index (int): index of the target of interest - specify which target to plot 
        horizon (int or float): telescope horizon in degree, 12 by default
        
        returns:
        --------
        fig, ax
        
        '''
        fig = plt.figure(figsize=(16,2*int(days)))
        
        for day in range(days):
            observability = np.zeros((2,48))
            
            ax = fig.add_subplot(int(days),1,day+1)
            day_time_start = start_time + timedelta(days=day)
            for i in range(48):
                block_time = day_time_start + timedelta(minutes=30) * i
                block_time_utc = block_time - self.utcoffset
                
                target_alt = self.observer.altaz(block_time_utc, self.targets[target_index]).alt.value
                if target_alt < horizon:
                    observability[0][i] = 0
                else:
                    observability[0][i] = 1
                    
                is_green_time = self._greentime_bool(block_time)
                if is_green_time == None:
                    observability[1][i] = np.nan
                else:
                    observability[1][i] = float(is_green_time)
                    
            extent = [-0.5, 47.5, -0.5, 1.5]
            ax.imshow(observability, extent=extent, origin='lower')
            ax.set_yticks(range(0, 2))
            ax.set_xticks(range(0, 48,2))
            ax.set_yticklabels(['Altitude Constrain','Greentime Constrain'])
            ax.set_xticklabels([f"{i:0>2}:00" for i in range(24)])
            
            ax.set_xticks(np.arange(extent[0], extent[1]), minor=True)
            ax.set_yticks(np.arange(extent[2], extent[3]), minor=True)
            ax.grid(which='minor', color='w', linestyle='-', linewidth=2)
            
            ax.set_xlabel(f'Observability in {day_time_start.year}-{day_time_start.month}-{day_time_start.day} [{self.tzinfo}]')
            
#         fig.suptitle(self.targets[target_index].name)
#         plt.tight_layout()
            
        return fig, ax
