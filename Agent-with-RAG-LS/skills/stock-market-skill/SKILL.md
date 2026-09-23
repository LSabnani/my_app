---
name: stock_market_tool
description: Retrieves real-time or simulated stock market performance, including top percentage gainers, lowest percentage decreasers (losers), and specific stock ticker metrics.
---

# Stock Market Skill

## Description
Retrieves real-time or simulated stock market performance, including top percentage gainers, lowest percentage decreasers (losers), and specific stock ticker metrics.

## Metadata
- **Name**: stock_market_tool
- **Function**: `stock_search.query_stock_market`
- **Trigger Queries**:
  - What are the stocks with the highest percentage increase today?
  - Show me top stock losers or stock market trends.
  - Check stock price and change percentage for AAPL or NVDA.

## Parameters
- `action` (string): Query type (`top_gainers`, `top_losers`, `ticker_search`).
- `ticker` (string, optional): Specific stock ticker symbol (e.g., `AAPL`, `NVDA`, `TSLA`).
