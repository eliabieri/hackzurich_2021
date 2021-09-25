import json, pathlib

import pandas as pd
import numpy as np

# %% 
rssi = pd.read_csv("data/rssi.csv")
rssi = rssi.loc[:, ['DateTime', 'PositionNoLeap',
                    'A1_ValidTel', 'A2_ValidTel', 'A2_RSSI']]
rssi.rename(columns={'PositionNoLeap':'Position'}, inplace=True)

# deltas
rssi['RSSI'] = rssi.A2_RSSI
rssi['deltaValidTel'] = (rssi.A1_ValidTel + rssi.A2_ValidTel).diff()
rssi.loc[0, 'deltaValidTel'] = 0
rssi.loc[rssi.deltaValidTel > 11, 'deltaValidTel'] = 5
rssi.loc[rssi.deltaValidTel < 0, 'deltaValidTel'] = 0

rssi.drop(['A2_RSSI', 'A1_ValidTel', 'A2_ValidTel'],
          axis='columns',
          inplace=True)

# %% import velocities
velo = pd.read_csv("data/velocities.csv")
velo = velo.drop(['EmergencyStopLimit', 'ID'], axis='columns')
velo.rename(columns={'CurrentVelocity': 'Velocity'}, inplace=True)
velo = velo.loc[velo.Velocity!=0]

# %% disruptions
disr = pd.read_csv("data/disruptions.csv")
disr.loc[disr["DisruptionCode"]==960862267, ["Description"]] = "Zwangsbremse wurde aktiviert"
disr.loc[disr["DisruptionCode"]==960862258, ["Description"]] = "Keine Linienleitertelegramme empfangen"

disr["disr_connection"] = False
disr.loc[disr.DisruptionCode == 960862258, "disr_connection"] = True

# %% merge datasets
df = pd.merge(rssi, velo, on='DateTime', how='inner')
df = pd.merge(df, disr.loc[disr.disr_connection==True,['DateTime', 'disr_connection']].drop_duplicates(),
              on='DateTime', how='outer', sort=True)
df.loc[df.disr_connection.isna(), 'disr_connection'] = False

df.fillna(method='pad', inplace=True)
df.fillna(0, inplace=True)

# %% create path chunks
nChunks = 300
chunkSize =(df.Position.max()-df.Position.min()) // 300
print(f'Chunk Size: {chunkSize/10} m')
df["posChunk"] = (df.Position-df.Position.min())+1
df.posChunk = (df.posChunk//chunkSize).astype(int)

# %% create time chunks
# get signed speed
df["deltaS"] = pd.to_datetime(df.DateTime).diff().dt.total_seconds()
df.loc[df.deltaS.isna(), 'deltaS']=0

df["Position_D"] = df.Position.diff()/10000 / df.deltaS * 3600
df["Position_D"] = df.Position_D.rolling(window=300).mean()


# get direction
df["Direction"] = 0
df.loc[df.Position_D > 0, 'Direction'] = 1
df.loc[df.Position_D < 0, 'Direction'] = -1
df['TimeChunk'] = np.nan
df.loc[df.Direction.diff() != 0, 'TimeChunk'] = np.arange((df.Direction.diff() != 0).sum())
df.TimeChunk.fillna(method='pad', inplace=True)
df.TimeChunk.fillna(0, inplace=True)
print("Number of time chunks: ", (df.Direction.diff() != 0).sum())

# %% get mean and variance
meanGroupVals = df.loc[:,['deltaValidTel', 'RSSI','TimeChunk', 'posChunk']].groupby(['TimeChunk', 'posChunk']).mean()
meanGroupVals.plot(figsize=(120,10))

RSSI_mean = meanGroupVals.RSSI.mean()
tel_mean = meanGroupVals.deltaValidTel.mean()
RSSI_var = meanGroupVals.RSSI.var()
tel_var = meanGroupVals.deltaValidTel.var()

with pathlib.Path('dataInspection/mean_variance.json').open('w') as f:
    f.write(json.dumps({'RSSI_mean' : RSSI_mean,
                        'tel_mean' : tel_mean,
                        'RSSI_var' : RSSI_var,
                        'tel_var' : tel_var}, indent=4))
