from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
ANOMALIES_FILE = DATA_DIR / "anomalies.json"

DISRUPTIONS_FILE = DATA_DIR / "disruptions_L01_D055.csv"
RSSI_FILE = DATA_DIR / "rssi_L01_D055.csv"
VELOCITY_FILE = DATA_DIR / "velocities_L01_D055.csv"