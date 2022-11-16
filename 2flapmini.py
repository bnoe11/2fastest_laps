"""
This Project is largely inspired by Jasper on medium
https://medium.com/towards-formula-1-analysis/formula-1-data-analysis-tutorial-2021-russian-gp-to-box-or-not-to-box-da6399bd4a39

"""

import matplotlib.pyplot as plt
import fastf1 as ff1

from fastf1 import plotting
import numpy as np
import pandas as pd
from matplotlib.pyplot import figure
from matplotlib import cm
from matplotlib.collections import LineCollection
import warnings
warnings.filterwarnings("ignore")

plotting.setup_mpl()
ff1.Cache.enable_cache('Cache')

pd.options.mode.chained_assignment = None

session = ff1.get_session(2022, 'Saudi Arabia', 'Race')
session.load()

driver1 = "LEC"
driver2 = "VER"

d1 = session.laps.pick_driver(driver1).pick_fastest()
d2 = session.laps.pick_driver(driver2).pick_fastest()

tel1 = d1.get_telemetry().add_distance()
tel2 = d2.get_telemetry().add_distance()

tel1['Driver'] = driver1
tel2['Driver'] = driver2

telemetry = pd.DataFrame()

telemetry = telemetry.append(tel1)
telemetry = telemetry.append(tel2)

n_minisec = 25
total_distance = max(telemetry['Distance'])
minisec_len = total_distance / n_minisec
minisectors = [0]

for i in range(1, n_minisec):
    minisectors.append(minisec_len * (i))

telemetry['Minisector'] = telemetry['Distance'].apply(
    lambda z: (
        minisectors.index(
            min(minisectors, key = lambda x: abs(x-z))) + 1
        )
    )


avg_speed = telemetry.groupby(['Minisector','Driver'])['Speed'].mean().reset_index()
fastest_driver = avg_speed.loc[avg_speed.groupby(['Minisector'])['Speed'].idxmax()]
fastest_driver = fastest_driver[['Minisector','Driver']].rename(columns={'Driver': 'Fastest_driver'})

telemetry = telemetry.merge(fastest_driver, on=['Minisector'])
telemetry = telemetry.sort_values(by=['Distance'])

telemetry.loc[telemetry['Fastest_driver'] ==  driver1, 'Fastest_driver_int'] = 1
telemetry.loc[telemetry['Fastest_driver'] ==  driver2, 'Fastest_driver_int'] = 2

print(telemetry.columns)

#Change the graph to be a legend instead of a colorbat
#figure out a way to change the colors of the graph
def minisector_plot(save=False, details=True):
    x = np.array(telemetry['X'].values)
    y = np.array(telemetry['Y'].values)

    points = np.array([x,y]).T.reshape(-1,1,2)
    segments = np.concatenate([points[:-1], points[1:]], axis = 1)
    driverlap = telemetry['Fastest_driver_int'].to_numpy().astype(float)

    cmap = cm.get_cmap('RdYlBu', 2) #change to driver colors
    lc_driv = LineCollection(segments, norm=plt.Normalize(1,cmap.N+1), cmap=cmap)
    lc_driv.set_array(driverlap)
    lc_driv.set_linewidth(2)
    

    plt.rcParams['figure.figsize'] = [10,5]

    if details:
        title = plt.suptitle(f"2022 Saudi Arabian GP - Fastest Minisectors\n@bnoebnoe | @ur_sac")
    
    plt.gca().add_collection(lc_driv)
    plt.axis('equal')
    plt.tick_params(labelleft=False,left=False,labelbottom=False,bottom=False)

    if details:
        cbar = plt.colorbar(mappable=lc_driv, boundaries=np.arange(1,4))
        cbar.set_ticks(np.arange(1.5,3.5)) # research this
        cbar.set_ticklabels([driver1, driver2]) #replace with driver names

    if save:
        plt.savefig(f"img/fastest_minisectors_flap.png", dpi = 300)

    plt.show()



minisector_plot(save = False, details = True)