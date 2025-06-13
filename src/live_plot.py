import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from deriv_ws import DerivLiveStreamer
from pattern_detector import CRTPatternDetector

class LiveCandlePlotter:
    def __init__(self, symbol):
        self.symbol = symbol
        self.candles = []
        self.detector = CRTPatternDetector(window_size=3)

        self.fig, self.ax = plt.subplots()
        plt.ion()
        self.fig.show()
        self.fig.canvas.draw()

    def on_new_candle(self, candle):
        self.candles.append(candle)
        if len(self.candles) > 50:
            self.candles.pop(0)

        pattern = self.detector.add_candle(candle)
        self.draw_chart(pattern)

    def draw_chart(self, pattern):
        self.ax.clear()

        dates = [mdates.date2num(c['timestamp']) for c in self.candles]
        opens = [c['open'] for c in self.candles]
        highs = [c['high'] for c in self.candles]
        lows = [c['low'] for c in self.candles]
        closes = [c['close'] for c in self.candles]

        width = 0.0008
        color_up = 'green'
        color_down = 'red'

        for i in range(len(self.candles)):
            color = color_up if closes[i] >= opens[i] else color_down
            self.ax.add_patch(Rectangle(
                (dates[i] - width/2, min(opens[i], closes[i])),
                width,
                abs(opens[i] - closes[i]),
                color=color,
                alpha=0.8
            ))
            self.ax.plot([dates[i], dates[i]], [lows[i], highs[i]], color=color)

        if pattern is not None:
            idx = len(self.candles) - 1
            candle = self.candles[idx]
            self.ax.add_patch(Rectangle(
                (dates[idx] - width/2, candle['low']),
                width,
                candle['high'] - candle['low'],
                edgecolor='blue',
                linewidth=2,
                fill=False
            ))
            self.ax.text(dates[idx], candle['high'], f"CRT {pattern['type']}",
                         color='blue', fontsize=10, fontweight='bold')

        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.set_title(f"Live candles for {self.symbol}")
        self.fig.autofmt_xdate()
        self.ax.set_ylabel("Price")
        self.fig.canvas.draw()
        plt.pause(0.01)

def main():
    symbol = "R_75"
    plotter = LiveCandlePlotter(symbol)
    streamer = DerivLiveStreamer(symbol, plotter.on_new_candle)
    streamer.start()

if __name__ == "__main__":
    main()
