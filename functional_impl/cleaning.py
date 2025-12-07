from typing import List, Dict, Any
import re
from datetime import datetime
from functools import reduce

from core.utils import infer_column_types

def handle_missing_data(data: List[Dict[str, Any]], config: Dict[str, Any], col_types: Dict[str, str]) -> List[Dict[str, Any]]:
    """Handle missing data according to config."""
    if 'missing_data_action' not in config:
        return data

    action = config.get('missing_data_action', 'remove')

    if action == 'remove':
        return list(filter(lambda row: reduce(lambda acc, v: acc and v not in (None, ""), row.values(), True), data))
    elif action == 'fill':
        col_defaults: Dict[str, Any] = reduce(
            lambda acc, col: acc.update({
                col: calc_col_mean(col, data, col_types) if col_types.get(col) == 'number' else calc_col_mode(col, data)
            }) or acc,
            col_types.keys(),
            {}
        )
        return list(map(lambda row: dict(map(lambda col: (col, col_defaults[col] if row[col] in (None, "") else row[col]), row)), data))
    
    return data

def standardize_dates(data: List[Dict[str, Any]], config: Dict[str, Any], col_types: Dict[str, str]) -> List[Dict[str, Any]]:
    """Standardize date format according to config."""
    date_cols = reduce(lambda acc, col: acc + [col] if col_types.get(col) == 'date' else acc, col_types.keys(), [])

    return list(map(lambda row: dict(map(
        lambda col: (col, row[col] if col not in date_cols else parse_date(str(row[col])).strftime('%Y-%m-%d')), row
    )), data))

def standardize_numerical_precision(data: List[Dict[str, Any]], col_types: Dict[str, str]) -> List[Dict[str, Any]]:
    """Round numerical values to specified precision."""

    precision = 2
    num_cols = reduce(lambda acc, col: acc + [col] if col_types.get(col) == 'number' else acc, col_types.keys(), [])

    return list(map(lambda row: dict(map(
        lambda col: (col, round(float(row[col]), precision) if col in num_cols and row[col] not in (None, "") else row[col]), row
    )), data))

def calc_col_mean(col: str, data: List[Dict[str, Any]], col_types: Dict[str, str]) -> float:
    """Calculate mean of a numerical column."""
    if col_types.get(col) != 'number':
        return 0.0
    
    total = reduce(lambda acc, row: acc + float(row[col]), data, 0.0)
    count = len(data)
    return total / count if count > 0 else 0.0

def calc_col_mode(col: str, data: List[Dict[str, Any]]) -> Any:
    """Calculate mode of a column."""
    freq: Dict[Any, int] = reduce(lambda acc, row: (
        acc.update({row[col]: acc.get(row[col], 0) + 1}) or acc
    ), data, {})
    return max(freq.items(), key=lambda x: x[1])[0]

def parse_date(date_str: str) -> Any:
    """Try to parse date string flexibly."""
    date = date_str.strip()
    patterns = [
        ('%Y-%m-%d', r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}"),
        ('%d-%m-%Y', r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}"),
        ('%m-%d-%Y', r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}"),
    ]
    return reduce(lambda acc, fmt_pattern: (
        acc or datetime.strptime(date.split()[0], fmt_pattern[0].replace('-', date[4]))
    ), patterns, None)

def clean(data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Clean data according to config."""
    col_types: Dict[str, str] = infer_column_types(data)
    cleaned_data = handle_missing_data(data, config, col_types)
    standardized_dates_data = standardize_dates(cleaned_data, config, col_types)
    standardized_numerical_data = standardize_numerical_precision(standardized_dates_data, col_types)
    
    return standardized_numerical_data