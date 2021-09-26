from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
ANOMALIES_FILE = DATA_DIR / "anomalies.json"

EVENTS_FILE = DATA_DIR / "events.csv"
DISRUPTIONS_FILE = DATA_DIR / "disruptions_L01.csv"
RSSI_FILE = DATA_DIR / "rssi_L01.csv"
VELOCITY_FILE = DATA_DIR / "velocities_L01.csv"