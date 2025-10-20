import json
from tqdm import tqdm
from util.db.execute import compare_sqls_outcomes
from infrastructure.database.database_manager import DatabaseManager

# --- Configuration ---
generated_json_path = "../results/contexts_20251020_153012.json"  # file with "generated_sql_queries"
gold_json_path = "./dataset/dev/bird_subset.json"                 # file with "question", "SQL", etc.
output_path = "./comparison_results.json"                         # where to save results

# --- Load data ---
with open(generated_json_path, "r", encoding="utf-8") as f:
    generated_data = json.load(f)

with open(gold_json_path, "r", encoding="utf-8") as f:
    gold_data = json.load(f)

db_manager = DatabaseManager()
assert len(generated_data) == len(gold_data), "JSON arrays must have the same length"

# --- Stats trackers ---
stats = {
    "total": 0,
    "matched": 0,
    "unmatched": 0,
    "error": 0,
    "selected_matched": 0,
    "selected_error": 0,
}

results = []

# --- Compare each pair ---
for gen_item, gold_item in tqdm(zip(generated_data, gold_data), total=len(gold_data)):
    db_id = gold_item.get("db_id")
    gold_sql = gold_item.get("SQL")
    question = gold_item.get("question")
    question_id = gold_item.get("question_id")

    # Create database engine for that DB
    database_engine = db_manager.create_engine(db_id)

    found_match = False
    matching_generated_sql = None
    comparison_error = False

    # --- Compare all generated SQLs ---
    for g in gen_item.get("generated_sql_queries", []):
        gen_sql = g.get("sql_exec_info", {}).get("sql")
        if not gen_sql:
            continue

        try:
            comparison_status = compare_sqls_outcomes(gen_sql, gold_sql, "public", database_engine)
        except Exception as e:
            comparison_status = -1
            comparison_error = True
            print(f"[{db_id}] ❌ Error comparing SQLs: {e}")
            continue

        if comparison_status == 1:
            found_match = True
            matching_generated_sql = gen_sql
            break

    # --- Compare selected_sql_query (if present) ---
    selected_sql_query_info = gen_item.get("selected_sql_query", {})
    selected_sql_exec_info = selected_sql_query_info.get("sql_exec_info", {}) if selected_sql_query_info else {}
    selected_sql = selected_sql_exec_info.get("sql")

    selected_match = False
    selected_error = False

    if selected_sql:
        try:
            selected_status = compare_sqls_outcomes(selected_sql, gold_sql, "public", database_engine)
            if selected_status == 1:
                selected_match = True
        except Exception as e:
            selected_error = True
            print(f"[{db_id}] ⚠️ Error comparing selected_sql_query: {e}")

    # --- Update stats ---
    stats["total"] += 1
    if comparison_error:
        stats["error"] += 1
    elif found_match:
        stats["matched"] += 1
    else:
        stats["unmatched"] += 1

    if selected_match:
        stats["selected_matched"] += 1
    if selected_error:
        stats["selected_error"] += 1

    # --- Record results ---
    result_entry = {
        "question_id": question_id,
        "db_id": db_id,
        "question": question,
        "gold_sql": gold_sql,
        "matched": found_match,
        "matching_generated_sql": matching_generated_sql,
        "error": comparison_error,
        "selected_sql_query": selected_sql,  # just the SQL string for readability
        "selected_matched": selected_match,
        "selected_error": selected_error,
    }
    results.append(result_entry)

# --- Save results ---
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# --- Print statistics ---
accuracy = (stats["matched"] / stats["total"]) * 100 if stats["total"] > 0 else 0
selected_accuracy = (stats["selected_matched"] / stats["total"]) * 100 if stats["total"] > 0 else 0

print("\n📊 --- SQL Comparison Summary ---")
print(f"Total items             : {stats['total']}")
print(f"Matched (any generated) : {stats['matched']}")
print(f"Unmatched               : {stats['unmatched']}")
print(f"Errors (generated)      : {stats['error']}")
print(f"Accuracy (generated)    : {accuracy:.2f}%")
print()
print(f"Selected SQL matched    : {stats['selected_matched']}")
print(f"Selected SQL errors     : {stats['selected_error']}")
print(f"Accuracy (selected_sql) : {selected_accuracy:.2f}%")
print(f"\n✅ Detailed results saved to: {output_path}")
