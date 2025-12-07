from typing import List, Dict, Any, Tuple
from functional_impl.cleaning import clean
from functional_impl.transformation import transform, aggregate_by_key
from functional_impl.analysis import analyze

def run_pipeline(config, dataset) -> Tuple[List[Dict[str, Any]], dict, dict | None]:
    output_data = transform(clean(dataset, config), config)
    analysis_summary = analyze(output_data)
    
    return output_data, analysis_summary, aggregate_by_key(output_data, config)