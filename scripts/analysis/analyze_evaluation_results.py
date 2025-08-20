import json
import os
import argparse
from typing import List, Dict

def analyze_results(results_dir: str):
    """
    Analyzes all evaluation_results_*.json files in a directory and prints a summary table.
    """
    all_metrics = []
    for filename in os.listdir(results_dir):
        if filename.startswith("evaluation_results_") and filename.endswith(".json"):
            filepath = os.path.join(results_dir, filename)
            with open(filepath, "r") as f:
                results_data = json.load(f)

            total_tasks = len(results_data)
            if total_tasks == 0:
                continue

            executable_queries = sum(1 for r in results_data if r['execution_status'] != "INCORRECT_SYNTAX")
            correct_queries = sum(1 for r in results_data if r['comparison_status'] == 1)

            execution_accuracy = (executable_queries / total_tasks) * 100
            correct_sql_accuracy = (correct_queries / total_tasks) * 100

            all_metrics.append({
                "filename": filename,
                "execution_accuracy": execution_accuracy,
                "correct_sql_accuracy": correct_sql_accuracy
            })

    print_summary_table(all_metrics)

def print_summary_table(metrics: List[Dict]):
    """
    Prints a formatted summary table of the analysis results.
    """
    if not metrics:
        print("No evaluation results found to analyze.")
        return

    print(f"{'Filename':<50} | {'Execution Accuracy (%)':<25} | {'Correct SQL Accuracy (%)':<25}")
    print("-" * 105)

    for m in metrics:
        print(f"{m['filename']:<50} | {m['execution_accuracy']:<25.2f} | {m['correct_sql_accuracy']:<25.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze evaluation results.")
    parser.add_argument(
        "--results_dir",
        type=str,
        default="results",
        help="The directory containing the evaluation results JSON files."
    )
    args = parser.parse_args()
    analyze_results(args.results_dir)