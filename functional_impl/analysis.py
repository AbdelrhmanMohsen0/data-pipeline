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

def _calculate_median(data: List[Dict[str, Any]]) -> Dict[str, float]:
    if not data:
        return {}
    
    numeric_pairs = reduce(
        lambda accumulated_pairs, row: accumulated_pairs + list(filter(
            lambda key_value: isinstance(key_value[1], (int, float)),
            row.items()
        )),
        data,
        []
    )
    
    if not numeric_pairs:
        return {}
    
    grouped_by_key = reduce(
        lambda grouped_values, key_value_pair: {
            **grouped_values, 
            key_value_pair[0]: grouped_values.get(key_value_pair[0], []) + [key_value_pair[1]]
        },
        numeric_pairs, 
        {}
    )

    return dict(map(
        lambda key_values: (key_values[0], _median(sorted(key_values[1]))),
        grouped_by_key.items()
    ))

def _median(sorted_values: List[float]) -> float:

    value_count = len(sorted_values)
    middle_index = value_count // 2
    
    if value_count % 2 == 1:
        return sorted_values[middle_index]
    else:
        lower_middle = sorted_values[middle_index - 1]
        upper_middle = sorted_values[middle_index]
        return (lower_middle + upper_middle) / 2

def _calculate_variance(data: List[Dict[str, Any]]) -> Dict[str, float]:
    if not data:
        return {}

    numeric_pairs = reduce(
        lambda accumulated_pairs, row: accumulated_pairs + list(filter(
            lambda key_value: isinstance(key_value[1], (int, float)),
            row.items()
        )),
        data,
        []
    )
    
    if not numeric_pairs:
        return {}
 
    grouped_by_key = reduce(
        lambda grouped_values, key_value_pair: {
            **grouped_values, 
            key_value_pair[0]: grouped_values.get(key_value_pair[0], []) + [key_value_pair[1]]
        },
        numeric_pairs, 
        {}
    )

    return dict(map(
        lambda key_values: (key_values[0], _variance(key_values[1])),
        grouped_by_key.items()
    ))

def _variance(values: List[float]) -> float:

    value_count = len(values)
    mean_value = reduce(
        lambda accumulated_sum, value: accumulated_sum + value, 
        values, 
        0
    ) / value_count

    sum_squared_differences = reduce(
        lambda accumulated_squared_diffs, value: accumulated_squared_diffs + (value - mean_value) ** 2,
        values,
        0
    )

    return sum_squared_differences / value_count

def _monthly_trend(data: List[Dict[str, Any]], date_col: str, value_col: str) -> Dict[str, float]:
    # Calculate monthly trend (percentage change month-to-month)
    
    if not data:
        return {}

    month_value_pairs = list(filter(
        lambda pair: pair is not None,
        map(
            lambda row: _extract_month_value(row, date_col, value_col),
            data
        )
    ))
    
    if not month_value_pairs:
        return {}

    monthly_sales = reduce(
        lambda grouped_sales, month_value: {
            **grouped_sales,
            month_value[0]: grouped_sales.get(month_value[0], 0) + month_value[1]
        },
        month_value_pairs,
        {}
    )
    
    sorted_months = sorted(monthly_sales.keys())

    return dict(filter(
        lambda item: item is not None,
        map(
            lambda i: _calculate_month_change(sorted_months, monthly_sales, i) if i > 0 else None,
            range(len(sorted_months))
        )
    ))

def _extract_month_value(row: Dict[str, Any], date_col: str, value_col: str) -> tuple:
    
    date = row.get(date_col)
    value = row.get(value_col)
    
    if not isinstance(value, (int, float)):
        return None
    
    if isinstance(date, str) and len(date) >= 7:
        month = date[:7]  # "YYYY-MM"
        return (month, value)
    
    return None

def _calculate_month_change(sorted_months: List[str], monthly_sales: Dict[str, float], current_index: int) -> tuple:

    current_month = sorted_months[current_index]
    previous_month = sorted_months[current_index - 1]
    
    current_sales = monthly_sales[current_month]
    previous_sales = monthly_sales[previous_month]

    if previous_sales == 0:
        return None

    percentage_change = ((current_sales - previous_sales) / previous_sales) * 100
    
    return (current_month, percentage_change)

def analyze(data) -> dict[str, dict[str, Any]]:
    if not data:
        return {}
    
    return {
        'mean': _calculate_mean(data),
        'median': _calculate_median(data),
        'variance': _calculate_variance(data),
        'trend': _monthly_trend(data, 'Sale_Date', 'Sales_Amount'),
    }
