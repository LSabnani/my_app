# Point & Figure (P&F / PNF) Technical Specification

## 1. Executive Summary

This specification defines the functional, algorithmic, data schema, and output requirements for the **Point & Figure (P&F / PNF)** technical analysis engine and visualization platform. P&F charting is a price-only technical analysis methodology that filters out time and minor market noise, focusing exclusively on significant price trends, reversals, support/resistance levels, status reading notation (e.g., `X4@433.341`), target price projections based on John J. Murphy's methodology, and comparative multi-stock screening (such as Magnificent 7 ranking).

---

## 2. Core Principles & Philosophy

1. **Price-Only Dynamics**: Time is omitted from the horizontal axis. A new box entry is plotted only when price moves past defined thresholds.
2. **Column Structure**:
   - **`X` Columns**: Represent rising prices (bullish momentum).
   - **`O` Columns**: Represent falling prices (bearish momentum).
3. **Noise Reduction**: Minor price fluctuations below the designated box threshold are filtered out.
4. **Status Reading Notation**: Real-time evaluation of current state (`<Column_Type><Box_Count>@<Current_Price>`), trend bias, breakout/breakdown signals, key horizontal levels, price objectives, and reward percentages.

---

## 3. System Architecture & Tech Stack

The application is structured into a modular Python engine, a FastAPI web API server, a glassmorphism web interface, and an automated report generation workflow.

- **Python Backend Engine ([pnf_engine.py](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/pnf_engine.py))**: Implements core P&F box/column algorithm, column reversal logic, status notation generation, pattern detection, support/resistance identification, and target price math.
- **FastAPI Application ([main.py](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/main.py))**: REST API service handling data ingestion via `yfinance` with fallback synthetic benchmark data generation, supporting query parameter overrides.
- **Web Frontend ([static/index.html](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/static/index.html), [static/app.js](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/static/app.js), [static/styles.css](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/static/styles.css))**: Dark glassmorphism UI displaying interactive column visualizers, status chips, benchmark preset buttons, and real-time indicators.
- **Output Report ([OUTPUT.md](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/OUTPUT.md))**: Structured tabular and CSV comparative report for stock groups (e.g. Magnificent 7), sorted by Reward %.

---

## 4. Engine Specifications & Parameters

### 4.1 Parameters Configuration

| Parameter | API Default | Description |
| :--- | :--- | :--- |
| **`symbol`** | `AMAT` | Ticker symbol evaluated for analysis. |
| **`box_size_pct`** | `1.0%` | Dynamic percentage box size calculated from asset price (or fixed monetary amount). |
| **`reversal`** | `3` boxes | Number of boxes required in the opposite direction to trigger a column reversal. |
| **`period`** | `6m` | Historical price lookback window (`1m`, `3m`, `6m`, `1y`, `2y`). |
| **`use_mock`** | `false` | Force synthetic benchmark dataset mode for standard compliance testing. |

### 4.2 Box Scaling & Reversal Rules

- **Dynamic Box Size ($B$)**:
  $$B = P_{\text{baseline}} \times \left(\frac{\text{box\_size\_pct}}{100}\right)$$
  *(Or a fixed dollar amount if configured).*

- **Advancement Logic**:
  - In an **`X` Column**: Add $N = \lfloor\frac{P - P_{\text{top}}}{B}\rfloor$ boxes for every upward increment of $B$.
  - In an **`O` Column**: Add $N = \lfloor\frac{P_{\text{bottom}} - P}{B}\rfloor$ boxes for every downward increment of $B$.

- **Reversal Logic**:
  - Reversal from `X` to `O`: Triggered when price falls $\ge \text{Reversal Count} \times B$ below column peak ($P_{\text{top}}$).
  - Reversal from `O` to `X`: Triggered when price rises $\ge \text{Reversal Count} \times B$ above column trough ($P_{\text{bottom}}$).

---

## 5. Pattern Detection & Signal Generation

### 5.1 Classic Patterns

#### Double Top Buy Signal (Bullish Breakout)
- **Condition**: Current `X` column top price exceeds the highest box price of the immediate preceding `X` column.
- **Interpretation**: Buyers broke through resistance, confirming bullish continuation.

```
       [X]  <- Breakout Box (Double Top Buy)
        X
    X   X
    X   X
X   X   X
```

#### Double Bottom Sell Signal (Bearish Breakdown)
- **Condition**: Current `O` column bottom price falls below the lowest box price of the immediate preceding `O` column.
- **Interpretation**: Sellers broke through support, confirming bearish breakdown.

```
O       O
O       O
O   O   O
O   O   O
    O  [O] <- Breakdown Box (Double Bottom Sell)
```

---

## 6. Calculations & Target Projections

### 6.1 Status Reading Notation
The system formats current status into a standardized compact notation:
- **Format**: `<Column_Type><Box_Count>@<Current_Price>`
- **Examples**:
  - `X4@433.341`: Active rising `X` column, 4 boxes tall, latest price \$433.341.
  - `X15@240.130`: Active rising `X` column, 15 boxes tall, latest price \$240.130.
  - `O3@333.090`: Active falling `O` column, 3 boxes tall, latest price \$333.090.

### 6.2 Target Price Objectives

#### 1. Near-Term Objective
Calculated using the base column box count shift formula:
$$\text{Projected Box Shift} = \frac{\text{Base Box Count} \times \text{Reversal Count}}{2}$$
$$\text{Near-Term Target} = \text{Column Extremum} \pm (\text{Projected Box Shift} \times B)$$

#### 2. Long-Term Objective
Calculated via horizontal base extension projection:
- **Bullish Extension**: $\text{Resistance} + (\text{Price Shift} \times 2.5)$
- **Bearish Extension**: $\max(0, \text{Support} - (\text{Price Shift} \times 2.5))$

#### 3. Reward % Calculation
$$\text{Reward \%} = \left(\frac{\text{Long-Term Objective} - \text{Current Price}}{\text{Current Price}}\right) \times 100\%$$

### 6.3 Support and Resistance Identification
- **PNF Resistance**: Highest box price observed across all `X` columns.
- **PNF Support**: Lowest box price observed across all `O` columns.

---

## 7. Output Specifications

### 7.1 JSON REST API Schema (`/api/pnf/analyze`)

```json
{
  "symbol": "AMAT",
  "data_source": "Live Market Data (yfinance)",
  "data_points": 120,
  "parameters": {
    "box_size_pct": 1.0,
    "box_size_val": 4.3334,
    "reversal": 3
  },
  "status_reading": "X4@433.341",
  "trend": "Bullish",
  "signal": "Double Top Buy (Bullish Breakout)",
  "levels": {
    "support": 442.05,
    "resistance": 555.73
  },
  "targets": {
    "near_term": 464.60,
    "long_term": 631.00
  },
  "columns": [
    {
      "type": "X",
      "boxes": [420.0, 424.2, 428.4, 432.6],
      "box_count": 4,
      "top_price": 432.6,
      "bottom_price": 420.0,
      "start_index": 0,
      "end_index": 12
    }
  ]
}
```

### 7.2 Multi-Stock Output Table Specification ([OUTPUT.md](file:///c:/Users/Lalit.MSI/Documents/Education/AntiGravity/my_app/PNF/OUTPUT.md))

Multi-stock analysis outputs (e.g. Magnificent 7 screening) produce CSV data blocks and Markdown tables sorted by **Reward %** in descending order:

```markdown
| Symbol | Current Price | Open | Low | High | PNF Status | Near Term Objective | Long Term Objective | Reward % |
```

---

## 8. Benchmark Verification & Compliance

- **AMAT StockCharts Benchmark**:
  - Parameters: 1% Box, 3-Box Reversal
  - Status Reading: `X4@433.341`
  - Resistance: `$555.73` \| Support: `$442.05`
  - Near-Term Target: `$464.60` \| Long-Term Objective: `$631.00`
