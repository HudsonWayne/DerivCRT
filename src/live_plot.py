import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading

# Thread-safe candle buffer
candles_buffer = []
buffer_lock = threading.Lock()

def add_candle(candle):
    with buffer_lock:
        candles_buffer.append(candle)
        # Optional: keep last N candles only
        if len(candles_buffer) > 100:
            candles_buffer.pop(0)

def update_plot(frame):
    with buffer_lock:
        if not candles_buffer:
            return

        timestamps = [c['timestamp'] for c in candles_buffer]
        opens = [c['open'] for c in candles_buffer]
        highs = [c['high'] for c in candles_buffer]
        lows = [c['low'] for c in candles_buffer]
        closes = [c['close'] for c in candles_buffer]

    plt.cla()  # Clear current axes

    # Plot close price line
    plt.plot(timestamps, closes, label='Close Price')

    plt.title('Live Candle Close Prices')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

def start_plotting():
    fig = plt.figure()
    ani = FuncAnimation(fig, update_plot, interval=1000, save_count=100)
    plt.show()
