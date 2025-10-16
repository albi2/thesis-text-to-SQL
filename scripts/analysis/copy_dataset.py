import json

# --- file paths ---
SOURCE_FILE = "./dataset/dev/dev.json"
DEST_FILE = "./dataset/dev/bird_subset.json"

# --- load JSON files ---
with open(SOURCE_FILE, "r", encoding="utf-8") as f:
    source_items = json.load(f)

with open(DEST_FILE, "r", encoding="utf-8") as f:
    dest_items = json.load(f)

# --- build lookup by question_id ---
source_lookup = {item["question_id"]: item for item in source_items}

# --- rebuild destination ---
new_dest_items = []
missing_items = []

for item in dest_items:
    qid = item.get("question_id")
    if qid in source_lookup:
        new_dest_items.append(source_lookup[qid])
    else:
        missing_items.append(item)

# --- save updated destination file ---
with open(DEST_FILE, "w", encoding="utf-8") as f:
    json.dump(new_dest_items, f, indent=2, ensure_ascii=False)

# --- report ---
print(f"✅ Updated {DEST_FILE} with {len(new_dest_items)} items.")
if missing_items:
    print(f"\n⚠️ {len(missing_items)} items were not found in source.json:")
    for item in missing_items:
        print(f"  - question_id: {item.get('question_id')}")
else:
    print("\n✅ All destination items were found in the source file.")
