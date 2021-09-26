from lib import constants
from dataclasses import dataclass
from enum import Enum
from typing import List
from datetime import datetime
import json
import time

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
        events = constants.EVENTS_FILE.open()
        disruptions = constants.DISRUPTIONS_FILE.open()
        events = constants.EVENTS_FILE.open()
        print("Analysis in progress")
        time.sleep(4)
        print("Analysis finished")
        ## TODO analysis
        anomalies: List[Anomaly] = []
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
