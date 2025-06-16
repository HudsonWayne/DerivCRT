import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from datetime import datetime

plt.style.use("dark_background")  # ✅ FIXED: Changed from 'seaborn-dark-palette'

class LiveCandlePlot:
    def __init__(self, get_data_callback=None, get_labels_callback=None):
        self.get_data_callback = get_data_callback
        self.get_labels_callback = get_labels_callback
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=1000)

    def update(self, frame):
        self.ax.clear()

        if self.get_data_callback is None:
            return

        df = self.get_data_callback()
        if df.empty:
            return

        # Convert epoch to datetime
        df["time"] = pd.to_datetime(df["epoch"], unit="s")

        # Plot candlesticks
        for i in range(len(df)):
            o = df.iloc[i]["open"]
            h = df.iloc[i]["high"]
            l = df.iloc[i]["low"]
            c = df.iloc[i]["close"]
            t = df.iloc[i]["time"]
            color = "green" if c >= o else "red"
            self.ax.plot([t, t], [l, h], color=color, linewidth=1.5)
            self.ax.plot([t, t], [o, c], color=color, linewidth=6)

        # Optional: annotate patterns like Accumulation, Manipulation, Distribution
        if self.get_labels_callback:
            labels = self.get_labels_callback()
            for lbl in labels:
                idx = lbl["index"]
                text = lbl["label"]
                if idx < len(df):
                    candle_time = df.iloc[idx]["time"]
                    candle_close = df.iloc[idx]["close"]
                    self.ax.text(candle_time, candle_close, text, fontsize=9, color='yellow', ha='center')

        self.ax.set_title("Live CRT Candlestick Chart (4H)")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")
        self.ax.grid(True)

    def show(self):
        plt.tight_layout()
        plt.show()
