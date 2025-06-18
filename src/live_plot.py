import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle

class LiveCandlePlot:
    def __init__(self, get_candles_callback, get_trade_signals_callback=None):
        self.get_candles = get_candles_callback
        self.get_trade_signals = get_trade_signals_callback
        self.fig, self.ax = plt.subplots(figsize=(14, 6))
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=2000, cache_frame_data=False)

    def update(self, frame):
        candles = self.get_candles()
        if not candles:
            return
        self.ax.clear()
        x = range(len(candles))
        opens = [c['open'] for c in candles]
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        closes = [c['close'] for c in candles]

        for i in x:
            color = 'green' if closes[i] >= opens[i] else 'red'
            self.ax.vlines(i, lows[i], highs[i], color=color)
            self.ax.add_patch(Rectangle((i - 0.3, min(opens[i], closes[i])), 0.6, max(0.01, abs(closes[i] - opens[i])), color=color))

        signals = self.get_trade_signals() if self.get_trade_signals else []
        for s in signals:
            if s["type"] == "none":
                self.ax.text(0, max(highs), "🕵️ No valid CRT or breakout signal", fontsize=12, color='gray')
            else:
                i = s["entry_index"]
                self.ax.plot(i, s["entry_price"], marker="^" if s["type"] == "buy" else "v", color="blue", markersize=12)
                self.ax.text(i, s["entry_price"], f"{s['type'].upper()} SIGNAL", fontsize=10, color='navy', weight='bold')

        self.ax.set_title("🔥 Live CRT & Breakout Detector with Thank You Chart")
        self.ax.set_xlabel("4H Candle Index")
        self.ax.set_ylabel("Price")
        self.ax.text(0.9, 0.01, "Thank you for using CRT tracker 🚀", transform=self.ax.transAxes, fontsize=10, ha='right', color='green')
        self.fig.canvas.draw_idle()

    def show(self):
        plt.tight_layout()
        plt.show()
