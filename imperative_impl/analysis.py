from typing import Any


class DataAnalyzer:
    def __init__(self, data):
        self.data = data

    def analyze(self):
        if not self.data:
            return {}

        summary: dict[str, dict[str, Any]] = {
            'mean': self._calculate_mean(),
            'median': self._calculate_median(),
            'variance': self._calculate_variance(),
            'trend': self._monthly_trend('Sale_Date', 'Sales_Amount'),
        }

        return summary

    def _calculate_mean(self):
        if not self.data:
            return {}
        
        means = {}
        for record in self.data:
            for key, value in record.items():
                if isinstance(value, (int, float)):
                    if key not in means:
                        means[key] = {'sum': 0, 'count': 0}
                    means[key]['sum'] += value
                    means[key]['count'] += 1
        
        return {key: means[key]['sum'] / means[key]['count'] for key in means if means[key]['count'] > 0}
    
    def _calculate_median(self):
        if not self.data:
            return {}
        
        values = {}
        for record in self.data:
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
        
        if not self.data:
            return {}

        monthly_sales = {}
        
        for row in self.data:
            date = row.get(date_col)
            value = row.get(value_col)
            
            if not isinstance(value, (int, float)):
                continue

            if isinstance(date, str) and len(date) >= 7:
                month = date[:7] 
                monthly_sales[month] = monthly_sales.get(month, 0) + value
        
        if not monthly_sales:
            return {}
        
        sorted_months = sorted(monthly_sales.keys())
        trend = {}
        
        for i in range(1, len(sorted_months)):
            current_month = sorted_months[i]
            previous_month = sorted_months[i - 1]
            
            current_sales = monthly_sales[current_month]
            previous_sales = monthly_sales[previous_month]
            
            if previous_sales == 0:
                continue
            
            percentage_change = ((current_sales - previous_sales) / previous_sales) * 100
            trend[current_month] = percentage_change
        
        return trend

