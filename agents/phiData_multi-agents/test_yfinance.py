import yfinance as yf

print("Testing TSLA data...")
tsla = yf.Ticker("TSLA")

# Try getting basic info first
print("\nBasic Info:")
print(tsla.info)

print("\nTesting NVDA data...")
nvda = yf.Ticker("NVDA")
print("\nBasic Info:")
print(nvda.info)
