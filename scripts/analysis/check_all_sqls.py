import json
from tqdm import tqdm
from util.db.execute import compare_sqls_outcomes
from infrastructure.database.database_manager import DatabaseManager
from typing import List, Dict, Tuple, Optional
import hashlib
from collections import Counter

class QueryResultCache:
    """Cache for SQL query comparison results to avoid redundant database calls."""
    
    def __init__(self):
        self._comparison_cache: Dict[Tuple[str, str], int] = {}
    
    def _hash_sql(self, sql: str) -> str:
        """Create a hash for SQL query to use as cache key."""
        return hashlib.md5(sql.encode('utf-8')).hexdigest()
    
    def get_comparison(self, sql_1: str, sql_2: str) -> Optional[int]:
        """Get cached comparison result between two queries."""
        key1 = (self._hash_sql(sql_1), self._hash_sql(sql_2))
        key2 = (self._hash_sql(sql_2), self._hash_sql(sql_1))
        
        if key1 in self._comparison_cache:
            return self._comparison_cache[key1]
        if key2 in self._comparison_cache:
            return self._comparison_cache[key2]
        return None
    
    def set_comparison(self, sql_1: str, sql_2: str, result: int):
        """Cache the comparison result between two queries."""
        key = (self._hash_sql(sql_1), self._hash_sql(sql_2))
        self._comparison_cache[key] = result
    
    def clear(self):
        """Clear all cached data."""
        self._comparison_cache.clear()


def cluster_equivalent_queries(queries: List[Dict], gold_sql: str, db_path: str, engine, cache: QueryResultCache) -> Tuple[List[List[Dict]], int]:
    """Cluster queries based on equivalent results."""
    if not queries:
        return [], -1
    
    clusters = []
    visited = [False] * len(queries)

    for i in range(len(queries)):
        if visited[i]:
            continue
        
        current_cluster = [queries[i]]
        visited[i] = True
        
        sql_i = queries[i].get("sql_exec_info", {}).get("sql")
        if not sql_i:
            continue
        
        for j in range(i + 1, len(queries)):
            if not visited[j]:
                sql_j = queries[j].get("sql_exec_info", {}).get("sql")
                if not sql_j:
                    continue
                
                cached_result = cache.get_comparison(sql_i, sql_j)
                if cached_result is not None:
                    are_equivalent = (cached_result == 1)
                else:
                    try:
                        comparison_status = compare_sqls_outcomes(sql_i, sql_j, db_path, engine)
                        cache.set_comparison(sql_i, sql_j, comparison_status)
                        are_equivalent = (comparison_status == 1)
                    except Exception:
                        are_equivalent = False
                
                if are_equivalent:
                    current_cluster.append(queries[j])
                    visited[j] = True
        
        clusters.append(current_cluster)
    
    if clusters:
        largest_cluster_idx = max(range(len(clusters)), key=lambda i: len(clusters[i]))
        return clusters, largest_cluster_idx
    return [], -1


def select_by_self_consistency(queries: List[Dict], gold_sql: str, db_path: str, engine, cache: QueryResultCache) -> Tuple[Optional[str], int, bool, float]:
    """
    Select query from largest cluster (self-consistency).
    Returns (selected_sql, cluster_size, matches_gold, selected_query_score)
    """
    if not queries:
        return None, 0, False, float('-inf')
    
    clusters, largest_idx = cluster_equivalent_queries(queries, gold_sql, db_path, engine, cache)
    
    if largest_idx == -1:
        return None, 0, False, float('-inf')
    
    largest_cluster = clusters[largest_idx]
    cluster_size = len(largest_cluster)
    
    selected_query = largest_cluster[0]
    selected_sql = selected_query.get("sql_exec_info", {}).get("sql")
    selected_score = selected_query.get("score", float('-inf')) # Get the original score of the selected query
    
    if selected_sql:
        try:
            cached_result = cache.get_comparison(selected_sql, gold_sql)
            if cached_result is not None:
                matches = (cached_result == 1)
            else:
                comparison_status = compare_sqls_outcomes(selected_sql, gold_sql, db_path, engine)
                cache.set_comparison(selected_sql, gold_sql, comparison_status)
                matches = (comparison_status == 1)
        except Exception:
            matches = False
    else:
        matches = False
    
    return selected_sql, cluster_size, matches, selected_score # Return the original score


def select_highest_score_from_methods(methods: List[Tuple[str, str, float]]) -> Tuple[Optional[str], Optional[str]]:
    """
    Select the method with highest score from a list of (method_name, sql, score) tuples.
    Returns (selected_sql, method_name)
    """
    valid_methods = [(name, sql, score) for name, sql, score in methods if sql is not None]
    if not valid_methods:
        return None, None
    
    # Use max score as the primary key for sorting
    best = max(valid_methods, key=lambda x: x[2])
    return best[1], best[0]


def voting_among_methods(methods: List[Tuple[str, str]], gold_sql: str, db_path: str, engine, cache: QueryResultCache) -> Tuple[Optional[str], int, bool]:
    """
    Cluster SQLs from multiple methods and select by voting (largest cluster).
    Returns (selected_sql, num_votes, matches_gold)
    """
    # Filter out None SQLs
    valid_sqls = [(name, sql) for name, sql in methods if sql is not None]
    if not valid_sqls:
        return None, 0, False
    
    # Group equivalent SQLs using clustering
    sql_to_methods = {}
    processed_indices = set()
    clusters = []
    
    for i, (name_i, sql_i) in enumerate(valid_sqls):
        if i in processed_indices:
            continue
        
        cluster = [(name_i, sql_i)]
        processed_indices.add(i)
        
        for j in range(i + 1, len(valid_sqls)):
            if j in processed_indices:
                continue
            
            name_j, sql_j = valid_sqls[j]
            
            cached_result = cache.get_comparison(sql_i, sql_j)
            if cached_result is not None:
                are_equivalent = (cached_result == 1)
            else:
                try:
                    comparison_status = compare_sqls_outcomes(sql_i, sql_j, db_path, engine)
                    cache.set_comparison(sql_i, sql_j, comparison_status)
                    are_equivalent = (comparison_status == 1)
                except Exception:
                    are_equivalent = False
            
            if are_equivalent:
                cluster.append((name_j, sql_j))
                processed_indices.add(j)
        
        clusters.append(cluster)
    
    # Find largest cluster (most votes)
    if not clusters:
        return None, 0, False
    
    largest_cluster = max(clusters, key=len)
    num_votes = len(largest_cluster)
    selected_sql = largest_cluster[0][1]
    
    # Check if it matches gold
    if selected_sql:
        try:
            cached_result = cache.get_comparison(selected_sql, gold_sql)
            if cached_result is not None:
                matches = (cached_result == 1)
            else:
                comparison_status = compare_sqls_outcomes(selected_sql, gold_sql, db_path, engine)
                cache.set_comparison(selected_sql, gold_sql, comparison_status)
                matches = (comparison_status == 1)
        except Exception:
            matches = False
    else:
        matches = False
    
    return selected_sql, num_votes, matches


# --- Configuration ---
generated_json_path = "../results/contexts_20251101_233307.json"
gold_json_path = "./dataset/dev/bird_subset.json"
output_path = "./comparison_results.json"

# --- Load data ---
with open(generated_json_path, "r", encoding="utf-8") as f:
    generated_data = json.load(f)

with open(gold_json_path, "r", encoding="utf-8") as f:
    gold_data = json.load(f)

db_manager = DatabaseManager()
# assert len(generated_data) == len(gold_data), "JSON arrays must have the same length"
if len(generated_data) < len(gold_data):
    gold_data = gold_data[:len(generated_data)]

cache = QueryResultCache()

# --- Stats trackers ---
stats = {
    "total": 0,
    "matched": 0,
    "unmatched": 0,
    "error": 0,
    "selected_matched": 0,
    "tournament_matched": 0,
    "usc_matched": 0,
    "hybrid_matched": 0,
    "best_score_matched": 0,
    "self_consistency_matched": 0,
    
    # OR combinations (if either matches)
    "any_method_matched": 0,
    "selected_or_tournament": 0,
    "selected_or_usc": 0,
    "selected_or_hybrid": 0,
    "selected_or_best_score": 0,
    "selected_or_self_consistency": 0,
    "tournament_or_usc": 0,
    "tournament_or_hybrid": 0,
    "tournament_or_best_score": 0,
    "tournament_or_self_consistency": 0,
    "usc_or_hybrid": 0,
    "usc_or_best_score": 0,
    "usc_or_self_consistency": 0,
    "hybrid_or_best_score": 0,
    "hybrid_or_self_consistency": 0,
    "best_score_or_self_consistency": 0,
    "all_methods_matched": 0,
    
    # Score-based combinations
    "score_selected_or_tournament": 0,
    "score_selected_or_usc": 0,
    "score_selected_or_hybrid": 0,
    "score_selected_or_best_score": 0,
    "score_selected_or_self_consistency": 0,     # NEW
    "score_tournament_or_usc": 0,
    "score_tournament_or_hybrid": 0,
    "score_tournament_or_best_score": 0,
    "score_tournament_or_self_consistency": 0,   # NEW
    "score_usc_or_hybrid": 0,
    "score_usc_or_best_score": 0,
    "score_usc_or_self_consistency": 0,          # NEW
    "score_hybrid_or_best_score": 0,
    "score_hybrid_or_self_consistency": 0,       # NEW
    "score_best_score_or_self_consistency": 0,   # NEW
    "score_all_six": 0,                          # RENAMED
    
    # Voting-based combinations (quadruples and more)
    "vote_all_four": 0,                          # Kept for compatibility
    "vote_all_six": 0,                           # NEW
    
    # Voting-based combinations (triples)
    "vote_selected_tournament_usc": 0,
    "vote_selected_tournament_hybrid": 0,
    "vote_selected_tournament_best_score": 0,
    "vote_selected_usc_hybrid": 0,
    "vote_selected_usc_best_score": 0,
    "vote_selected_hybrid_best_score": 0,
    "vote_tournament_usc_hybrid": 0,
    "vote_tournament_usc_best_score": 0,
    "vote_tournament_hybrid_best_score": 0,
    "vote_usc_hybrid_best_score": 0,    
    "vote_selected_tournament_self": 0,
    "vote_selected_usc_self": 0,
    "vote_selected_hybrid_self": 0,
    "vote_selected_best_score_self": 0,
    "vote_tournament_usc_self": 0,
    "vote_tournament_hybrid_self": 0,
    "vote_tournament_best_score_self": 0,
    "vote_usc_hybrid_self": 0,
    "vote_usc_best_score_self": 0,
    "vote_hybrid_best_score_self": 0,
}

results = []

# --- Compare each pair ---
for gen_item, gold_item in tqdm(zip(generated_data, gold_data), total=len(gold_data)):
    db_id = gold_item.get("db_id")
    gold_sql = gold_item.get("SQL")
    question = gold_item.get("question")
    question_id = gold_item.get("question_id")

    database_engine = db_manager.create_engine(db_id)

    found_match = False
    matching_generated_sql = None
    comparison_error = False

    # --- Compare all generated SQLs ---
    for g in gen_item.get("generated_sql_queries", []):
        gen_sql = g.get("sql_exec_info", {}).get("sql")
        if not gen_sql:
            continue

        cached_result = cache.get_comparison(gen_sql, gold_sql)
        if cached_result is not None:
            comparison_status = cached_result
        else:
            try:
                comparison_status = compare_sqls_outcomes(gen_sql, gold_sql, "public", database_engine)
                cache.set_comparison(gen_sql, gold_sql, comparison_status)
            except Exception as e:
                comparison_status = -1
                comparison_error = True
                print(f"[{db_id}] ❌ Error comparing SQLs: {e}")
                continue

        if comparison_status == 1:
            found_match = True
            matching_generated_sql = gen_sql
            break

    # --- Get method results ---
    selected_sql_query_info = gen_item.get("selected_sql_query", {})
    selected_sql = selected_sql_query_info.get("sql_exec_info", {}).get("sql") if selected_sql_query_info else None
    selected_score = selected_sql_query_info.get("score", float('-inf')) if selected_sql_query_info else float('-inf')

    winning_queries = gen_item.get("winning_queries", [])
    tournament_sql = winning_queries[0].get("sql_exec_info", {}).get("sql") if len(winning_queries) > 0 else None
    tournament_score = winning_queries[0].get("score", float('-inf')) if len(winning_queries) > 0 else float('-inf')
    
    usc_sql = winning_queries[1].get("sql_exec_info", {}).get("sql") if len(winning_queries) > 1 else None
    usc_score = winning_queries[1].get("score", float('-inf')) if len(winning_queries) > 1 else float('-inf')

    # Hybrid
    hybrid_sql = None
    hybrid_score = float('-inf')
    if len(winning_queries) == 2:
        if tournament_score > usc_score:
            hybrid_sql = tournament_sql
            hybrid_score = tournament_score
        elif usc_score > tournament_score:
            hybrid_sql = usc_sql
            hybrid_score = usc_score
        else:
            hybrid_sql = selected_sql if selected_sql else tournament_sql
            hybrid_score = selected_score if selected_sql else tournament_score

    # Best score
    generated_sql_queries = gen_item.get("generated_sql_queries", [])
    best_score_sql = None
    best_score_score = float('-inf')
    if generated_sql_queries:
        max_score = max((g.get("score", float('-inf')) for g in generated_sql_queries), default=float('-inf'))
        max_score_queries = [g for g in generated_sql_queries if g.get("score", float('-inf')) == max_score]
        
        if len(max_score_queries) > 1 and selected_sql:
            if any(g.get("sql_exec_info", {}).get("sql") == selected_sql for g in max_score_queries):
                best_score_sql = selected_sql
            else:
                best_score_sql = max_score_queries[0].get("sql_exec_info", {}).get("sql")
        elif max_score_queries:
            best_score_sql = max_score_queries[0].get("sql_exec_info", {}).get("sql")
        best_score_score = max_score

    # Self-consistency
    # MODIFICATION: Capture the original score of the selected query
    self_consistency_sql, cluster_size, _, self_consistency_score = select_by_self_consistency(
        generated_sql_queries, gold_sql, "public", database_engine, cache
    )

    # --- Check individual methods ---
    def check_match(sql):
        if not sql:
            return False
        cached = cache.get_comparison(sql, gold_sql)
        if cached is not None:
            return cached == 1
        try:
            status = compare_sqls_outcomes(sql, gold_sql, "public", database_engine)
            cache.set_comparison(sql, gold_sql, status)
            return status == 1
        except:
            return False

    selected_match = check_match(selected_sql)
    tournament_match = check_match(tournament_sql)
    usc_match = check_match(usc_sql)
    hybrid_match = check_match(hybrid_sql)
    best_score_match = check_match(best_score_sql)
    self_consistency_match = check_match(self_consistency_sql)

    # --- Score-based pairwise combinations ---
    # MODIFICATION: Use the original score from the self-consistency-selected query
    methods_data = [
        ("selected", selected_sql, selected_score),
        ("tournament", tournament_sql, tournament_score),
        ("usc", usc_sql, usc_score),
        ("hybrid", hybrid_sql, hybrid_score),
        ("best_score", best_score_sql, best_score_score),
        ("self_consistency", self_consistency_sql, self_consistency_score), # Use the original score
    ]

    score_results = {}
    
    # MODIFICATION: Added all pairs for self_consistency
    pairs = [
        (["selected", "tournament"], "score_selected_or_tournament"),
        (["selected", "usc"], "score_selected_or_usc"),
        (["selected", "hybrid"], "score_selected_or_hybrid"),
        (["selected", "best_score"], "score_selected_or_best_score"),
        (["selected", "self_consistency"], "score_selected_or_self_consistency"),
        (["tournament", "usc"], "score_tournament_or_usc"),
        (["tournament", "hybrid"], "score_tournament_or_hybrid"),
        (["tournament", "best_score"], "score_tournament_or_best_score"),
        (["tournament", "self_consistency"], "score_tournament_or_self_consistency"),
        (["usc", "hybrid"], "score_usc_or_hybrid"),
        (["usc", "best_score"], "score_usc_or_best_score"),
        (["usc", "self_consistency"], "score_usc_or_self_consistency"),
        (["hybrid", "best_score"], "score_hybrid_or_best_score"),
        (["hybrid", "self_consistency"], "score_hybrid_or_self_consistency"),
        (["best_score", "self_consistency"], "score_best_score_or_self_consistency"),
    ]
    
    for method_names, stat_key in pairs:
        methods_subset = [(n, s, sc) for n, s, sc in methods_data if n in method_names]
        selected_sql_result, _ = select_highest_score_from_methods(methods_subset)
        score_results[stat_key] = check_match(selected_sql_result)
        if score_results[stat_key]:
            stats[stat_key] += 1

    # MODIFICATION: Changed from "all four" to "all six"
    score_all_six_sql, _ = select_highest_score_from_methods(methods_data)
    score_all_six_match = check_match(score_all_six_sql)
    score_results["score_all_six"] = score_all_six_match
    if score_all_six_match:
        stats["score_all_six"] += 1

    # --- Voting-based combinations ---
    voting_results = {}
    
    # All six methods (quadruple)
    # MODIFICATION: Changed from "all four" to "all six"
    all_methods_for_voting = [
        ("selected", selected_sql), 
        ("tournament", tournament_sql), 
        ("usc", usc_sql), 
        ("hybrid", hybrid_sql),
        ("best_score", best_score_sql),
        ("self_consistency", self_consistency_sql)
    ]
    vote_all_six_sql, vote_all_six_votes, vote_all_six_match = voting_among_methods(
        all_methods_for_voting,
        gold_sql, "public", database_engine, cache
    )
    voting_results["vote_all_six"] = vote_all_six_match
    if vote_all_six_match:
        stats["vote_all_six"] += 1
        
    # Keep old vote_all_four for reference
    vote_all_four_sql, vote_all_four_votes, vote_all_four_match = voting_among_methods(
        [("selected", selected_sql), ("tournament", tournament_sql), 
         ("usc", usc_sql), ("hybrid", hybrid_sql)],
        gold_sql, "public", database_engine, cache
    )
    voting_results["vote_all_four"] = vote_all_four_match
    if vote_all_four_match:
        stats["vote_all_four"] += 1


    # MODIFICATION: Added all triples for self_consistency
    triples = [
        # Original 10
        ([("selected", selected_sql), ("tournament", tournament_sql), ("usc", usc_sql)], 
         "vote_selected_tournament_usc"),
        ([("selected", selected_sql), ("tournament", tournament_sql), ("hybrid", hybrid_sql)], 
         "vote_selected_tournament_hybrid"),
        ([("selected", selected_sql), ("tournament", tournament_sql), ("best_score", best_score_sql)], 
         "vote_selected_tournament_best_score"),
        ([("selected", selected_sql), ("usc", usc_sql), ("hybrid", hybrid_sql)], 
         "vote_selected_usc_hybrid"),
        ([("selected", selected_sql), ("usc", usc_sql), ("best_score", best_score_sql)], 
         "vote_selected_usc_best_score"),
        ([("selected", selected_sql), ("hybrid", hybrid_sql), ("best_score", best_score_sql)], 
         "vote_selected_hybrid_best_score"),
        ([("tournament", tournament_sql), ("usc", usc_sql), ("hybrid", hybrid_sql)], 
         "vote_tournament_usc_hybrid"),
        ([("tournament", tournament_sql), ("usc", usc_sql), ("best_score", best_score_sql)], 
         "vote_tournament_usc_best_score"),
        ([("tournament", tournament_sql), ("hybrid", hybrid_sql), ("best_score", best_score_sql)], 
         "vote_tournament_hybrid_best_score"),
        ([("usc", usc_sql), ("hybrid", hybrid_sql), ("best_score", best_score_sql)], 
         "vote_usc_hybrid_best_score"),
         
        # New 10 with self_consistency (using 'self' as key)
        ([("selected", selected_sql), ("tournament", tournament_sql), ("self_consistency", self_consistency_sql)], 
         "vote_selected_tournament_self"),
        ([("selected", selected_sql), ("usc", usc_sql), ("self_consistency", self_consistency_sql)], 
         "vote_selected_usc_self"),
        ([("selected", selected_sql), ("hybrid", hybrid_sql), ("self_consistency", self_consistency_sql)], 
         "vote_selected_hybrid_self"),
        ([("selected", selected_sql), ("best_score", best_score_sql), ("self_consistency", self_consistency_sql)], 
         "vote_selected_best_score_self"),
        ([("tournament", tournament_sql), ("usc", usc_sql), ("self_consistency", self_consistency_sql)], 
         "vote_tournament_usc_self"),
        ([("tournament", tournament_sql), ("hybrid", hybrid_sql), ("self_consistency", self_consistency_sql)], 
         "vote_tournament_hybrid_self"),
        ([("tournament", tournament_sql), ("best_score", best_score_sql), ("self_consistency", self_consistency_sql)], 
         "vote_tournament_best_score_self"),
        ([("usc", usc_sql), ("hybrid", hybrid_sql), ("self_consistency", self_consistency_sql)], 
         "vote_usc_hybrid_self"),
        ([("usc", usc_sql), ("best_score", best_score_sql), ("self_consistency", self_consistency_sql)], 
         "vote_usc_best_score_self"),
        ([("hybrid", hybrid_sql), ("best_score", best_score_sql), ("self_consistency", self_consistency_sql)], 
         "vote_hybrid_best_score_self"),
    ]
    
    for methods_list, stat_key in triples:
        vote_sql, votes, match = voting_among_methods(methods_list, gold_sql, "public", database_engine, cache)
        voting_results[stat_key] = match
        if match:
            stats[stat_key] += 1

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
    if tournament_match:
        stats["tournament_matched"] += 1
    if usc_match:
        stats["usc_matched"] += 1
    if hybrid_match:
        stats["hybrid_matched"] += 1
    if best_score_match:
        stats["best_score_matched"] += 1
    if self_consistency_match:
        stats["self_consistency_matched"] += 1

    # --- Update OR combination stats (if either matches) ---
    any_method = (selected_match or tournament_match or usc_match or 
                  hybrid_match or best_score_match or self_consistency_match)
    all_methods = (selected_match and tournament_match and usc_match and 
                   hybrid_match and best_score_match and self_consistency_match)
    
    if any_method:
        stats["any_method_matched"] += 1
    if selected_match or tournament_match:
        stats["selected_or_tournament"] += 1
    if selected_match or usc_match:
        stats["selected_or_usc"] += 1
    if selected_match or hybrid_match:
        stats["selected_or_hybrid"] += 1
    if selected_match or best_score_match:
        stats["selected_or_best_score"] += 1
    if selected_match or self_consistency_match:
        stats["selected_or_self_consistency"] += 1
    if tournament_match or usc_match:
        stats["tournament_or_usc"] += 1
    if tournament_match or hybrid_match:
        stats["tournament_or_hybrid"] += 1
    if tournament_match or best_score_match:
        stats["tournament_or_best_score"] += 1
    if tournament_match or self_consistency_match:
        stats["tournament_or_self_consistency"] += 1
    if usc_match or hybrid_match:
        stats["usc_or_hybrid"] += 1
    if usc_match or best_score_match:
        stats["usc_or_best_score"] += 1
    if usc_match or self_consistency_match:
        stats["usc_or_self_consistency"] += 1
    if hybrid_match or best_score_match:
        stats["hybrid_or_best_score"] += 1
    if hybrid_match or self_consistency_match:
        stats["hybrid_or_self_consistency"] += 1
    if best_score_match or self_consistency_match:
        stats["best_score_or_self_consistency"] += 1
    if all_methods:
        stats["all_methods_matched"] += 1

    # --- Record results ---
    result_entry = {
        "question_id": question_id,
        "db_id": db_id,
        "question": question,
        "gold_sql": gold_sql,
        "matched": found_match,
        "selected_matched": selected_match,
        "tournament_matched": tournament_match,
        "usc_matched": usc_match,
        "hybrid_matched": hybrid_match,
        "best_score_matched": best_score_match,
        "self_consistency_matched": self_consistency_match,
        "any_method_matched": any_method,
        "all_methods_matched": all_methods,
        **score_results,
        **voting_results,
    }
    results.append(result_entry)

# --- Save results ---
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# --- Calculate and print accuracies ---
def calc_acc(key):
    return (stats[key] / stats["total"]) * 100 if stats["total"] > 0 else 0

print("\n📊 === SQL COMPARISON SUMMARY ===\n")
print(f"Total items: {stats['total']}")

print("\n" + "="*60)
print("INDIVIDUAL METHOD PERFORMANCE")
print("="*60)
print(f"Selected       : {stats['selected_matched']:4d} ({calc_acc('selected_matched'):.2f}%)")
print(f"Tournament     : {stats['tournament_matched']:4d} ({calc_acc('tournament_matched'):.2f}%)")
print(f"USC            : {stats['usc_matched']:4d} ({calc_acc('usc_matched'):.2f}%)")
print(f"Hybrid         : {stats['hybrid_matched']:4d} ({calc_acc('hybrid_matched'):.2f}%)")
print(f"Best Score     : {stats['best_score_matched']:4d} ({calc_acc('best_score_matched'):.2f}%)")
print(f"Self-Consist.  : {stats['self_consistency_matched']:4d} ({calc_acc('self_consistency_matched'):.2f}%)")

print("\n" + "="*60)
print("OR COMBINATIONS (If Either Method Matches)")
print("="*60)
print(f"🎯 ANY method matched          : {stats['any_method_matched']:4d} ({calc_acc('any_method_matched'):.2f}%)")
print(f"\nPairwise OR combinations:")
print(f"  Selected OR Tournament        : {stats['selected_or_tournament']:4d} ({calc_acc('selected_or_tournament'):.2f}%)")
print(f"  Selected OR USC               : {stats['selected_or_usc']:4d} ({calc_acc('selected_or_usc'):.2f}%)")
print(f"  Selected OR Hybrid            : {stats['selected_or_hybrid']:4d} ({calc_acc('selected_or_hybrid'):.2f}%)")
print(f"  Selected OR Best Score        : {stats['selected_or_best_score']:4d} ({calc_acc('selected_or_best_score'):.2f}%)")
print(f"  Selected OR Self-Consistency  : {stats['selected_or_self_consistency']:4d} ({calc_acc('selected_or_self_consistency'):.2f}%)")
print(f"  Tournament OR USC             : {stats['tournament_or_usc']:4d} ({calc_acc('tournament_or_usc'):.2f}%)")
print(f"  Tournament OR Hybrid          : {stats['tournament_or_hybrid']:4d} ({calc_acc('tournament_or_hybrid'):.2f}%)")
print(f"  Tournament OR Best Score      : {stats['tournament_or_best_score']:4d} ({calc_acc('tournament_or_best_score'):.2f}%)")
print(f"  Tournament OR Self-Consistency: {stats['tournament_or_self_consistency']:4d} ({calc_acc('tournament_or_self_consistency'):.2f}%)")
print(f"  USC OR Hybrid                 : {stats['usc_or_hybrid']:4d} ({calc_acc('usc_or_hybrid'):.2f}%)")
print(f"  USC OR Best Score             : {stats['usc_or_best_score']:4d} ({calc_acc('usc_or_best_score'):.2f}%)")
print(f"  USC OR Self-Consistency       : {stats['usc_or_self_consistency']:4d} ({calc_acc('usc_or_self_consistency'):.2f}%)")
print(f"  Hybrid OR Best Score          : {stats['hybrid_or_best_score']:4d} ({calc_acc('hybrid_or_best_score'):.2f}%)")
print(f"  Hybrid OR Self-Consistency    : {stats['hybrid_or_self_consistency']:4d} ({calc_acc('hybrid_or_self_consistency'):.2f}%)")
print(f"  Best Score OR Self-Consistency: {stats['best_score_or_self_consistency']:4d} ({calc_acc('best_score_or_self_consistency'):.2f}%)")
print(f"\n✅ ALL methods matched         : {stats['all_methods_matched']:4d} ({calc_acc('all_methods_matched'):.2f}%)")

print("\n" + "="*60)
print("SCORE-BASED COMBINATIONS (Highest Score Selection)")
print("="*60)
print(f"Selected OR Tournament        : {stats['score_selected_or_tournament']:4d} ({calc_acc('score_selected_or_tournament'):.2f}%)")
print(f"Selected OR USC               : {stats['score_selected_or_usc']:4d} ({calc_acc('score_selected_or_usc'):.2f}%)")
print(f"Selected OR Hybrid            : {stats['score_selected_or_hybrid']:4d} ({calc_acc('score_selected_or_hybrid'):.2f}%)")
print(f"Selected OR Best Score        : {stats['score_selected_or_best_score']:4d} ({calc_acc('score_selected_or_best_score'):.2f}%)")
print(f"Selected OR Self-Consistency  : {stats['score_selected_or_self_consistency']:4d} ({calc_acc('score_selected_or_self_consistency'):.2f}%)")
print(f"Tournament OR USC             : {stats['score_tournament_or_usc']:4d} ({calc_acc('score_tournament_or_usc'):.2f}%)")
print(f"Tournament OR Hybrid          : {stats['score_tournament_or_hybrid']:4d} ({calc_acc('score_tournament_or_hybrid'):.2f}%)")
print(f"Tournament OR Best Score      : {stats['score_tournament_or_best_score']:4d} ({calc_acc('score_tournament_or_best_score'):.2f}%)")
print(f"Tournament OR Self-Consistency: {stats['score_tournament_or_self_consistency']:4d} ({calc_acc('score_tournament_or_self_consistency'):.2f}%)")
print(f"USC OR Hybrid                 : {stats['score_usc_or_hybrid']:4d} ({calc_acc('score_usc_or_hybrid'):.2f}%)")
print(f"USC OR Best Score             : {stats['score_usc_or_best_score']:4d} ({calc_acc('score_usc_or_best_score'):.2f}%)")
print(f"USC OR Self-Consistency       : {stats['score_usc_or_self_consistency']:4d} ({calc_acc('score_usc_or_self_consistency'):.2f}%)")
print(f"Hybrid OR Best Score          : {stats['score_hybrid_or_best_score']:4d} ({calc_acc('score_hybrid_or_best_score'):.2f}%)")
print(f"Hybrid OR Self-Consistency    : {stats['score_hybrid_or_self_consistency']:4d} ({calc_acc('score_hybrid_or_self_consistency'):.2f}%)")
print(f"Best Score OR Self-Consistency: {stats['score_best_score_or_self_consistency']:4d} ({calc_acc('score_best_score_or_self_consistency'):.2f}%)")
print(f"All Six (Highest Score)       : {stats['score_all_six']:4d} ({calc_acc('score_all_six'):.2f}%)")

print("\n" + "="*60)
print("VOTING-BASED COMBINATIONS (Self-Consistency Voting)")
print("="*60)
print(f"All Six Methods (Voting)      : {stats['vote_all_six']:4d} ({calc_acc('vote_all_six'):.2f}%)")
print(f"All Four (Legacy) (Voting)    : {stats['vote_all_four']:4d} ({calc_acc('vote_all_four'):.2f}%)")
print(f"\nTriples (Voting):")
print(f"  Sel + Tour + USC            : {stats['vote_selected_tournament_usc']:4d} ({calc_acc('vote_selected_tournament_usc'):.2f}%)")
print(f"  Sel + Tour + Hybrid         : {stats['vote_selected_tournament_hybrid']:4d} ({calc_acc('vote_selected_tournament_hybrid'):.2f}%)")
print(f"  Sel + Tour + BestScore      : {stats['vote_selected_tournament_best_score']:4d} ({calc_acc('vote_selected_tournament_best_score'):.2f}%)")
print(f"  Sel + USC + Hybrid          : {stats['vote_selected_usc_hybrid']:4d} ({calc_acc('vote_selected_usc_hybrid'):.2f}%)")
print(f"  Sel + USC + BestScore       : {stats['vote_selected_usc_best_score']:4d} ({calc_acc('vote_selected_usc_best_score'):.2f}%)")
print(f"  Sel + Hybrid + BestScore    : {stats['vote_selected_hybrid_best_score']:4d} ({calc_acc('vote_selected_hybrid_best_score'):.2f}%)")
print(f"  Tour + USC + Hybrid         : {stats['vote_tournament_usc_hybrid']:4d} ({calc_acc('vote_tournament_usc_hybrid'):.2f}%)")
print(f"  Tour + USC + BestScore      : {stats['vote_tournament_usc_best_score']:4d} ({calc_acc('vote_tournament_usc_best_score'):.2f}%)")
print(f"  Tour + Hybrid + BestScore   : {stats['vote_tournament_hybrid_best_score']:4d} ({calc_acc('vote_tournament_hybrid_best_score'):.2f}%)")
print(f"  USC + Hybrid + BestScore    : {stats['vote_usc_hybrid_best_score']:4d} ({calc_acc('vote_usc_hybrid_best_score'):.2f}%)")
print(f"\nTriples with Self-Consistency:")
print(f"  Sel + Tour + Self           : {stats['vote_selected_tournament_self']:4d} ({calc_acc('vote_selected_tournament_self'):.2f}%)")
print(f"  Sel + USC + Self            : {stats['vote_selected_usc_self']:4d} ({calc_acc('vote_selected_usc_self'):.2f}%)")
print(f"  Sel + Hybrid + Self         : {stats['vote_selected_hybrid_self']:4d} ({calc_acc('vote_selected_hybrid_self'):.2f}%)")
print(f"  Sel + BestScore + Self      : {stats['vote_selected_best_score_self']:4d} ({calc_acc('vote_selected_best_score_self'):.2f}%)")
print(f"  Tour + USC + Self           : {stats['vote_tournament_usc_self']:4d} ({calc_acc('vote_tournament_usc_self'):.2f}%)")
print(f"  Tour + Hybrid + Self        : {stats['vote_tournament_hybrid_self']:4d} ({calc_acc('vote_tournament_hybrid_self'):.2f}%)")
print(f"  Tour + BestScore + Self     : {stats['vote_tournament_best_score_self']:4d} ({calc_acc('vote_tournament_best_score_self'):.2f}%)")
print(f"  USC + Hybrid + Self         : {stats['vote_usc_hybrid_self']:4d} ({calc_acc('vote_usc_hybrid_self'):.2f}%)")
print(f"  USC + BestScore + Self      : {stats['vote_usc_best_score_self']:4d} ({calc_acc('vote_usc_best_score_self'):.2f}%)")
print(f"  Hybrid + BestScore + Self   : {stats['vote_hybrid_best_score_self']:4d} ({calc_acc('vote_hybrid_best_score_self'):.2f}%)")


print(f"\n{'='*60}")
print(f"✅ Detailed results saved to: {output_path}")
print(f"{'='*60}\n")

