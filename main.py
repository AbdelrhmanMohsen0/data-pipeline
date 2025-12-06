import argparse
from core.io import load_csv, load_json, output_summary
from core.cli_menu import main_menu
from imperative_impl.runner import run_pipeline
from core.io import save_csv

def main():
    parser = argparse.ArgumentParser(description="Data pipeline processor")
    parser.add_argument(
        "dataset",
        type=str,
        help="Path to the input dataset CSV file"
    )

    args = parser.parse_args()
    dataset_path = args.dataset
    dataset = None
    if dataset_path.endswith('.csv'):
        dataset = load_csv(dataset_path)
    elif dataset_path.endswith('.json'):
        dataset = load_json(dataset_path)
    else:
        print("Unsupported file format. Please provide a CSV or JSON file.")
        return
    
    if dataset or not len(dataset) == 0:
        config = main_menu(dataset)
        print(config)
        output, analyzing_report, aggregation = run_pipeline(config, dataset)
        if config.get('output') == "Save to CSV":
            output_path = dataset_path.rsplit('/', 1)[0] + '/' + dataset_path.rsplit('/', 1)[1].rsplit('.', 1)[0] + '_output.' + dataset_path.rsplit('.', 1)[1]
            save_csv(output, output_path)
        else:
            output_summary(output)

if __name__ == "__main__":
    main()
