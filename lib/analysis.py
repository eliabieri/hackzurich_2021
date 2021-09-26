from lib import constants
from dataclasses import dataclass
from enum import Enum
from typing import List
from datetime import datetime
import json
import time
import json

import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from scipy.special import expit

class AnomalyType(str, Enum):
    ANTENNA_DEGRADATION = "ANTENNA_DEGRADATION"
    INTERFERENCE = "INTERFERENCE"

@dataclass
class Anomaly:
    lat1: float
    lon1: float
    lat2: float
    lon2: float
    type: AnomalyType
    severeness: float
    distanceOnTrack: int
    peak: bool
    detectedOn: datetime = datetime.now()

class DataAnalyzer:

    @classmethod
    def analyzeData(cls) -> None:
        """This function shall analyze the events file and write the found
        anomalies to the anomalies file
        """
        print("Analysis in progress")
        nTimeChunks = 10
        distThresh = 30
        with open('dataInspection/mean_variance.json', "r") as f:
            mean_var = json.load(f)

        df = cls._mergeData(constants.VELOCITY_FILE, constants.RSSI_FILE, constants.DISRUPTIONS_FILE)
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
        
        # find peaks of anomalies:
        telPeaks = find_peaks(meanGroupVals.telDiff.values, height=1, distance=distThresh)
        rssiPeaks = find_peaks(meanGroupVals.rssiDiff.values, height=1, distance=distThresh)
        
        # check if telPeak is actually also a rssi peak
        peakDuplicate = []
        for tp in telPeaks[0]:
            if (np.abs(rssiPeaks[0]-tp) < (distThresh/distThresh)).any():
                peakDuplicate.append(tp)
        
        meanGroupVals['telDiff'] = expit(meanGroupVals.telDiff)*2  -1
        meanGroupVals['rssiDiff'] = expit(meanGroupVals.rssiDiff)*2 -1
        
        anomalies: List[Anomaly] = []
        for idx, row in meanGroupVals.iterrows():
            dfC = df.loc[(df.posChunk == idx)]
            an = Anomaly(
                    lat1 = dfC.loc[dfC.Position == dfC.Position.min(), 'Latitude'].values[0],
                    lon1 = dfC.loc[dfC.Position == dfC.Position.min(), 'Longitude'].values[0],
                    lat2 = dfC.loc[dfC.Position == dfC.Position.max(), 'Latitude'].values[0],
                    lon2 = dfC.loc[dfC.Position == dfC.Position.max(), 'Longitude'].values[0],
                    type = AnomalyType.ANTENNA_DEGRADATION,
                    severeness = np.sum(row.values)/2,
                    distanceOnTrack = dfC.Position.mean(),
                    peak=False,
                        )
            if (idx in telPeaks) and (idx not in peakDuplicate):
                an.type = AnomalyType.INTERFERENCE
                an.peak = True
            
            if idx in rssiPeaks:
                an.peak = True
            
            anomalies.append(an)
            
        
        print("Analysis finished")
        cls._writeAnomalyFile(anomalies)

    @staticmethod
    def _writeAnomalyFile(anomalies: List[Anomaly]) -> None:
        with constants.ANOMALIES_FILE.open("w") as f:
            ## Ugly hack to serialize dataclass
            f.write(json.dumps({
                "anomalies": [{
                    "lat1": anomaly.lat1,
                    "lon1": anomaly.lon1,
                    "lat2": anomaly.lat2,
                    "lon2": anomaly.lon2,
                    "type": anomaly.type,
                    "peak": anomaly.peak,
                    "severeness": anomaly.severeness,
                    "distanceOnTrack": anomaly.distanceOnTrack,
                    "detectedOn": anomaly.detectedOn.isoformat(),
                } for anomaly in anomalies]
            }))
    
    @staticmethod
    def _mergeData(rssiPath, veloPath, disrPath):
        rssi = pd.read_csv(rssiPath)
        rssi = rssi.loc[:, ['DateTime', 'PositionNoLeap','Latitude', 'Longitude',
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
    
