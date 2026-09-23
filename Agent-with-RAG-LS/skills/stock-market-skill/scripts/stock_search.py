import random
import datetime

SAMPLE_STOCKS = [
    {"ticker": "NVDA", "name": "NVIDIA Corp", "price": 128.50, "change_pct": 5.42, "category": "Tech"},
    {"ticker": "AAPL", "name": "Apple Inc", "price": 224.30, "change_pct": 2.15, "category": "Tech"},
    {"ticker": "MSFT", "name": "Microsoft Corp", "price": 448.90, "change_pct": 1.84, "category": "Tech"},
    {"ticker": "AMZN", "name": "Amazon.com Inc", "price": 186.20, "change_pct": -0.75, "category": "Consumer"},
    {"ticker": "GOOGL", "name": "Alphabet Inc", "price": 179.40, "change_pct": 3.10, "category": "Tech"},
    {"ticker": "TSLA", "name": "Tesla Inc", "price": 254.10, "change_pct": -4.85, "category": "Automotive"},
    {"ticker": "META", "name": "Meta Platforms", "price": 512.60, "change_pct": 4.12, "category": "Tech"},
    {"ticker": "JPM", "name": "JPMorgan Chase", "price": 208.70, "change_pct": -1.20, "category": "Finance"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "price": 156.40, "change_pct": 6.80, "category": "Tech"},
    {"ticker": "NFLX", "name": "Netflix Inc", "price": 680.10, "change_pct": -2.40, "category": "Entertainment"}
]

def query_stock_market(action: str = "top_gainers", ticker: str = "") -> dict:
    """
    Returns top gaining stocks, top losing stocks, or specific stock ticker data.
    """
    action_clean = str(action).lower().strip()
    
    if ticker:
        ticker_clean = str(ticker).upper().strip()
        matched = [s for s in SAMPLE_STOCKS if s["ticker"] == ticker_clean or ticker_clean in s["name"].upper()]
        return {
            "query_type": "ticker_search",
            "ticker": ticker_clean,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": matched if matched else f"No stock data found for ticker symbol '{ticker_clean}'."
        }
    
    if "loser" in action_clean or "decrease" in action_clean:
        sorted_stocks = sorted(SAMPLE_STOCKS, key=lambda x: x["change_pct"])
        return {
            "query_type": "top_losers",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": sorted_stocks[:5]
        }
    else:
        # Default: top gainers / highest percentage increase
        sorted_stocks = sorted(SAMPLE_STOCKS, key=lambda x: x["change_pct"], reverse=True)
        return {
            "query_type": "top_gainers",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": sorted_stocks[:5]
        }

if __name__ == "__main__":
    print(query_stock_market("top_gainers"))
