import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
from datetime import datetime
import threading

candles_buffer = []
levels_buffer = []
buffer_lock = threading.Lock()

def add_candle(candle):
    with buffer_lock:
        candles_buffer.append(candle)
        if len(candles_buffer) > 200:
            candles_buffer.pop(0)

def add_level(entry, sl, tp):
    with buffer_lock:
        levels_buffer.append((entry, sl, tp))
        if len(levels_buffer) > 10:
            levels_buffer.pop(0)

def update_plot(frame):
    with buffer_lock:
        if not candles_buffer:
            return

        timestamps = [c["timestamp"] for c in candles_buffer]
        dates = mdates.date2num(timestamps)

        fig.clf()
        ax = fig.add_subplot(1, 1, 1)

        for i in range(len(candles_buffer)):
            c = candles_buffer[i]
            color = "green" if c["close"] >= c["open"] else "red"
            ax.plot([dates[i], dates[i]], [c["low"], c["high"]], color=color)
            ax.add_patch(
                plt.Rectangle(
                    (dates[i] - 0.1, min(c["open"], c["close"])),
                    0.2,
                    abs(c["close"] - c["open"]),
                    color=color
                )
            )

        # Plot SL/TP lines
        for entry, sl, tp in levels_buffer:
            ax.axhline(y=entry, color="blue", linestyle="--", label="Entry")
            ax.axhline(y=sl, color="orange", linestyle="--", label="SL")
            ax.axhline(y=tp, color="purple", linestyle="--", label="TP")

        ax.set_title("🔴 Bearish | 🟢 Bullish | CRT Live 4H Candles")
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
        fig.autofmt_xdate()
        ax.grid(True)

def start_plotting():
    global fig
    fig = plt.figure()
    ani = FuncAnimation(fig, update_plot, interval=3000)
    plt.show()
