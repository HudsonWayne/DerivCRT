import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation
import threading
import queue
import random
import time

class LivePlotter:
    def __init__(self):
        self.candles = []  # Will hold dicts with keys: timestamp, open, high, low, close
        self.data_queue = queue.Queue()

        # Setup plot
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Live Candlestick Chart")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")

        # Format date axis
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.fig.autofmt_xdate()

    def add_candle(self, candle):
        """Add candle data (from websocket or simulator)"""
        self.data_queue.put(candle)

    def process_queue(self):
        while not self.data_queue.empty():
            candle = self.data_queue.get()
            self.candles.append(candle)

        # Keep only last 50 candles for performance
        self.candles = self.candles[-50:]

    def draw_chart(self):
        self.ax.clear()
        self.ax.set_title("Live Candlestick Chart")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.fig.autofmt_xdate()

        if not self.candles:
            return

        dates = []
        opens = []
        highs = []
        lows = []
        closes = []

        for c in self.candles:
            ts = c['timestamp']
            # Convert if needed
            if isinstance(ts, (int, float)):
                dt = datetime.datetime.fromtimestamp(ts)
            else:
                dt = ts  # already datetime
            dates.append(mdates.date2num(dt))
            opens.append(c['open'])
            highs.append(c['high'])
            lows.append(c['low'])
            closes.append(c['close'])

        width = 0.0005  # width for candle bodies in days

        for i in range(len(dates)):
            color = 'green' if closes[i] >= opens[i] else 'red'
            # Draw candle body
            self.ax.bar(dates[i], abs(closes[i] - opens[i]), width, bottom=min(opens[i], closes[i]), color=color)
            # Draw wick (high-low line)
            self.ax.vlines(dates[i], lows[i], highs[i], color=color)

    def update(self, frame):
        self.process_queue()
        self.draw_chart()

def simulate_data(plotter):
    """Simulate candle data and send to plotter"""
    base_price = 100000
    while True:
        now = datetime.datetime.now()
        open_p = base_price + random.uniform(-50, 50)
        close_p = open_p + random.uniform(-50, 50)
        high_p = max(open_p, close_p) + random.uniform(0, 20)
        low_p = min(open_p, close_p) - random.uniform(0, 20)

        candle = {
            'timestamp': now,
            'open': open_p,
            'high': high_p,
            'low': low_p,
            'close': close_p
        }

        plotter.add_candle(candle)
        base_price = close_p
        time.sleep(1)  # New candle every second (for demo)

def run_plotter():
    plotter = LivePlotter()

    # Start data simulator in separate thread
    t = threading.Thread(target=simulate_data, args=(plotter,), daemon=True)
    t.start()

    ani = animation.FuncAnimation(plotter.fig, plotter.update, interval=1000)
    plt.show()

if __name__ == "__main__":
    run_plotter()
