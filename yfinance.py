import yfinance as yf
import mplfinance as mpf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_imbalance(data, fill_amount):
    fig, ax = mpf.plot(data, type='candle', style='yahoo', volume=True, returnfig=True)
   
    imbalance_areas = []
    current_imbalance = None
   
    for i in range(len(data)):
        if current_imbalance is not None:
            if (current_imbalance['type'] == 'bullish' and data['Close'].iloc[i] < current_imbalance['high']) or \
               (current_imbalance['type'] == 'bearish' and data['Close'].iloc[i] > current_imbalance['low']):
                if (current_imbalance['high'] - current_imbalance['low']) * fill_amount <= abs(data['Close'].iloc[i] - current_imbalance['high' if current_imbalance['type'] == 'bullish' else 'low']):
                    current_imbalance = None
                else:
                    continue
       
        if current_imbalance is None:
            if data['Close'].iloc[i] > data['Open'].iloc[i]:
                current_imbalance = {'type': 'bullish', 'low': data['Low'].iloc[i], 'high': data['High'].iloc[i]}
            elif data['Close'].iloc[i] < data['Open'].iloc[i]:
                current_imbalance = {'type': 'bearish', 'low': data['Low'].iloc[i], 'high': data['High'].iloc[i]}
       
        if current_imbalance is not None:
            imbalance_areas.append(current_imbalance)
   
    for imbalance in imbalance_areas:
        rect = patches.Rectangle((data.index.get_loc(data[data['Low'] == imbalance['low']].index[0]), imbalance['low']),
                                 len(data[data['Low'] == imbalance['low']]),
                                 imbalance['high'] - imbalance['low'],
                                 color='green' if imbalance['type'] == 'bullish' else 'red',
                                 alpha=0.5)
        ax[0].add_patch(rect)
   
    plt.show()

data = yf.download('NQ=F', period='5d', interval='30m')
plot_imbalance(data, fill_amount=0.5)
