### Code for semi-automatically loading ATCA schedule and checking for the green time

```
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
```
