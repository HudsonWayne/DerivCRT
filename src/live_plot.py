import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading

candles_buffer = []
buffer_lock = threading.Lock()

def add_candle(candle):
    with buffer_lock:
        candles_buffer.append(candle)
        if len(candles_buffer) > 100:
            candles_buffer.pop(0)

def update_plot(frame):
    with buffer_lock:
        if not candles_buffer:
            return
        timestamps = [c['timestamp'].strftime("%H:%M:%S") for c in candles_buffer]
        closes = [c['close'] for c in candles_buffer]
    
    plt.cla()
    plt.plot(timestamps, closes, label='Close Price')
    plt.title("Live CRT Chart (Close Prices)")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()

def start_plotting():
    fig = plt.figure()
    ani = FuncAnimation(fig, update_plot, interval=1000)
    plt.show()
