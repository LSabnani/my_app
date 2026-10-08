# Magnificent 7 (Mag 7) Point & Figure (PNF) Analysis Output

This document contains the Point & Figure (P&F / PNF) analysis output for the **Magnificent 7 (Mag 7)** stocks using a **1% Box Size** and **3-Box Reversal** parameters, sorted by **Reward %** in descending order.

---

## CSV Data Output (Sorted by Reward % Descending)

```csv
Symbol,Current Price,Open,Low,High,PNF Status,Near Term Objective,Long Term Objective,Reward %
NVDA,240.13,242.08,239.60,243.37,X15@240.130,279.14,338.96,+41.16%
TSLA,380.23,382.04,378.52,383.33,X6@380.225,409.27,523.94,+37.80%
GOOGL,348.19,347.37,344.68,349.09,X3@348.190,361.04,435.20,+24.99%
AMZN,256.15,253.40,251.08,256.64,X4@256.150,268.12,314.93,+22.95%
MSFT,531.04,531.68,528.82,535.69,X9@531.036,577.49,652.69,+22.91%
META,744.00,746.80,736.69,747.60,X4@744.000,777.97,858.06,+15.33%
AAPL,333.09,332.30,330.62,334.38,O3@333.090,319.12,247.42,-25.72%
```

---

## Rendered Table View (Sorted by Reward % Descending)

| Symbol | Current Price | Open | Low | High | PNF Status | Near Term Objective | Long Term Objective | Reward % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **NVDA** | \$240.13 | \$242.08 | \$239.60 | \$243.37 | `X15@240.130` | \$279.14 | \$338.96 | **+41.16%** |
| **TSLA** | \$380.23 | \$382.04 | \$378.52 | \$383.33 | `X6@380.225` | \$409.27 | \$523.94 | **+37.80%** |
| **GOOGL** | \$348.19 | \$347.37 | \$344.68 | \$349.09 | `X3@348.190` | \$361.04 | \$435.20 | **+24.99%** |
| **AMZN** | \$256.15 | \$253.40 | \$251.08 | \$256.64 | `X4@256.150` | \$268.12 | \$314.93 | **+22.95%** |
| **MSFT** | \$531.04 | \$531.68 | \$528.82 | \$535.69 | `X9@531.036` | \$577.49 | \$652.69 | **+22.91%** |
| **META** | \$744.00 | \$746.80 | \$736.69 | \$747.60 | `X4@744.000` | \$777.97 | \$858.06 | **+15.33%** |
| **AAPL** | \$333.09 | \$332.30 | \$330.62 | \$334.38 | `O3@333.090` | \$319.12 | \$247.42 | **-25.72%** |

---

## Calculation Notes
- **Parameters**: 1.0% dynamic box size, 3-box reversal.
- **PNF Status Notation**: `<Column_Type><Box_Count>@<Current_Price>`
- **Near Term Objective**: Calculated as $\text{Breakout Level} \pm \frac{\text{Base Count} \times 3}{2} \times \text{Box Size}$.
- **Long Term Objective**: Projected using column horizontal base extension.
- **Reward %**: Calculated as $\frac{\text{Long Term Objective} - \text{Current Price}}{\text{Current Price}} \times 100\%$ and sorted in descending order.
