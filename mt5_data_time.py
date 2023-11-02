# python_mt5_timing.py

import MetaTrader5 as mt5
import time

mt5.initialize()

start_time = time.time()


for _ in range(1,10):
    tick = mt5.symbol_info_tick("EURUSD")
    price_b = tick.bid
    price_a = tick.ask
    volume = tick.volume
    print(price_b,price_a, volume)

end_time = time.time()

mt5.shutdown()

print(f"Tempo usando Python com MetaTrader5: {end_time - start_time:.9f} segundos")
