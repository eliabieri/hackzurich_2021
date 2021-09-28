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
# Create conda environment
conda env install
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
