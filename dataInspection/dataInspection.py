import pandas as pd
import numpy as np

# %% 
rssi = pd.read_csv("data/rssi.csv")
rssi = rssi.drop(['AreaNumber', 'Track', 'Position', 'ID'], axis='columns')
rssi.rename(columns={'PositionNoLeap':'Position'}, inplace=True)
# deltas
rssi['deltaTel'] = rssi.A2_TotalTel.diff()
rssi.loc[0, 'deltaTel'] = 0
rssi.loc[rssi.deltaTel > 11, 'deltaTel'] = 5
rssi.loc[rssi.deltaTel < 0, 'deltaTel'] = 0

rssi['deltaValidTel'] = rssi.A2_ValidTel.diff()
rssi.loc[0, 'deltaValidTel'] = 0
rssi.loc[rssi.deltaValidTel > 11, 'deltaValidTel'] = 5
rssi.loc[rssi.deltaValidTel < 0, 'deltaValidTel'] = 0

rssi['telLoss'] = rssi.deltaTel - rssi.deltaValidTel

# %%
velo = pd.read_csv("data/velocities.csv")
velo = velo.drop(['EmergencyStopLimit', 'ID'], axis='columns')
velo.rename(columns={'CurrentVelocity': 'Velocity'}, inplace=True)
velo = velo.loc[velo.Velocity!=0]

# %%
disr = pd.read_csv("data/disruptions.csv")
disr.loc[disr["DisruptionCode"]==960862267, ["Description"]] = "Zwangsbremse wurde aktiviert"
disr.loc[disr["DisruptionCode"]==960862258, ["Description"]] = "Keine Linienleitertelegramme empfangen"

disr["disr_connection"] = False
disr.loc[disr.DisruptionCode == 960862258, "disr_connection"] = True

disr["disr_brake"] = False
disr.loc[disr.DisruptionCode == 960862267, "disr_brake"] = True

disr["disr_noPos"] = False
disr.loc[disr.DisruptionCode == 960862268, "disr_noPos"] = True

disr["disr_badCalibration"] = False
disr.loc[disr.DisruptionCode == 960862257, "disr_badCalibration"] = True

# %% merge datasets
df = pd.merge(rssi, velo, on='DateTime', how='inner')
df = pd.merge(df, disr.loc[disr.disr_connection==True,['DateTime', 'disr_connection']].drop_duplicates(),
              on='DateTime', how='outer')
df = pd.merge(df, disr.loc[disr.disr_brake==True,['DateTime', 'disr_brake']].drop_duplicates(),
              on='DateTime', how='outer')
df = pd.merge(df, disr.loc[disr.disr_noPos==True,['DateTime', 'disr_noPos']].drop_duplicates(),
              on='DateTime', how='outer')
df = pd.merge(df, disr.loc[disr.disr_badCalibration==True,['DateTime', 'disr_badCalibration']].drop_duplicates(),
              on='DateTime', how='outer', sort=True)
df.loc[df.disr_connection.isna(), 'disr_connection'] = False
df.loc[df.disr_brake.isna(), 'disr_brake'] = False

df.fillna(method='pad', inplace=True)
df.fillna(0, inplace=True)

# %% create path chunks
nChunks = 300
chunkSize =(df.Position.max()-df.Position.min()) // 300
print("Chunk Size: ", chunkSize)
df["posChunk"] = (df.Position-df.Position.min())+1
df.posChunk = (df.posChunk//chunkSize).astype(int)

# %% get subset where connection was lost and surounding data
idx = np.array(df.loc[df.disr_connection==True].index)
idx_ = idx.copy()
for i in range(-1, 6):
    print(i)
    if i==0:
        continue
    idx = np.append(idx, idx_ + i)

idx = np.unique(idx)
cols = ['DateTime', 'Position', 'Velocity',
        'disr_connection', 'disr_brake', 'posChunk']
badConnection_df = df.loc[idx, cols]

# %% mean per time-chunk in one position-chunk
chunkNr = 274
timeThresh = 30

df_c = df.loc[df.posChunk==chunkNr].copy()
df_c["chunkDeltaS"] = pd.to_datetime(df_c.DateTime).diff().dt.total_seconds()
df_c.loc[0, 'chunkDeltaS'] = 0

# create time groups
df_c['timeChunk'] = np.nan
df_c.loc[df_c.chunkDeltaS > timeThresh, 'timeChunk'] = np.arange((df_c.chunkDeltaS > timeThresh).sum())
df_c.timeChunk.fillna(method='pad', inplace=True)
df_c.fillna(0, inplace=True)

df_c['disr_connection_int'] = df_c.disr_connection.astype(int)*10

df_c.loc[:,['deltaValidTel', 'A2_RSSI', 'disr_connection_int', 'timeChunk']].groupby('timeChunk').mean().plot(figsize=(100,10))
