## Disclaimer ⚠️
This code was written during a Hackathon. It's ugly, it's faulty and it's not save for consumption  
The challenge description is [here](doc/Workshop_Siemens_Mobility_20210924.pdf)   
The Devpost writeup can be found [here](https://devpost.com/software/zsl90-predictive-maintenance-platform)

## Installation

### Prerequisites
- [Conda](https://docs.anaconda.com/anaconda/install/index.html)
- [Flutter](https://flutter.dev/docs/get-started/install)

### Backend
```bash
# Create conda environment from the environment file
conda env create -f environment.yml
# Activate conda environment
conda activate hz_2021
# Run backend
./run.sh
```

### Frontend
```bash
# Change into frontend directory
cd frontend
# Start frontend in Browser
flutter run -d chrome
# Alternatively, run the frontend on MacOS natively
flutter run -d macOS
```
Since the frontend is written in Flutter it runs natively on iOS, Android, Web, Windows, MacOs and Linux.

**Note: The web version of the frontend currently does not support uploading new files!**

## Running an analysis
Our platform handles data as it comes from the trains, meaning, the three CSV files.     
As a starting point, the data from velocities_L01_D055.csv, rssi_L01_D055.csv, disruptions_L01_D055.csv is loaded.    
If new data is uploaded, the data is added to the previous data and an analysis is scheduled in the background.



## Algorithm

Using machine learning would be possible in theory, however, much more data would be needed. At the moment, only 138 incidents are available to learn from. If dozens of trains would provide the data over a longer period of time, it could be possible. But still, if a previously unseen problem arises, all the data can't help. For this type of data, we would then use a one dimensional convolutional neural network over the position dimension followed by a LSTM Network to analyse the the changes over time.

With the currently available data, only classical anomaly detection can be applied effectively. We believe that this can be very reliable however, as this method can 'learn' from the normal runs instead of the incidents. It was not that straight forward as it might seem. The code also has to be relatively efficient, as the dataset is quite large. 

First, the timeline is separated into individual rides. The position signal seems to be read from a GPS and can therefore have fluctuations and the train does necessarily always drive all the way to the last station. For this reason, we used the moving average of the derivative of the position to determine in which direction the train is moving and then separate the rides when the direction is changing. 

![dataOverview](.\doc\dataOverview.png)



Analysis of the incidents showed that the problem always occurred over a certain range on the track. This range could be represented using a gaussian curve, but instead we just cut the track into 300 chunks of ~100m length (faster and works probably just as well). Anomalies are then detected in each chunk using previously calculated mean and variance of voltage and package loss. Data from more recent rides is weighted more heavily to detect anomalies faster.

The results from all 300 sections are then send to the frontend. In addition, peaks are calculated if a outlier threshold (called "severance score" in the frontend) is reached. If multiple chunks reach the threshold in the range of 3km, only the one with the highest value is considered a peak. This peak values are also send to the frontend and visualized. When the threshold is reached only for the package loss but not for the voltage, it is assumed that is is likely a interference problem.

The threshold were determined using the 138 incidents in the dataset.
