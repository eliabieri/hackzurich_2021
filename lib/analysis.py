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
    lat: float
    lon: float
    type: AnomalyType
    severeness: float
    distanceOnTrack: int
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
        time.sleep(20)
        print("Analysis finished")
        ## TODO analysis
        anomalies: List[Anomaly] = [
            Anomaly(
                lat=47.39562302092118,
                lon=8.057479921589058,
                type=AnomalyType.ANTENNA_DEGRADATION,
                distanceOnTrack=49876,
                severeness=0.2
            ),
            Anomaly(
                lat=47.30757390295709,
                lon=8.080110130195234,
                type=AnomalyType.INTERFERENCE,
                distanceOnTrack=113095,
                severeness=0.8
            )
        ]
        cls._writeAnomalyFile(anomalies)

    @staticmethod
    def _writeAnomalyFile(anomalies: List[Anomaly]) -> None:
        with constants.ANOMALIES_FILE.open("w") as f:
            ## Ugly hack to serialize dataclass
            f.write(json.dumps({
                "anomalies": [{
                    "lat": anomaly.lat,
                    "lon": anomaly.lon,
                    "type": anomaly.type,
                    "severeness": anomaly.severeness,
                    "distanceOnTrack": anomaly.distanceOnTrack,
                    "detectedOn": anomaly.detectedOn.isoformat(),
                } for anomaly in anomalies]
            }))
