from typing import Any, List, Dict
from functools import reduce

def _calculate_mean(data: List[Dict[str, Any]]) -> dict[str, float]:
    if not data:
        return {}
    
    cols_sum = dict(reduce(
        lambda acc, row: {**acc, **dict(map(
            lambda col: (col[0], acc.get(col[0], 0) + col[1]) if isinstance(col[1], (int, float)) else (col[0], acc.get(col[0], 0)),
            row.items()
        ))},
        data,
        {}
    ))
    
    return dict(map(
        lambda col: (col, cols_sum[col] / len(data)),
        cols_sum.keys()
    ))

def _calculate_median(data: List[Dict[str, Any]]) -> dict[str, float]:
    if not data:
        return {}
    
    values = {}
    for record in data:
        for key, value in record.items():
            if isinstance(value, (int, float)):
                if key not in values:
                    values[key] = []
                    values[key].append(value)
        
    medians = {}
    for key in values:
        sorted_values = sorted(values[key])
        n = len(sorted_values)
        if n % 2 == 1:
            medians[key] = sorted_values[n // 2]
        else:
            medians[key] = (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
    
    return medians

def _calculate_variance(self):
    if not self.data:
        return {}

    # Identify numerical columns
    numeric_columns = {}
    for row in self.data:
        for key, value in row.items():
            if isinstance(value, (int, float)):
                numeric_columns.setdefault(key, []).append(value)

    variances = {}

    for col, values in numeric_columns.items():
        n = len(values)
        if n == 0:
            variances[col] = None
            continue

        # Calculate mean manually
        mean = sum(values) / len(values)
    
        # Calculate variance manually
        sq_diff_sum = 0
        for v in values:
            sq_diff_sum += (v - mean) ** 2
        
        variance = sq_diff_sum / n   # population variance

        variances[col] = variance

    return variances

def _monthly_trend(self, date_col, value_col):
    trend = {}  # { "YYYY-MM" : sum }

    for row in self.data:
        date = row.get(date_col)
        value = row.get(value_col)

        if not isinstance(value, (int, float)):
            continue

        # expects date format YYYY-MM-DD
        if isinstance(date, str) and len(date) >= 7:
            month = date[:7]  # "YYYY-MM"
            trend[month] = trend.get(month, 0) + value

    return trend

def analyze(data) -> dict[str, dict[str, Any]]:
    if not data:
        return {}
    
    return {
        'mean': _calculate_mean(data),
        'median': _calculate_median(data),
        'variance': _calculate_variance(data),
        'trend': _monthly_trend(data, 'Sale_Date', 'Sales_Amount'),
    }
