# live_plot.py
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd

plt.style.use("dark_background")  # ✅ No seaborn needed


class LiveCandlePlot:
    def __init__(self, get_data_callback, get_labels_callback):
        self.get_data_callback = get_data_callback
        self.get_labels_callback = get_labels_callback

        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=1000)

    def update(self, frame):
        df = self.get_data_callback()
        if df.empty:
            print("No data yet")
            return

        self.ax.clear()
        self.ax.set_title("Live CRT Volatility Index Plot")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")

        df['timestamp'] = pd.to_datetime(df['epoch'], unit='s')
        self.ax.plot(df['timestamp'], df['close'], label='Close Price')

        labels = self.get_labels_callback()
        for label in labels:
            self.ax.axvline(x=pd.to_datetime(label['time'], unit='s'), color='red', linestyle='--')
            self.ax.text(pd.to_datetime(label['time'], unit='s'), label['price'], label['type'], color='red')

        self.ax.legend()

def start_plotting():
    plt.tight_layout()
    plt.show()
