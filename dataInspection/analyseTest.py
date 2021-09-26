import json

import pandas as pd
import numpy as np
from scipy.signal import find_peaks

# %% import mean an variance values
with open('dataInspection/mean_variance.json', "r") as f:
    mean_var = json.load(f)

# %% import rssi
def mergeData(rssiPath, veloPath, disrPath):
    rssi = pd.read_csv(rssiPath)
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
    
    # import velocities
    velo = pd.read_csv(veloPath)
    velo = velo.drop(['EmergencyStopLimit', 'ID'], axis='columns')
    velo.rename(columns={'CurrentVelocity': 'Velocity'}, inplace=True)
    velo = velo.loc[velo.Velocity!=0]
    
    #  disruptions
    disr = pd.read_csv(disrPath)
    disr.loc[disr["DisruptionCode"]==960862267, ["Description"]] = "Zwangsbremse wurde aktiviert"
    disr.loc[disr["DisruptionCode"]==960862258, ["Description"]] = "Keine Linienleitertelegramme empfangen"
    
    disr["disr_connection"] = False
    disr.loc[disr.DisruptionCode == 960862258, "disr_connection"] = True
    
    # merge datasets
    df = pd.merge(rssi, velo, on='DateTime', how='inner')
    df = pd.merge(df, disr.loc[disr.disr_connection==True,['DateTime', 'disr_connection']].drop_duplicates(),
                  on='DateTime', how='outer', sort=True)
    df.loc[df.disr_connection.isna(), 'disr_connection'] = False
    
    df.fillna(method='pad', inplace=True)
    df.fillna(0, inplace=True)
    
    # create path chunks
    nChunks = 300
    chunkSize =(df.Position.max()-df.Position.min()) // 300
    print(f'Chunk Size: {chunkSize/10} m')
    df["posChunk"] = (df.Position-df.Position.min())+1
    df.posChunk = (df.posChunk//chunkSize).astype(int)
    
    # create time chunks
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
    return df

deltaDays = 1
rssiPath = f"data/rssi_L{deltaDays:02d}.csv"
veloPath = f"data/velocities_L{deltaDays:02d}.csv"
disrPath = f"data/disruptions_L{deltaDays:02d}.csv"
df = mergeData(rssiPath, veloPath, disrPath)

# %% get Mean per group
nTimeChunks = 10

df['telDiff'] = df.deltaValidTel - mean_var['tel_mean']
df['rssiDiff'] = df.RSSI - mean_var['RSSI_mean']
meanGroupVals = df.loc[:,['telDiff', 'rssiDiff','TimeChunk', 'posChunk']].groupby(['TimeChunk', 'posChunk']).mean()

meanGroupVals['telDiff'] = meanGroupVals['telDiff'] / np.sqrt(mean_var['tel_var'])
meanGroupVals['rssiDiff'] = meanGroupVals['rssiDiff'] / np.sqrt(mean_var['RSSI_var'])

timeChunks = pd.Series(meanGroupVals.index.get_level_values(0))
timeChunks = timeChunks- timeChunks.max() + nTimeChunks
timeChunks.loc[timeChunks < 0] = 0

meanGroupVals['telDiff'] = (meanGroupVals.telDiff * timeChunks.values).abs()
meanGroupVals['rssiDiff'] = (meanGroupVals.rssiDiff * timeChunks.values).abs()
meanGroupVals = meanGroupVals.groupby(level=1).mean()/nTimeChunks
meanGroupVals.loc[0:1] = 0

# %% find peaks of anomalies:
telPeaks = find_peaks(meanGroupVals.telDiff.values, height=1, distance=30)
rssiPeaks = find_peaks(meanGroupVals.rssiDiff.values, height=1, distance=30)