from typing import List, Dict, Any, Tuple
from imperative_impl.cleaning import DataCleaner
from imperative_impl.transformation import DataTransformer
from imperative_impl.analysis import DataAnalyzer

def run_pipeline(config, dataset) -> Tuple[List[Dict[str, Any]], dict, dict | None]:
    cleaner = DataCleaner(dataset, config)
    cleaner.clean()

    transformer = DataTransformer(dataset, config)
    transformer.transform()

    analyzer = DataAnalyzer(dataset)
    analysis_results = analyzer.analyze()

    return dataset, analysis_results, transformer.aggregate_by_key()