from typing import List, Dict, Any
from functools import reduce

from core.utils import infer_column_types

def _filter_rows(data: List[Dict[str, Any]], config: Dict[str, Any], col_types: Dict[str, str]) -> List[Dict[str, Any]]:
    """Filter rows based on condition in config."""
    if 'filter' not in config or not config['filter'].get('apply', False):
        return data

    filter_config = config['filter']
    col = filter_config.get('column')
    operator = filter_config.get('operator')
    value: Any = filter_config.get('value')

    if not col or not operator:
        return data
    
    does_match = lambda row, val: (
        (operator == '>' and row[col] > val) or
        (operator == '<' and row[col] < val) or
        (operator == '>=' and row[col] >= val) or
        (operator == '<=' and row[col] <= val) or
        (operator == '==' and row[col] == val) or
        (operator == 'Exactly equal' and row[col] == val) or
        (operator == 'Contains' and str(val) in str(row[col]))
    )

    convert_val = lambda v: (
        float(v) if col_types.get(col) == 'number' else str(v).lower()
    )
    
    return list(filter(lambda row: (
        does_match({col: convert_val(row[col])}, convert_val(value))
    ), data))

def _compute_new_column(data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute a new column based on config."""
    if 'compute' not in config:
        return data

    compute_config = config['compute']
    if compute_config is None:
        return data
    
    compute_profit = lambda row: (
        (float(row.get('Unit_Price', 0)) - float(row.get('Unit_Cost', 0))) * float(row.get('Quantity_Sold', 0))
    )
    
    return list(map(lambda row: (
        {**row, 'Profit': compute_profit(row)} if compute_config == 'Profit' else row
    ), data))

def aggregate_by_key(data: List[Dict[str, Any]], config: Dict[str, Any]) -> dict | None:
    """Aggregate data by a specified key."""
    if 'aggregate' not in config:
        return

    if config['aggregate'] is None:
        return 
    
    if config['aggregate'] == 'Aggregate total sales by region':
        key_col = 'Region'
        value_col = 'Sales_Amount'

    return dict(reduce(
        lambda acc, row: {
            **acc, 
            row[key_col]: acc.get(row[key_col], 0) + (
                float(row.get(value_col, 0)) 
                if row.get(value_col) not in (None, "") else 0.0
            )
        },
        data,
        {}
    ))

def transform(data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    col_types = infer_column_types(data)
    filtered_data = _filter_rows(data, config, col_types)
    computed_data = _compute_new_column(filtered_data, config)
    return computed_data    