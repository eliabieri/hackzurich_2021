# -*- coding: utf-8 -*-
import json, time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta

from scipy.signal import find_peaks
from scipy.special import expit

def mergeData(rssi, velo, disr):
    rssi = rssi.loc[:, ['DateTime', 'PositionNoLeap', 'Latitude', 'Longitude',
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
    velo = velo.drop(['EmergencyStopLimit', 'ID'], axis='columns')
    velo.rename(columns={'CurrentVelocity': 'Velocity'}, inplace=True)
    velo = velo.loc[velo.Velocity!=0]
    
    #  disruptions
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
    # print("Number of time chunks: ", (df.Direction.diff() != 0).sum())
    return df

# %%
deltaDays = 2

rssi = pd.read_csv("data/rssi.csv")
rssi_dt = pd.to_datetime(rssi.DateTime)
finalTime = rssi_dt.iloc[-1] 
rssi_dt = finalTime - rssi_dt

velo = pd.read_csv("data/velocities.csv")
velo_dt = pd.to_datetime(velo.DateTime)
velo_dt = finalTime - velo_dt

disr = pd.read_csv("data/disruptions.csv")
disr_dt = pd.to_datetime(disr.DateTime)
disr_dt = finalTime - disr_dt

with open('dataInspection/mean_variance.json', "r") as f:
    mean_var = json.load(f)

# %%

plt.ion()
for minDay in range(100, 1, -1):
    print("Day: ", -minDay)
    for hour in range(22, 2, -4):
        
        minTime = timedelta(days=minDay, hours=hour)
        maxTime = timedelta(days=deltaDays + minDay, hours=hour)
        rssi_sub = rssi.loc[(rssi_dt > minTime)&(rssi_dt<maxTime)]
        velo_sub= velo.loc[(velo_dt > minTime)&(velo_dt<maxTime)]
        disr_sub = disr.loc[(disr_dt > minTime)&(disr_dt<maxTime)]
        
        df = mergeData(rssi_sub.copy(), velo_sub.copy(), disr_sub.copy())
        
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
        
        meanGroupVals['telDiff'] = expit(meanGroupVals.telDiff)*2  -1
        meanGroupVals['rssiDiff'] = expit(meanGroupVals.rssiDiff)*2 -1
        
        meanGroupVals.plot(ylim=(0,1), title=f'day {-minDay}, h {-hour}', figsize=(14,8))
        plt.show()
        # time.sleep(1)
        
        # %% find peaks of anomalies:
        telPeaks = find_peaks(meanGroupVals.telDiff.values, height=1, distance=30)
        rssiPeaks = find_peaks(meanGroupVals.rssiDiff.values, height=1, distance=30)
        
        # check if telPeak is actually also a rssi peak
        peakDuplicate = []
        for tp in telPeaks[0]:
            if (np.abs(rssiPeaks[0]-tp) < 15).any():
                peakDuplicate.append(tp)
