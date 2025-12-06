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

    def _handle_missing_data(self) -> None:
        """Handle missing data according to config."""
        if 'missing_data' not in self.config:
            return

        missing_config = self.config['missing_data']
        action = missing_config.get('action', 'remove')

        if action == 'remove':
            self.data = [row for row in self.data if all(v not in (None, "") for v in row.values())]
        elif action == 'fill':
            defaults = missing_config.get('defaults', {})
            for row in self.data:
                for col, value in row.items():
                    if value in (None, ""):
                        col_type = self.col_types.get(col, 'string')
                        if col_type == 'number':
                            row[col] = defaults.get('number', 0)
                        elif col_type == 'date':
                            row[col] = defaults.get('date', '1970-01-01')
                        else:
                            row[col] = defaults.get('string', 'N/A')

    def _standardize_dates(self) -> None:
        """Standardize date format according to config."""
        if 'date_format' not in self.config:
            return

        target_format = self.config['date_format'].lower()
        date_cols = [col for col, dtype in self.col_types.items() if dtype == 'date']

        for row in self.data:
            for col in date_cols:
                if col in row:
                    try:
                        parsed = self._parse_date(str(row[col]))
                        if parsed:
                            row[col] = self._format_date(parsed, target_format)
                    except Exception:
                        pass

    def _parse_date(self, date_str: str) -> Any:
        """Try to parse date string flexibly."""
        date_str = date_str.strip()
        patterns = [
            r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}",
            r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}",
        ]

        for pattern in patterns:
            if re.match(pattern, date_str):
                try:
                    sep = '-' if '-' in date_str else '/'
                    if re.match(r"^\d{4}[-/]", date_str):
                        return datetime.strptime(date_str.split()[0], f'%Y{sep}%m{sep}%d')
                    else:
                        return datetime.strptime(date_str.split()[0], f'%d{sep}%m{sep}%Y')
                except Exception:
                    pass
        return None

    def _format_date(self, dt: datetime, format_str: str) -> str:
        """Format datetime according to format string using y, m, d."""
        format_str = format_str.lower()
        # Map format string to strftime
        result = format_str
        year_count = format_str.count('y')
        month_count = format_str.count('m')
        day_count = format_str.count('d')

        year_fmt = f'%Y' if year_count >= 4 else f'%y'
        month_fmt = f'%m' if month_count >= 2 else f'%#m'
        day_fmt = f'%d' if day_count >= 2 else f'%#d'

        result = result.replace('yyyy', year_fmt).replace('yy', year_fmt)
        result = result.replace('mm', month_fmt).replace('m', month_fmt)
        result = result.replace('dd', day_fmt).replace('d', day_fmt)

        return dt.strftime(result)

