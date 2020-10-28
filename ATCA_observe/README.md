### Code for semi-automatically loading ATCA schedule and checking for the green time

**STEP 1**
Download ATCA schedules from ATCA observing portal. Since the code is semi-automatic, you need to download it mannually week by week.
*REMEMBER* to save as `webpage,complete`, even though we only need the `.html` file

**STEP 2**
Example:
```
import astropy.units as u
from astroplan import FixedTarget
from astropy.coordinates import SkyCoord
from datetime import datetime, timedelta

portal_htmls = ['./test/Week1.html', './test/Week2.html'] #the webpages for schedules downloaded from ATCA observing portal.
target = [FixedTarget(name='src1', coord=SkyCoord(233.3333,-66.6666,unit=u.deg)),
          FixedTarget(name='src2', coord=SkyCoord(66.6666,-23.3333,unit=u.deg))] # the sources of interest
t = datetime.fromisoformat('2020-10-28')
obs = ATCA_obs(target, tzinfo='Australia/Sydney', portal_htmls=portal_htmls)

fig, ax = obs.plot_target_altitude_with_schedule(t, duration=timedelta(days=10), dateformat='%D-%H:%M')
fig, ax = obs.plot_single_observability_heatmap(t, days=7, target_index=0)
```
By default, we observe in Australia/Sydney timezone. All the time in the plot is based on the `tzinfo` when you initiate your ATCA_obs object

There is `timezone` information in the schedule, we've already considered that in the code.
