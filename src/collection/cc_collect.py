#!/usr/bin/env python
from crypto_analytics.data_source import CryptoCompareOHLCV
from crypto_analytics.types import Interval
from crypto_analytics.types.symbol import Symbol, SymbolPair

# interval = Interval(input('Interval: '))
# fsym = input('Symbols: ')
# tsym = input('Convert Symbols: ')
# limit = input('Limit: ')
# output_file = input('CSV file path: ')

interval = Interval.MINUTE
pair = SymbolPair(Symbol.BITCOIN, Symbol.USD)
rows = 60
output_file = 'cc_collect_data.csv'

candles = CryptoCompareOHLCV(interval, pair, rows)
candles.validated_fetch()
print(candles.data)
print('time:', candles.time.head(), sep='\n')
print('open:', candles.open.head(), sep='\n')
print('high:', candles.high.head(), sep='\n')
print('low:', candles.low.head(), sep='\n')
print('close:', candles.close.head(), sep='\n')
print('volume:', candles.volume.head(), sep='\n')
candles.write(output_file)
