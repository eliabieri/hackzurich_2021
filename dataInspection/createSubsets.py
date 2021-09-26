# -*- coding: utf-8 -*-
import pandas as pd
from datetime import timedelta

deltaDays = 3
minTime = timedelta(days=deltaDays)

rssi = pd.read_csv("data/rssi.csv")
rssi_dt = pd.to_datetime(rssi.DateTime)
finalTime = rssi_dt.iloc[-1] 

rssi_dt = finalTime - rssi_dt
rssi.loc[rssi_dt < minTime].to_csv(f"data/rssi_L{deltaDays:02d}.csv")

# %%
velo = pd.read_csv("data/velocities.csv")
velo_dt = pd.to_datetime(velo.DateTime)

velo_dt = finalTime - velo_dt
velo.loc[velo_dt < minTime].to_csv(f"data/velocities_L{deltaDays:02d}.csv")

# %%
disr = pd.read_csv("data/disruptions.csv")
disr_dt = pd.to_datetime(disr.DateTime)

disr_dt = finalTime - disr_dt
disr.loc[disr_dt < minTime].to_csv(f"data/disruptions_L{deltaDays:02d}.csv")
