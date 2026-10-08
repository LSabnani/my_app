"""
Point & Figure (P&F / PNF) Core Engine & Technical Indicator Module.
Implements Box calculation, Column reversal logic, Pattern detection,
Status Reading, and Target price objectives based on SPEC.md.
"""

from typing import List, Dict, Any, Optional
import math
import pandas as pd


class PnFBox:
    def __init__(self, price: float):
        self.price = round(price, 4)

    def to_dict(self):
        return {"price": self.price}


class PnFColumn:
    def __init__(self, col_type: str, start_index: int):
        # col_type: 'X' for rising, 'O' for falling
        self.col_type = col_type
        self.boxes: List[float] = []
        self.start_index = start_index
        self.end_index = start_index

    @property
    def top_price(self) -> float:
        return max(self.boxes) if self.boxes else 0.0

    @property
    def bottom_price(self) -> float:
        return min(self.boxes) if self.boxes else 0.0

    @property
    def box_count(self) -> int:
        return len(self.boxes)

    def to_dict(self):
        return {
            "type": self.col_type,
            "boxes": [round(b, 4) for b in self.boxes],
            "box_count": self.box_count,
            "top_price": round(self.top_price, 4),
            "bottom_price": round(self.bottom_price, 4),
            "start_index": self.start_index,
            "end_index": self.end_index,
        }


class PnFEngine:
    def __init__(self, box_size_pct: float = 1.0, reversal_count: int = 3, fixed_box_size: Optional[float] = None):
        """
        :param box_size_pct: Percentage box size (e.g. 1.0 for 1%)
        :param reversal_count: Reversal amount in box count (e.g. 3)
        :param fixed_box_size: Fixed monetary box size (optional override)
        """
        self.box_size_pct = box_size_pct
        self.reversal_count = reversal_count
        self.fixed_box_size = fixed_box_size

    def calculate_box_size(self, price: float) -> float:
        if self.fixed_box_size is not None and self.fixed_box_size > 0:
            return self.fixed_box_size
        return price * (self.box_size_pct / 100.0)

    def generate_chart(self, prices: List[float], timestamps: Optional[List[str]] = None) -> Dict[str, Any]:
        if not prices:
            return {
                "columns": [],
                "status_reading": "N/A",
                "trend": "Neutral",
                "signal": "None",
                "levels": {"support": 0.0, "resistance": 0.0},
                "targets": {"near_term": 0.0, "long_term": 0.0}
            }

        columns: List[PnFColumn] = []
        current_col: Optional[PnFColumn] = None

        # Determine baseline box size from initial price
        base_price = prices[0]
        box_size = self.calculate_box_size(base_price)
        if box_size <= 0:
            box_size = 0.01

        # We keep track of current grid level reference
        for i, price in enumerate(prices):
            if not current_col:
                # First price initializes the first column as 'X'
                current_col = PnFColumn('X', i)
                initial_box = math.floor(price / box_size) * box_size
                current_col.boxes.append(initial_box)
                columns.append(current_col)
                continue

            current_col.end_index = i

            if current_col.col_type == 'X':
                current_top = current_col.top_price
                # Check for rising movement (new X boxes)
                if price >= current_top + box_size:
                    num_new_boxes = math.floor((price - current_top) / box_size)
                    for b in range(1, num_new_boxes + 1):
                        new_box_price = current_top + (b * box_size)
                        current_col.boxes.append(new_box_price)
                # Check for reversal to O column
                elif price <= current_top - (self.reversal_count * box_size):
                    num_o_boxes = math.floor((current_top - price) / box_size)
                    new_col = PnFColumn('O', i)
                    for b in range(1, num_o_boxes + 1):
                        new_box_price = current_top - (b * box_size)
                        new_col.boxes.append(new_box_price)
                    columns.append(new_col)
                    current_col = new_col

            elif current_col.col_type == 'O':
                current_bottom = current_col.bottom_price
                # Check for falling movement (new O boxes)
                if price <= current_bottom - box_size:
                    num_new_boxes = math.floor((current_bottom - price) / box_size)
                    for b in range(1, num_new_boxes + 1):
                        new_box_price = current_bottom - (b * box_size)
                        current_col.boxes.append(new_box_price)
                # Check for reversal to X column
                elif price >= current_bottom + (self.reversal_count * box_size):
                    num_x_boxes = math.floor((price - current_bottom) / box_size)
                    new_col = PnFColumn('X', i)
                    for b in range(1, num_x_boxes + 1):
                        new_box_price = current_bottom + (b * box_size)
                        new_col.boxes.append(new_box_price)
                    columns.append(new_col)
                    current_col = new_col

        latest_price = prices[-1]
        last_col = columns[-1] if columns else None

        # 1. Status Reading (e.g. X4@433.341)
        if last_col:
            status_reading = f"{last_col.col_type}{last_col.box_count}@{latest_price:.3f}"
        else:
            status_reading = "N/A"

        # 2. Support & Resistance Identification
        all_tops = [col.top_price for col in columns if col.col_type == 'X']
        all_bottoms = [col.bottom_price for col in columns if col.col_type == 'O']

        resistance = max(all_tops) if all_tops else latest_price
        support = min(all_bottoms) if all_bottoms else latest_price

        # 3. Pattern & Signal Detection
        signal = "Neutral / Consolidation"
        trend = "Neutral"
        near_term_target = latest_price
        long_term_target = latest_price

        if len(columns) >= 3:
            # Check for Double Top Buy (Bullish Breakout)
            # Current column is X, exceeds top of previous X column
            prev_x_cols = [c for c in columns[:-1] if c.col_type == 'X']
            prev_o_cols = [c for c in columns[:-1] if c.col_type == 'O']

            if last_col and last_col.col_type == 'X' and prev_x_cols:
                prev_x_top = prev_x_cols[-1].top_price
                if last_col.top_price > prev_x_top:
                    signal = "Double Top Buy (Bullish Breakout)"
                    trend = "Bullish"

            # Check for Double Bottom Sell (Bearish Breakdown)
            if last_col and last_col.col_type == 'O' and prev_o_cols:
                prev_o_bottom = prev_o_cols[-1].bottom_price
                if last_col.bottom_price < prev_o_bottom:
                    signal = "Double Bottom Sell (Bearish Breakdown)"
                    trend = "Bearish"

        if trend == "Neutral" and last_col:
            trend = "Bullish" if last_col.col_type == 'X' else "Bearish"

        # 4. Target Price Projections
        # Near term target formula: Projected Boxes = (Base Box Count * Reversal Count) / 2
        if last_col:
            base_count = last_col.box_count
            box_shift = (base_count * self.reversal_count) / 2.0
            price_shift = box_shift * box_size

            if last_col.col_type == 'X':
                near_term_target = last_col.top_price + price_shift
                long_term_target = resistance + (price_shift * 2.5)
            else:
                near_term_target = last_col.bottom_price - price_shift
                long_term_target = max(0.0, support - (price_shift * 2.5))

        return {
            "parameters": {
                "box_size_pct": self.box_size_pct,
                "box_size_val": round(box_size, 4),
                "reversal": self.reversal_count
            },
            "status_reading": status_reading,
            "trend": trend,
            "signal": signal,
            "levels": {
                "support": round(support, 2),
                "resistance": round(resistance, 2)
            },
            "targets": {
                "near_term": round(near_term_target, 2),
                "long_term": round(long_term_target, 2)
            },
            "columns": [col.to_dict() for col in columns],
            "price_history_length": len(prices),
            "latest_price": round(latest_price, 4)
        }
