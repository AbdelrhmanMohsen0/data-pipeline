from typing import List, Dict, Any
from functional_impl.cleaning import clean

def run_pipeline(config, dataset) -> List[Dict[str, Any]]:
    return clean(dataset, config)
