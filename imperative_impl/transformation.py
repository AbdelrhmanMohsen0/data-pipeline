from typing import List, Dict, Any

from core.utils import infer_column_types

class DataTransformer:
    def __init__(self, data: List[Dict[str, Any]], config: Dict[str, Any]):
        self.data = data
        self.config = config
        self.col_types: Dict[str, str] = infer_column_types(data)

    def transform(self) -> None:
        self._filter_rows()
        self._compute_new_column()
        
    def _filter_rows(self) -> None:
        """Filter rows based on condition in config."""
        if 'filter' not in self.config or not self.config['filter'].get('apply', False):
            return

        filter_config = self.config['filter']
        col = filter_config.get('column')
        operator = filter_config.get('operator')
        value: Any = filter_config.get('value')

        if not col or not operator:
            return

        filtered_data = []
        for row in self.data:
            if col not in row:
                continue

            row_value = row[col]
            col_type = self.col_types.get(col, 'string')

            # Convert to comparable type
            if col_type == 'number':
                try:
                    row_value = float(row_value)
                except Exception:
                    continue
            else:
                row_value = str(row_value).lower()
                value = str(value).lower() if isinstance(value, str) else value

            # Apply operator
            match = False
            if operator == '>':
                match = row_value > value
            elif operator == '<':
                match = row_value < value
            elif operator == '>=':
                match = row_value >= value
            elif operator == '<=':
                match = row_value <= value
            elif operator == '==':
                match = row_value == value
            elif operator == 'Exactly equal':
                match = row_value == value
            elif operator == 'Contains':
                match = str(value) in str(row_value)

            if match:
                filtered_data.append(row)

        self.data[:] = [*filtered_data]

    def _compute_new_column(self) -> None:
        """Compute a new column based on config."""
        if 'compute' not in self.config:
            return

        compute_config = self.config['compute']
        if compute_config is None:
            return
        
        if compute_config == 'Profit':
            for row in self.data:
                try:
                    unit_price = float(row.get('Unit_Price', 0))
                    unit_cost = float(row.get('Unit_Cost', 0))
                    quantity = float(row.get('Quantity_Sold', 0))
                    row['Profit'] = (unit_price - unit_cost) * quantity
                except Exception:
                    row['Profit'] = None

    def aggregate_by_key(self) -> dict | None:
        """Aggregate data by a specified key."""
        if 'aggregate' not in self.config:
            return

        if self.config['aggregate'] is None:
            return 
        
        if self.config['aggregate'] == 'Aggregate total sales by region':
            key_col = 'Region'
            value_col = 'Sales_Amount'
            aggregation: Dict[Any, float] = {}
            for row in self.data:
                key = row.get(key_col)
                value = 0.0
                try:
                    value = float(row.get(value_col, 0))
                except Exception:
                    value = 0.0
                if key in aggregation:
                    aggregation[key] += value
                else:
                    aggregation[key] = value

        return aggregation
