#!/usr/bin/env python3
import argparse
import json
import sys
import os

from util.db.execute import compare_sqls_outcomes
from infrastructure.database.database_manager import DatabaseManager


def main():
    parser = argparse.ArgumentParser(description="Compare generated SQL vs gold SQL for JSON items and update results.")
    parser.add_argument("--results_path", required=True, help="Path to the JSON file containing the generated SQL results.")
    parser.add_argument("--questions_path", required=True, help="Path to the JSON file containing the question metadata.")
    args = parser.parse_args()

    # Validate files
    if not os.path.exists(args.results_path):
        print(f"❌ Results JSON file not found: {args.results_path}")
        sys.exit(1)
    if not os.path.exists(args.questions_path):
        print(f"❌ Questions JSON file not found: {args.questions_path}")
        sys.exit(1)

    # Load data
    with open(args.results_path, "r") as f:
        results_data = json.load(f)

    with open(args.questions_path, "r") as f:
        questions_data = json.load(f)

    if not isinstance(results_data, list) or not isinstance(questions_data, list):
        print("❌ Both JSON files must contain arrays of items.")
        sys.exit(1)

    if len(results_data) != len(questions_data):
        print("❌ The number of items in results and questions JSON files do not match.")
        sys.exit(1)

    print(f"🔍 Comparing {len(results_data)} SQL query pairs...")

    db_manager = DatabaseManager()

    for i, (result_item, question_item) in enumerate(zip(results_data, questions_data)):
        gold_sql = result_item.get("gold_sql")
        gen_sql = result_item.get("generated_sql")
        db_id = question_item.get("db_id", "toxicology")

        # Default to 0 if anything fails
        comparison_status = 0

        if not gold_sql:
            print(f"[{i}] ⚠️ Missing gold SQL — skipping.")
        elif not gen_sql:
            print(f"[{i}] ⚠️ Missing generated SQL — skipping.")
        else:
            try:
                database_engine = db_manager.create_engine(db_id)
                # Use your provided SQL comparison utility
                comparison_status = compare_sqls_outcomes(gen_sql, gold_sql, "public", database_engine)
                print(f"[{i}] ✅ comparison_status → {comparison_status} (db={db_id})")
            except Exception as e:
                print(f"[{i}] ❌ Error comparing SQLs: {e}")
                comparison_status = 0

        result_item["comparison_status"] = comparison_status

    # Save back to the same file
    with open(args.results_path, "w") as f:
        json.dump(results_data, f, indent=4)

    print(f"✅ Updated JSON file saved in place: {args.results_path}")


if __name__ == "__main__":
    main()