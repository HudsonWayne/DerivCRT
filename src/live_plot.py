import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle

class LiveCandlePlot:
    def __init__(self, get_candles_callback, get_trade_signals_callback=None):
        self.get_candles = get_candles_callback
        self.get_trade_signals = get_trade_signals_callback
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ani = animation.FuncAnimation(
            self.fig,
            self.update,
            interval=2000,
            cache_frame_data=False
        )
        self.last_signals = []

    def update(self, frame):
        candles = self.get_candles()
        if not candles:
            return

        self.ax.clear()

        opens = [c['open'] for c in candles]
        highs = [c['high'] for c in candles]
        lows = [c['low'] for c in candles]
        closes = [c['close'] for c in candles]
        x = range(len(candles))

        self.ax.set_xlim(-1, len(candles) + 1)
        min_low = min(lows)
        max_high = max(highs)
        margin = (max_high - min_low) * 0.15
        self.ax.set_ylim(min_low - margin, max_high + margin)

        # Draw candles
        for i in x:
            color = 'green' if closes[i] >= opens[i] else 'red'
            self.ax.vlines(i, lows[i], highs[i], color=color, linewidth=1)
            lower = min(opens[i], closes[i])
            height = abs(closes[i] - opens[i])
            height = height if height > 0 else 0.01
            rect = Rectangle((i - 0.3, lower), 0.6, height, color=color, alpha=0.8)
            self.ax.add_patch(rect)

        # Draw trade signals
        if self.get_trade_signals:
            signals = self.get_trade_signals()
            self.last_signals = signals

            buy_drawn = False
            sell_drawn = False
            for s in signals:
                i = s['entry_index']
                ep = s['entry_price']
                tp = s['tp_price']
                sl = s['sl_price']

                if s['type'] == 'buy':
                    self.ax.plot(i, ep, marker='^', color='lime', markersize=14, label='Buy' if not buy_drawn else "")
                    self.ax.plot(i, tp, marker='v', color='blue', markersize=10, label='Take Profit' if not buy_drawn else "")
                    self.ax.plot(i, sl, marker='x', color='black', markersize=10, label='Stop Loss' if not buy_drawn else "")
                    buy_drawn = True
                    # Draw text label
                    self.ax.text(i, ep, 'BUY', color='green', fontsize=10, fontweight='bold', verticalalignment='bottom')
                elif s['type'] == 'sell':
                    self.ax.plot(i, ep, marker='v', color='red', markersize=14, label='Sell' if not sell_drawn else "")
                    self.ax.plot(i, tp, marker='^', color='blue', markersize=10, label='Take Profit' if not sell_drawn else "")
                    self.ax.plot(i, sl, marker='x', color='black', markersize=10, label='Stop Loss' if not sell_drawn else "")
                    sell_drawn = True
                    self.ax.text(i, ep, 'SELL', color='red', fontsize=10, fontweight='bold', verticalalignment='top')

        # Add legend without duplicates
        handles, labels = self.ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        self.ax.legend(by_label.values(), by_label.keys())

        self.ax.set_title("Live 4H Volatility 75 Candlestick Chart with Advanced CRT Trades")
        self.ax.set_xlabel("Candle Index (4H)")
        self.ax.set_ylabel("Price")

        # Show last signals info on plot
        info_y = max_high + margin * 0.05
        for idx, s in enumerate(self.last_signals[-3:]):
            info_text = f"{s['description']}: {s['type'].upper()} @ {s['entry_price']:.2f}, TP: {s['tp_price']:.2f}, SL: {s['sl_price']:.2f}"
            self.ax.text(0, info_y + idx * margin * 0.1, info_text, fontsize=9, color='navy', fontweight='bold')

        self.fig.canvas.draw_idle()

    def show(self):
        plt.tight_layout()
        plt.show()
