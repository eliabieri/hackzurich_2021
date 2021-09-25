import pandas as pd
import numpy as np

# %% 
rssi = pd.read_csv("data/rssi.csv")
rssi = rssi.drop(['AreaNumber', 'Track', 'Position'], axis='columns')


velo = pd.read_csv("data/velocities.csv")
velo = velo.drop('EmergencyStopLimit', axis='columns')

disr = pd.read_csv("data/disruptions.csv")
disr.loc[disr["DisruptionCode"]==960862267, ["Description"]] = "Zwangsbremse wurde aktiviert"
disr.loc[disr["DisruptionCode"]==960862258, ["Description"]] = "Keine Linienleitertelegramme empfangen"

# %% merge datasets
df = pd.merge(rssi, velo, on='DateTime', how='outer', sort=True)
