import MetaTrader5 as mt5

# Inicie a conexão com o terminal MT5
if not mt5.initialize():
    print("Erro na inicialização", mt5.last_error())
    quit()

# Especifique o par de moedas ou instrumento e o timeframe
symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M1  # gráfico de 1 minuto

# Obtenha os dados
rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)

print(rates)

# Feche a conexão com o MT5
mt5.shutdown()