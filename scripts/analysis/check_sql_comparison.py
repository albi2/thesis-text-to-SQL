#!/usr/bin/env python3
import argparse
import json
import sys
import os
import glob

from util.db.execute import compare_sqls_outcomes
from infrastructure.database.database_manager import DatabaseManager


def process_file(results_path, questions_data, db_manager):
    """Compare and update comparison_status for a single results JSON file."""
    with open(results_path, "r") as f:
        results_data = json.load(f)

    if not isinstance(results_data, list):
        print(f"❌ Skipping {results_path} — not a JSON array.")
        return 0, 0

    if len(results_data) != len(questions_data):
        print(f"❌ Skipping {results_path} — number of items does not match questions file.")
        return 0, 0

    print(f"\n🔍 Processing {os.path.basename(results_path)} ({len(results_data)} items)...")

    updated_count = 0

    for i, (result_item, question_item) in enumerate(zip(results_data, questions_data)):
        question_text = question_item.get("question", f"[Question {i}]")
        gold_sql = result_item.get("gold_sql")
        gen_sql = result_item.get("generated_sql")
        db_id = question_item.get("db_id", "toxicology")

        if not gold_sql:
            print(f"⚠️  Skipping '{question_text}' — missing gold SQL.")
            continue
        if not gen_sql:
            print(f"⚠️  Skipping '{question_text}' — missing generated SQL.")
            continue

        try:
            database_engine = db_manager.create_engine(db_id)
            comparison_status = compare_sqls_outcomes(gen_sql, gold_sql, "public", database_engine)

            if comparison_status == 1:
                result_item["comparison_status"] = 1
                updated_count += 1
                print(f"✅ '{question_text}' → comparison_status updated to 1 (db={db_id})")
            else:
                print(f"⚙️  '{question_text}' → comparison result = 0 (no update)")

        except Exception as e:
            print(f"❌ '{question_text}' → Error comparing SQLs: {e}")

    # Save updates
    with open(results_path, "w") as f:
        json.dump(results_data, f, indent=4)

    print(f"💾 Saved updates to: {results_path}")
    return updated_count, len(results_data)


def main():
    parser = argparse.ArgumentParser(
        description="Compare generated SQL vs gold SQL for multiple result files."
    )
    parser.add_argument(
        "--results_dir",
        required=True,
        help="Directory containing evaluation_results*.json files.",
    )
    parser.add_argument(
        "--questions_path",
        required=True,
        help="Path to the JSON file containing the question metadata.",
    )
    args = parser.parse_args()

    # Validate paths
    if not os.path.isdir(args.results_dir):
        print(f"❌ Directory not found: {args.results_dir}")
        sys.exit(1)
    if not os.path.exists(args.questions_path):
        print(f"❌ Questions JSON file not found: {args.questions_path}")
        sys.exit(1)

    # Load questions once
    with open(args.questions_path, "r") as f:
        questions_data = json.load(f)

    if not isinstance(questions_data, list):
        print("❌ Questions JSON file must contain an array.")
        sys.exit(1)

    # Find all result files
    result_files = sorted(glob.glob(os.path.join(args.results_dir, "evaluation_results*.json")))

    if not result_files:
        print(f"⚠️ No evaluation_results*.json files found in {args.results_dir}")
        sys.exit(0)

    print(f"🧩 Found {len(result_files)} result files to process.")
    db_manager = DatabaseManager()

    total_updated = 0
    total_items = 0

    for results_path in result_files:
        updated, count = process_file(results_path, questions_data, db_manager)
        total_updated += updated
        total_items += count

    print("\n✅ All files processed.")
    print(f"📊 Total items updated: {total_updated} / {total_items}")
    print(f"📁 Directory: {args.results_dir}")


if __name__ == "__main__":
    main()
