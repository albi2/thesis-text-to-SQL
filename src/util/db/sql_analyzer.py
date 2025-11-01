import sqlite3
import re
from typing import Dict, Tuple
from sqlalchemy.engine import Engine, CursorResult
from sqlalchemy import text

def calculate_sql_cost(sql: str, engine: Engine ) -> int:
    """
    Analyzes SQL query complexity and estimates cost for SQLite.
    
    Args:
        sql: SQL query string to analyze
        db_path: Path to SQLite database (default: in-memory)
    
    Returns:
        Dictionary containing cost metrics and analysis
    """
    cost = 0
    details = {}
    
    # Normalize SQL for analysis
    sql_upper = sql.upper().strip()
    
    # 1. Query type costs
    if 'SELECT' in sql_upper:
        cost += 10
        details['query_type'] = 'SELECT'
    if 'INSERT' in sql_upper:
        cost += 15
        details['query_type'] = 'INSERT'
    if 'UPDATE' in sql_upper:
        cost += 20
        details['query_type'] = 'UPDATE'
    if 'DELETE' in sql_upper:
        cost += 20
        details['query_type'] = 'DELETE'
    
    # 2. JOIN complexity
    join_count = len(re.findall(r'\bJOIN\b', sql_upper))
    cost += join_count * 25
    details['joins'] = join_count
    
    # 3. Subquery complexity
    subquery_count = sql.count('(SELECT') + sql.count('( SELECT')
    cost += subquery_count * 30
    details['subqueries'] = subquery_count
    
    # 4. Aggregate functions
    aggregates = len(re.findall(r'\b(COUNT|SUM|AVG|MIN|MAX|GROUP_CONCAT)\b', sql_upper))
    cost += aggregates * 15
    details['aggregates'] = aggregates
    
    # 5. GROUP BY complexity
    if 'GROUP BY' in sql_upper:
        cost += 20
        details['has_group_by'] = True
    
    # 6. ORDER BY complexity
    if 'ORDER BY' in sql_upper:
        cost += 15
        details['has_order_by'] = True
    
    # 7. DISTINCT operation
    if 'DISTINCT' in sql_upper:
        cost += 20
        details['has_distinct'] = True
    
    # 8. Window functions
    window_funcs = len(re.findall(r'\bOVER\s*\(', sql_upper))
    cost += window_funcs * 35
    details['window_functions'] = window_funcs
    
    # 9. UNION operations
    union_count = len(re.findall(r'\bUNION\b', sql_upper))
    cost += union_count * 30
    details['unions'] = union_count
    
    # 10. CTEs (Common Table Expressions)
    cte_count = len(re.findall(r'\bWITH\b', sql_upper))
    cost += cte_count * 25
    details['ctes'] = cte_count
    
    # 11. Get SQLite query plan if database connection available
    try:
        with engine.connect() as conn:
            # Run EXPLAIN QUERY PLAN
            explain_sql = f"EXPLAIN QUERY PLAN {sql}"
            result = conn.execute(text(explain_sql))
            plan = result.fetchall()

            details['query_plan'] = plan

            # Analyze query plan for table scans (expensive)
            plan_str = str(plan).upper()
            table_scans = plan_str.count('SCAN TABLE')
            cost += table_scans * 40
            details['table_scans'] = table_scans

            # Index usage (good, reduces cost)
            index_usage = plan_str.count('USING INDEX') + plan_str.count('USING COVERING INDEX')
            cost -= index_usage * 10
            details['index_usage'] = index_usage

    except sqlite3.Error as e:
        details['query_plan_error'] = str(e)
    except Exception as e:
        details['analysis_note'] = f"Could not analyze query plan: {str(e)}"
    
    # Ensure cost is non-negative
    return max(0, cost)
    
    # # Determine complexity level
    # if cost < 50:
    #     complexity = 'Low'
    # elif cost < 150:
    #     complexity = 'Medium'
    # elif cost < 300:
    #     complexity = 'High'
    # else:
    #     complexity = 'Very High'
        
# def explain_query_plan(sql: str, engine: Engine) -> Dict[str, Any]:
#     """
#     Retrieves the SQLite query plan and explains it in natural language.

#     Args:
#         sql: SQL query string to analyze.
#         engine: SQLAlchemy engine connected to a SQLite database.

#     Returns:
#         Dictionary containing raw plan, individual step explanations, and narrative.
#     """
#     result: Dict[str, Any] = {
#         'raw_plan': [],
#         'step_explanations': [],
#         'narrative': '',
#         'performance_notes': [],
#     }

#     try:
#         # Use SQLAlchemy connection context
#         with engine.connect() as conn:
#             # Execute EXPLAIN QUERY PLAN safely
#             explain_sql = f"EXPLAIN QUERY PLAN {sql}"
#             result_proxy = conn.execute(text(explain_sql))
#             plan = result_proxy.fetchall()
#             result['raw_plan'] = plan

#             # Parse SQL to extract additional context (custom helper)
#             sql_context = _extract_sql_context(sql)

#             step_descriptions: List[str] = []
#             for step in plan:
#                 # Typical structure: (id, parent, notused, detail)
#                 if len(step) == 4:
#                     step_id, parent, _, detail = step
#                 else:
#                     step_id, detail = 0, str(step)

#                 explanation = _parse_plan_step(detail, step_id, sql_context)
#                 result['step_explanations'].append(explanation)

#                 desc = _parse_plan_step_narrative(detail, sql_context)
#                 step_descriptions.append(desc)

#                 perf_note = _get_performance_note(detail)
#                 if perf_note:
#                     result['performance_notes'].append(perf_note)

#             # Combine into readable narrative
#             result['narrative'] = _create_narrative(
#                 step_descriptions,
#                 result['performance_notes'],
#                 sql_context
#             )

#     except Exception as e:
#         result['error'] = f"Error: {e}"
#         result['narrative'] = (
#             f"Could not analyze the query plan. "
#             f"Ensure the query is valid and the engine points to a SQLite database. Error: {e}"
#         )

#     return result


# def _extract_sql_context(sql: str) -> Dict:
#     """Extract important context from the SQL query itself."""
#     context = {
#         'where_clause': None,
#         'order_by': None,
#         'group_by': None,
#         'join_conditions': [],
#         'select_columns': None,
#         'having_clause': None,
#         'limit': None
#     }
    
#     sql_upper = sql.upper()
    
#     # Extract WHERE clause
#     where_match = re.search(r'WHERE\s+(.+?)(?:\s+GROUP BY|\s+ORDER BY|\s+HAVING|\s+LIMIT|\s*$)', sql, re.IGNORECASE | re.DOTALL)
#     if where_match:
#         context['where_clause'] = where_match.group(1).strip()
    
#     # Extract ORDER BY
#     order_match = re.search(r'ORDER BY\s+(.+?)(?:\s+LIMIT|\s*$)', sql, re.IGNORECASE | re.DOTALL)
#     if order_match:
#         context['order_by'] = order_match.group(1).strip()
    
#     # Extract GROUP BY
#     group_match = re.search(r'GROUP BY\s+(.+?)(?:\s+HAVING|\s+ORDER BY|\s+LIMIT|\s*$)', sql, re.IGNORECASE | re.DOTALL)
#     if group_match:
#         context['group_by'] = group_match.group(1).strip()
    
#     # Extract HAVING
#     having_match = re.search(r'HAVING\s+(.+?)(?:\s+ORDER BY|\s+LIMIT|\s*$)', sql, re.IGNORECASE | re.DOTALL)
#     if having_match:
#         context['having_clause'] = having_match.group(1).strip()
    
#     # Extract LIMIT
#     limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
#     if limit_match:
#         context['limit'] = limit_match.group(1)
    
#     # Extract JOIN conditions
#     join_matches = re.finditer(r'JOIN\s+(\w+)(?:\s+AS\s+(\w+))?\s+ON\s+(.+?)(?:\s+(?:LEFT|RIGHT|INNER|OUTER|CROSS|JOIN|WHERE|GROUP|ORDER|HAVING|LIMIT)|\s*$)', sql, re.IGNORECASE | re.DOTALL)
#     for match in join_matches:
#         table = match.group(1)
#         alias = match.group(2) if match.group(2) else table
#         condition = match.group(3).strip()
#         context['join_conditions'].append({'table': table, 'alias': alias, 'condition': condition})
    
#     # Extract SELECT columns (simplified)
#     select_match = re.search(r'SELECT\s+(.+?)\s+FROM', sql, re.IGNORECASE | re.DOTALL)
#     if select_match:
#         context['select_columns'] = select_match.group(1).strip()
    
#     return context


# def _parse_plan_step_narrative(detail: str) -> str:
#     """Parse a single query plan step into narrative form (without step numbering)."""
#     detail_upper = detail.upper()
    
#     # Scan operations
#     if 'SCAN TABLE' in detail_upper:
#         table_match = re.search(r'SCAN TABLE (\w+)', detail_upper)
#         table_name = table_match.group(1) if table_match else "unknown table"
        
#         if 'USING INDEX' in detail_upper:
#             index_match = re.search(r'USING INDEX (\w+)', detail_upper)
#             index_name = index_match.group(1) if index_match else "an index"
#             return f"scans the '{table_name}' table using the '{index_name}' index"
#         else:
#             return f"performs a full table scan on '{table_name}'"
    
#     # Search operations (index lookups)
#     if 'SEARCH TABLE' in detail_upper or 'SEARCH' in detail_upper:
#         table_match = re.search(r'(?:SEARCH )?TABLE (\w+)', detail_upper)
#         table_name = table_match.group(1) if table_match else "unknown table"
        
#         if 'USING INDEX' in detail_upper:
#             index_match = re.search(r'USING INDEX (\w+)', detail_upper)
#             index_name = index_match.group(1) if index_match else "an index"
            
#             if 'COVERING' in detail_upper:
#                 return f"efficiently searches '{table_name}' using covering index '{index_name}'"
#             else:
#                 return f"searches '{table_name}' using index '{index_name}'"
#         elif 'PRIMARY KEY' in detail_upper:
#             return f"looks up rows in '{table_name}' by primary key"
#         else:
#             return f"searches '{table_name}' without using an index"
    
#     # Temporary B-tree for sorting/grouping
#     if 'USE TEMP B-TREE' in detail_upper:
#         if 'ORDER BY' in detail_upper:
#             return "creates a temporary structure to sort the results"
#         elif 'GROUP BY' in detail_upper:
#             return "creates a temporary structure to group the data"
#         else:
#             return "creates a temporary structure for intermediate processing"
    
#     # Subquery execution
#     if 'EXECUTE SCALAR SUBQUERY' in detail_upper or 'EXECUTE CORRELATED SCALAR SUBQUERY' in detail_upper:
#         if 'CORRELATED' in detail_upper:
#             return "executes a correlated subquery for each row"
#         else:
#             return "executes a scalar subquery once"
    
#     if 'EXECUTE LIST SUBQUERY' in detail_upper:
#         return "executes a subquery to retrieve a list of values"
    
#     # Materialization
#     if 'MATERIALIZE' in detail_upper:
#         return "materializes a subquery or CTE by computing and storing its results"
    
#     # Co-routine
#     if 'CO-ROUTINE' in detail_upper:
#         return "sets up a co-routine for CTE processing"
    
#     # Compound query (UNION, etc.)
#     if 'COMPOUND QUERY' in detail_upper:
#         return "combines results using a compound operation (UNION/INTERSECT/EXCEPT)"
    
#     # Bloom filter
#     if 'BLOOM FILTER' in detail_upper:
#         return "uses a Bloom filter to quickly eliminate non-matching rows"
    
#     # Automatic index
#     if 'AUTOMATIC' in detail_upper and 'INDEX' in detail_upper:
#         return "creates an automatic temporary index"
    
#     # Default case - return simplified version
#     return detail.lower()


# def _create_narrative(step_descriptions: list, performance_notes: list) -> str:
#     """Create a cohesive narrative from individual step descriptions."""
#     if not step_descriptions:
#         return "No query plan available."
    
#     # Start the narrative
#     narrative_parts = []
    
#     if len(step_descriptions) == 1:
#         narrative_parts.append(f"This query {step_descriptions[0]}.")
#     else:
#         # Build a flowing narrative
#         narrative_parts.append(f"This query execution works as follows: First, it {step_descriptions[0]}")
        
#         # Add middle steps
#         for i in range(1, len(step_descriptions) - 1):
#             narrative_parts.append(f", then {step_descriptions[i]}")
        
#         # Add final step
#         if len(step_descriptions) > 1:
#             narrative_parts.append(f", and finally {step_descriptions[-1]}")
        
#         narrative_parts.append(".")
    
#     narrative = ''.join(narrative_parts)
    
#     # Add performance assessment
#     if performance_notes:
#         critical_issues = [n for n in performance_notes if '⚠️' in n]
#         positive_notes = [n for n in performance_notes if '✅' in n]
        
#         if critical_issues:
#             narrative += "\n\n⚠️ Performance concerns: "
#             concerns = []
#             if any('full table scan' in n.lower() for n in critical_issues):
#                 concerns.append("full table scans detected which may be slow on large tables")
#             if any('correlated' in n.lower() for n in critical_issues):
#                 concerns.append("correlated subqueries that execute repeatedly")
#             if any('temporary index' in n.lower() for n in performance_notes):
#                 concerns.append("temporary indexes being created on-the-fly")
            
#             narrative += ", ".join(concerns) + "."
        
#         if positive_notes:
#             narrative += "\n\n✅ Good practices: "
#             positives = []
#             if any('covering index' in n.lower() for n in positive_notes):
#                 positives.append("covering indexes are being used for optimal performance")
#             if positives:
#                 narrative += ", ".join(positives) + "."
        
#         # General optimization suggestions
#         if not positive_notes and critical_issues:
#             narrative += " Consider adding appropriate indexes to improve query performance."
    
#     return narrative

# def _parse_plan_step(detail: str, step_id: int) -> str:
#     """Parse a single query plan step into natural language."""
#     detail_upper = detail.upper()
    
#     # Scan operations
#     if 'SCAN TABLE' in detail_upper:
#         table_match = re.search(r'SCAN TABLE (\w+)', detail_upper)
#         table_name = table_match.group(1) if table_match else "unknown table"
        
#         if 'USING INDEX' in detail_upper:
#             index_match = re.search(r'USING INDEX (\w+)', detail_upper)
#             index_name = index_match.group(1) if index_match else "an index"
#             return f"Step {step_id}: Scanning table '{table_name}' using index '{index_name}' to efficiently locate rows."
#         else:
#             return f"Step {step_id}: Performing a FULL TABLE SCAN on '{table_name}' (checking every row - this can be slow for large tables)."
    
#     # Search operations (index lookups)
#     if 'SEARCH TABLE' in detail_upper or 'SEARCH' in detail_upper:
#         table_match = re.search(r'(?:SEARCH )?TABLE (\w+)', detail_upper)
#         table_name = table_match.group(1) if table_match else "unknown table"
        
#         if 'USING INDEX' in detail_upper:
#             index_match = re.search(r'USING INDEX (\w+)', detail_upper)
#             index_name = index_match.group(1) if index_match else "an index"
            
#             if 'COVERING' in detail_upper:
#                 return f"Step {step_id}: Efficiently searching table '{table_name}' using covering index '{index_name}' (all needed columns are in the index - very fast!)."
#             else:
#                 return f"Step {step_id}: Searching table '{table_name}' using index '{index_name}' to quickly find matching rows."
#         elif 'PRIMARY KEY' in detail_upper:
#             return f"Step {step_id}: Looking up rows in '{table_name}' by primary key (fastest possible lookup)."
#         else:
#             return f"Step {step_id}: Searching table '{table_name}' without an index (may be slow)."
    
#     # Temporary B-tree for sorting/grouping
#     if 'USE TEMP B-TREE' in detail_upper:
#         if 'ORDER BY' in detail_upper:
#             return f"Step {step_id}: Creating a temporary sorted structure for ORDER BY (requires extra memory and processing)."
#         elif 'GROUP BY' in detail_upper:
#             return f"Step {step_id}: Creating a temporary structure for GROUP BY operation (requires extra memory)."
#         else:
#             return f"Step {step_id}: Creating a temporary data structure for intermediate processing."
    
#     # Subquery execution
#     if 'EXECUTE SCALAR SUBQUERY' in detail_upper or 'EXECUTE CORRELATED SCALAR SUBQUERY' in detail_upper:
#         if 'CORRELATED' in detail_upper:
#             return f"Step {step_id}: Executing a correlated subquery (runs once for each row in outer query - can be expensive)."
#         else:
#             return f"Step {step_id}: Executing a scalar subquery (runs once and returns a single value)."
    
#     if 'EXECUTE LIST SUBQUERY' in detail_upper:
#         return f"Step {step_id}: Executing a subquery that returns a list of values (e.g., for IN clause)."
    
#     # Materialization
#     if 'MATERIALIZE' in detail_upper:
#         return f"Step {step_id}: Materializing a subquery or CTE (computing and storing results temporarily for reuse)."
    
#     # Co-routine
#     if 'CO-ROUTINE' in detail_upper:
#         return f"Step {step_id}: Setting up a co-routine for CTE (Common Table Expression) processing."
    
#     # Compound query (UNION, etc.)
#     if 'COMPOUND QUERY' in detail_upper:
#         return f"Step {step_id}: Processing a compound query (UNION, INTERSECT, or EXCEPT operation)."
    
#     # Bloom filter
#     if 'BLOOM FILTER' in detail_upper:
#         return f"Step {step_id}: Using a Bloom filter to quickly eliminate non-matching rows before JOIN."
    
#     # Automatic index
#     if 'AUTOMATIC' in detail_upper and 'INDEX' in detail_upper:
#         return f"Step {step_id}: Creating an automatic temporary index to speed up this query."
    
#     # Default case
#     return f"Step {step_id}: {detail}"


# def _get_performance_note(detail: str) -> str:
#     """Generate performance notes for specific plan operations."""
#     detail_upper = detail.upper()
    
#     if 'SCAN TABLE' in detail_upper and 'USING INDEX' not in detail_upper:
#         return "⚠️ Full table scan detected - consider adding an index for better performance."
    
#     if 'USE TEMP B-TREE' in detail_upper:
#         return "ℹ️ Temporary structure created - this uses extra memory and processing time."
    
#     if 'CORRELATED' in detail_upper:
#         return "⚠️ Correlated subquery - executes once per outer row, which can be slow for large datasets."
    
#     if 'AUTOMATIC' in detail_upper and 'INDEX' in detail_upper:
#         return "💡 SQLite is creating a temporary index - consider making this a permanent index."
    
#     if 'COVERING INDEX' in detail_upper:
#         return "✅ Using covering index - excellent! All needed data is in the index."
    
#     return None


# def _parse_plan_step(detail: str, step_id: int) -> str:
# if __name__ == "__main__":
#     # Simple query
#     simple_sql = "SELECT * FROM users WHERE id = 1"
#     result = calculate_sql_cost(simple_sql)
#     print(f"Simple Query Cost: {result['cost']} ({result['complexity']})")
#     print(f"Details: {result['details']}\n")
    
#     # Complex query
#     complex_sql = """
#     WITH user_stats AS (
#         SELECT user_id, COUNT(*) as order_count
#         FROM orders
#         GROUP BY user_id
#     )
#     SELECT DISTINCT u.name, u.email, s.order_count
#     FROM users u
#     JOIN user_stats s ON u.id = s.user_id
#     JOIN addresses a ON u.id = a.user_id
#     WHERE u.created_at > '2023-01-01'
#     ORDER BY s.order_count DESC
#     """
#     result = calculate_sql_cost(complex_sql)
#     print(f"Complex Query Cost: {result['cost']} ({result['complexity']})")
#     print(f"Details: {result['details']}")
#     print(f"Recommendations: {result['recommendations']}\n")
    
#     # Explain query plan
#     print("=" * 60)
#     print("QUERY PLAN EXPLANATION")
#     print("=" * 60)
#     plan_result = explain_query_plan(complex_sql)
#     print(f"\n{plan_result['narrative']}")
    
#     if plan_result.get('step_explanations'):
#         print("\n" + "-" * 60)
#         print("Detailed step-by-step breakdown:")
#         print("-" * 60)
#         for explanation in plan_result['step_explanations']:
#             print(f"  • {explanation}")