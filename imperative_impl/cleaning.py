from typing import List, Dict, Any
import re
from datetime import datetime

from core.utils import infer_column_types

class DataCleaner:
    def __init__(self, data: List[Dict[str, Any]], config: Dict[str, Any]):
        self.data = data
        self.config = config
        self.col_types: Dict[str, str] = infer_column_types(data)

    def clean(self) -> None:
        self._handle_missing_data()
        self._standardize_dates()
        self._standardize_numerical_precision()

    def _handle_missing_data(self) -> None:
        """Handle missing data according to config."""
        if 'missing_data_action' not in self.config:
            return

        action = self.config.get('missing_data_action', 'remove')
        if action == 'remove':
            self.data = [row for row in self.data if all(v not in (None, "") for v in row.values())]
        elif action == 'fill':
            col_means: Dict[str, float] = {}
            col_modes: Dict[str, Any] = {}
            for row in self.data:
                for col, value in row.items():
                    if value in (None, ""):
                        col_type = self.col_types.get(col, 'string')
                        if col_type == 'number':
                            row[col] = col_means.get(col, self._calc_col_mean(col))
                        elif col_type == 'date':
                            row[col] = col_modes.get(col, self._calc_col_mode(col))
                        else:
                            row[col] = col_modes.get(col, self._calc_col_mode(col))

    def _standardize_dates(self) -> None:
        """Standardize date format according to config."""
        date_cols = [col for col, dtype in self.col_types.items() if dtype == 'date']

        for row in self.data:
            for col in date_cols:
                if col in row:
                    try:
                        parsed = self._parse_date(str(row[col]))
                        if parsed:
                            row[col] = parsed.strftime('%Y-%m-%d')
                    except Exception:
                        pass

    def _parse_date(self, date_str: str) -> Any:
        """Try to parse date string flexibly."""
        date_str = date_str.strip()
        patterns = [
            ('%Y-%m-%d', r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}"),
            ('%d-%m-%Y', r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}"),
            ('%m-%d-%Y', r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}"),
        ]

        for fmt, pattern in patterns:
            if re.match(pattern, date_str):
                try:
                    date_part = date_str.split()[0]
                    return datetime.strptime(date_part, fmt.replace('-', date_str[4]))
                except Exception:
                    pass
        return None

    def _standardize_numerical_precision(self) -> None:
        """Round numerical values to specified precision."""

        precision = 2
        num_cols = [col for col, dtype in self.col_types.items() if dtype == 'number']

        for row in self.data:
            for col in num_cols:
                if col in row:
                    try:
                        val = float(row[col])
                        row[col] = round(val, precision)
                    except Exception:
                        pass
    
    def _calc_col_mean(self, col: str) -> float:

        """Calculate mean of a numerical column."""
        if self.col_types.get(col) != 'number':
            return 0.0
        total = 0.0
        count = 0
        for row in self.data:
            try:
                val = float(row[col])
                total += val
                count += 1
            except Exception:
                continue
        return total / count if count > 0 else 0.0
    
    def _calc_col_mode(self, col: str) -> Any:
        """Calculate mode of a column."""
        freq: Dict[Any, int] = {}
        for row in self.data:
            val = row.get(col)
            if val not in (None, ""):
                freq[val] = freq.get(val, 0) + 1
        if not freq:
            return None
        mode = max(freq.items(), key=lambda x: x[1])[0]
        return mode