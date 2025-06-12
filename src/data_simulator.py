import csv
import time
import threading
from datetime import datetime


class DataSimulator:
    def __init__(self, filepath, interval=1.0, callback=None):
        """
        :param filepath: Path to CSV file
        :param interval: Delay between candles (in seconds)
        :param callback: Function to call with each candle
        """
        self.filepath = filepath
        self.interval = interval
        self.callback = callback
        self._stop_event = threading.Event()

    def start(self):
        """Start the simulation in a new thread."""
        self._thread = threading.Thread(target=self._simulate_data)
        self._thread.start()

    def stop(self):
        """Stop the simulation."""
        self._stop_event.set()
        self._thread.join()

    def _simulate_data(self):
        """Internal method to simulate streaming data."""
        with open(self.filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if self._stop_event.is_set():
                    break

                # Convert values
                candle = {
                    'timestamp': datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                }

                if self.callback:
                    self.callback(candle)

                time.sleep(self.interval)
