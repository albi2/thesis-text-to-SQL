import sqlglot
from sqlglot import exp, parse, transforms
from typing import List, Dict, Optional, Tuple, Set

# Note: sqlite3 is used for type hinting, assuming 'engine' is a Connection
import sqlite3 

class SQLOptimizer:
    """
    Post-process SQL queries to fix common issues using sqlglot,
    focusing on DISTINCT and NULL handling.
    """
    
    def __init__(self, db_manager):
        """
        Initialize with database manager to access schema information.
        
        Args:
            db_manager: DatabaseManager instance for schema access
        """
        self.db_manager = db_manager
        self._schema_cache = {}  # Caches {db_id.table: set(pk_cols)}
        self._foreign_key_cache = {} # Caches {db_id.table: list(fk_dicts)}
        self._column_type_cache = {} # Caches {db_id.table: {col: type_str}}

    # --- Schema and Helper Methods (Kept for checks) ---

    def _get_table_schema(self, db_id: str, table_name: str, engine) -> None:
        """
        Internal helper to populate schema and column type caches
        using a single PRAGMA query.
        """
        cache_key = f"{db_id}.{table_name}"
        if cache_key in self._schema_cache:
            return  # Already populated

        try:
            result = list(engine.execute(f"PRAGMA table_info('{table_name}')"))
            pk_cols = {row[1].lower() for row in result if row[5] > 0}
            col_types = {row[1].lower(): row[2].upper() for row in result}
            
            self._schema_cache[cache_key] = pk_cols
            self._column_type_cache[cache_key] = col_types
        except Exception:
            self._schema_cache[cache_key] = set()
            self._column_type_cache[cache_key] = {}

    def get_primary_keys(self, db_id: str, table_name: str, engine) -> Set[str]:
        """Get primary key columns for a table from cache or SQLite."""
        cache_key = f"{db_id}.{table_name}"
        if cache_key not in self._schema_cache:
            self._get_table_schema(db_id, table_name, engine)
        return self._schema_cache[cache_key]
    
    def get_table_columns_and_types(self, db_id: str, table_name: str, engine) -> Dict[str, str]:
        """Get {column: type} mapping for a table from cache or SQLite."""
        cache_key = f"{db_id}.{table_name}"
        if cache_key not in self._column_type_cache:
            self._get_table_schema(db_id, table_name, engine)
        return self._column_type_cache[cache_key]

    def get_foreign_keys(self, db_id: str, table_name: str, engine) -> List[Dict]:
        """Get foreign key information for a table from SQLite."""
        cache_key = f"{db_id}.{table_name}"
        if cache_key in self._foreign_key_cache:
            return self._foreign_key_cache[cache_key]
        
        try:
            result = engine.execute(f"PRAGMA foreign_key_list('{table_name}')")
            fks = []
            for row in result:
                fks.append({
                    'from_col': row[3].lower(),
                    'to_table': row[2].lower(),
                    'to_col': row[4].lower() if row[4] else None
                })
            self._foreign_key_cache[cache_key] = fks
            return fks
        except Exception:
            self._foreign_key_cache[cache_key] = []
            return []
    
    def is_n_side_of_relationship(self, table: str, db_id: str, engine) -> bool:
        """Check if a table is on the N-side of a 1-N or N-N relationship."""
        if not table:
            return False
        fks = self.get_foreign_keys(db_id, table, engine)
        return len(fks) > 0

    def get_main_table_from_query(self, parsed_query) -> Optional[str]:
        """Extract the main FROM table from a parsed query (actual table name, not alias)."""
        try:
            from_clause = parsed_query.find(exp.From)
            if from_clause:
                table_expr = from_clause.this
                if isinstance(table_expr, exp.Table):
                    return table_expr.name.lower()
                if isinstance(table_expr, exp.Alias) and isinstance(table_expr.this, exp.Table):
                    return table_expr.this.name.lower()
        except Exception:
            pass
        return None

    @staticmethod
    def get_table_aliases(parsed_query: exp.Expression) -> Dict[str, str]:
        """Get mapping of table aliases to actual table names."""
        cte_map = {}
        
        if isinstance(parsed_query, exp.Select) and parsed_query.expressions:
            for cte in parsed_query.find_all(exp.CTE):
                cte_name = cte.alias.lower()
                sub_tables = list(cte.this.find_all(exp.Table))
                cte_map[cte_name] = sub_tables[0].name.lower() if len(sub_tables) == 1 else "(complex_cte)"

        alias_map = {}
        for table_source in parsed_query.find_all(exp.From, exp.Join):
            node = table_source.this
            table_name, alias = None, None

            if isinstance(node, exp.Alias):
                alias = node.alias.lower()
                if isinstance(node.this, exp.Table):
                    table_name = node.this.name.lower()
                elif isinstance(node.this, exp.Subquery):
                    sub_tables = list(node.this.find_all(exp.Table))
                    table_name = sub_tables[0].name.lower() if len(sub_tables) == 1 else "(complex_subquery)"
            elif isinstance(node, exp.Table):
                table_name = node.name.lower()
                alias = table_name

            if table_name and table_name in cte_map:
                table_name = cte_map[table_name]
            if alias and table_name:
                alias_map[alias] = table_name
                
        return alias_map
    
    def get_selected_tables(self, parsed_query) -> Set[str]:
        """Get all actual table names (not aliases) referenced in SELECT columns."""
        tables = set()
        alias_map = self.get_table_aliases(parsed_query)
        
        try:
            for select_expr in parsed_query.find_all(exp.Select):
                for projection in select_expr.expressions:
                    col = None
                    if isinstance(projection, exp.Column):
                        col = projection
                    elif isinstance(projection, exp.Alias) and isinstance(projection.this, exp.Column):
                        col = projection.this
                    
                    if col and hasattr(col, 'table') and col.table:
                        alias_or_table = col.table.lower()
                        actual_table = alias_map.get(alias_or_table, alias_or_table)
                        tables.add(actual_table)
        except Exception:
            pass
        return tables
    
    # --- 1. Ambiguous Column Check (Linter) ---

    def check_ambiguous_columns(self, sql: str, db_id: str, engine) -> List[str]:
        """
        LINT: Check for unqualified columns that exist in multiple tables.
        Returns a list of warning strings.
        """
        warnings = []
        try:
            parsed_query = sqlglot.parse_one(sql, read='sqlite')
            alias_map = self.get_table_aliases(parsed_query)
            if len(alias_map) <= 1:
                return []  # No ambiguity possible with one table

            # Build a map of {col_name: set(table_names)}
            col_to_tables_map = {}
            for alias, table_name in alias_map.items():
                if table_name.startswith("("): continue  # Skip subqueries
                
                columns = self.get_table_columns_and_types(db_id, table_name, engine).keys()
                for col in columns:
                    col_to_tables_map.setdefault(col, set()).add(table_name)
            
            # Find all unqualified columns (col.table is None)
            for col in parsed_query.find_all(exp.Column):
                if col.table is None:
                    col_name = col.name.lower()
                    if col_name in col_to_tables_map and len(col_to_tables_map[col_name]) > 1:
                        tables = col_to_tables_map[col_name]
                        warnings.append(
                            f"Ambiguous column: '{col_name}' exists in multiple tables: {tables}"
                        )
            
            return list(set(warnings)) # Return unique warnings
        except Exception as e:
            return [f"Error during ambiguity check: {e}"]

    # --- 2. NULLS LAST Check (Auto-Fix) ---

    @staticmethod
    def needs_nulls_last(sql: str) -> bool:
        """Check if query has ORDER BY ASC but doesn't have NULLS LAST."""
        try:
            parsed = sqlglot.parse_one(sql, read='sqlite')
            for order in parsed.find_all(exp.Order):
                is_asc = not order.args.get('desc', False)
                if is_asc:
                    sql_str = order.sql(dialect='sqlite').upper()
                    if 'NULLS LAST' not in sql_str:
                        return True
            return False
        except Exception:
            return False

    # @staticmethod
    # def add_nulls_last(sql: str) -> Optional[str]:
    #     """Add NULLS LAST to ORDER BY ASC clauses for SQLite."""
    #     import re
        
    #     try:
    #         parsed = sqlglot.parse_one(sql, read='sqlite')
            
    #         # Collect columns that need NULLS LAST with their full SQL representation
    #         columns_to_modify = []
            
    #         modified = False
    #         for order_by in parsed.find_all(exp.Order):
    #             for order_expr in order_by.expressions:
    #                 is_asc = not order_expr.args.get("desc", False)
    #                 has_nulls = order_expr.args.get("nulls_last") is not None
                    
    #                 if is_asc and not has_nulls:
    #                     # Get the exact SQL representation of this column
    #                     column_sql = order_expr.this.sql(dialect='sqlite')
    #                     columns_to_modify.append(column_sql)
    #                     order_expr.set("nulls_last", True)
    #                     modified = True
            
    #         if modified:
    #             output_sql = parsed.sql(dialect='sqlite', pretty=True)
                
    #             # For each column, add NULLS LAST using exact string matching
    #             for column in columns_to_modify:
    #                 # Escape special regex characters in the column name
    #                 escaped_column = re.escape(column)
                    
    #                 # Pattern: column followed by ASC (or nothing, then comma/end)
    #                 # Replace "column ASC" with "column ASC NULLS LAST"
    #                 pattern = rf'{escaped_column}\s+ASC\b(?!\s+NULLS)'
    #                 output_sql = re.sub(pattern, f'{column} ASC NULLS LAST', output_sql, count=1)
                    
    #                 # If no explicit ASC, handle implicit ASC
    #                 # Pattern: column followed by comma, newline, LIMIT, or end of ORDER BY
    #                 if f'{column} ASC NULLS LAST' not in output_sql:
    #                     pattern = rf'{escaped_column}(?=\s*(?:,|\n|$|LIMIT|OFFSET))'
    #                     output_sql = re.sub(pattern, f'{column} NULLS LAST', output_sql, count=1)
                
    #             print(f"ORIGINAL SQL: {sql}")
    #             print(f"MODIFIED SQL: {output_sql}")
    #             return output_sql
            
    #         return None
            
    #     except Exception as e:
    #         print(f"Error parsing SQL: {e}")
    #         return None



    @staticmethod
    def add_nulls_last(sql: str) -> Optional[str]:
        """
        Add WHERE conditions to exclude NULLs from *all columns* found in
        ORDER BY ASC expressions for SQLite, *ignoring columns inside CAST*.
        
        This version correctly handles nested queries by applying WHERE
        clauses to the specific SELECT statement that owns the ORDER BY.
        """
        
        def has_cast_ancestor(node: exp.Expression) -> bool:
            """
            Manually walks up the expression tree to check if the node
            has a CAST expression as one of its parents.
            """
            current = node.parent
            while current:
                if isinstance(current, exp.Cast):
                    return True
                current = current.parent
            return False

        try:
            parsed = sqlglot.parse_one(sql, read='sqlite')
            
            # Track if any modifications are made
            made_changes = False

            # Find all SELECT statements (including subqueries)
            for select_node in parsed.find_all(exp.Select):
                
                # Get the ORDER BY clause for *this* SELECT statement
                order_by = select_node.args.get("order")
                
                if not order_by:
                    # This SELECT does not have an ORDER BY, skip it
                    continue
                    
                # Use a dict to store unique col expressions *for this SELECT*
                unique_columns = {} 

                for order_expr in order_by.expressions:
                    # Check if ASC (default)
                    is_asc = not order_expr.args.get("desc", False)
                    
                    # Check if NULLS handling is already specified (both LAST and FIRST)
                    has_nulls = order_expr.args.get("nulls_last") is not None 
                    
                    if is_asc and not has_nulls:
                        expression_to_check = order_expr.this
                        columns_in_expr = expression_to_check.find_all(exp.Column)
                        
                        for col in columns_in_expr:
                            if not has_cast_ancestor(col):
                                col_sql = col.sql() 
                                if col_sql not in unique_columns:
                                    unique_columns[col_sql] = col.copy()
                
                if not unique_columns:
                    # No applicable columns for this ORDER BY, skip it
                    continue
                
                # If we're here, we found columns to add
                made_changes = True
                
                # Build "IS NOT NULL" conditions
                new_conditions = [
                    exp.Is(this=col_expr, expression=exp.Not(this=exp.Null()))
                    for col_expr in unique_columns.values()
                ]
                
                # Combine all new conditions with AND
                final_new_condition = new_conditions[0]
                for cond in new_conditions[1:]:
                    final_new_condition = exp.And(this=final_new_condition, expression=cond)
                    
                # Find existing WHERE clause *on this specific select_node*
                where = select_node.args.get("where")
                
                if where:
                    # If WHERE exists, AND the new condition to it
                    existing_condition = where.this
                    combined_condition = exp.And(this=existing_condition, expression=final_new_condition)
                    where.set("this", combined_condition)
                else:
                    # Otherwise, add a new WHERE clause *to this select_node*
                    select_node.where(final_new_condition, copy=False)
            
            # After checking all SELECT nodes, see if we did anything
            if not made_changes:
                return None
                
            modified_sql = parsed.sql(dialect='sqlite', pretty=True)
            
            print(f"ORIGINAL SQL: {sql}")
            print(f"MODIFIED SQL: {modified_sql}")
            return modified_sql
            
        except Exception as e:
            print(f"Error parsing SQL: {e}")
            return None
    # --- 3. MIN() NULL Check (Auto-Fix) ---

    @staticmethod
    def needs_min_null_check(sql: str) -> bool:
        """
        Checks if a query uses MIN(column) without a 
        corresponding 'WHERE column IS NOT NULL'.
        """
        try:
            parsed = sqlglot.parse_one(sql, read='sqlite')
            
            for min_func in parsed.find_all(exp.Min):
                # Get the column inside MIN()
                min_col = min_func.this
                if not isinstance(min_col, exp.Column):
                    continue # Skip MIN(literal), MIN(expression), etc.
                
                min_col_name = min_col.name.lower()
                
                # Find the WHERE clause for this MIN's SELECT
                select = min_func.find_ancestor(exp.Select)
                if not select:
                    continue
                
                where = select.args.get('where')
                if not where:
                    return True  # Has MIN() but no WHERE clause at all

                # Check if 'col IS NOT NULL' already exists in WHERE
                has_null_check = False
                for is_not_null in where.find_all(exp.IsNotNull):
                    check_col = is_not_null.this
                    if isinstance(check_col, exp.Column) and check_col.name.lower() == min_col_name:
                        has_null_check = True
                        break
                
                if not has_null_check:
                    return True # MIN(col) found, but 'col IS NOT NULL' is missing
            
            return False
        except Exception:
            return False

    @staticmethod
    def add_min_null_check(sql: str) -> Optional[str]:
        """
        Adds 'column IS NOT NULL' to the WHERE clause for any
        column wrapped in MIN().
        """
        try:
            parsed = sqlglot.parse_one(sql, read='sqlite')
            modified = False
            
            # Use set to avoid adding the same check multiple times
            checks_to_add = {} # {select_node: set(col_name)}
            
            for min_func in parsed.find_all(exp.Min):
                min_col = min_func.this
                if not isinstance(min_col, exp.Column):
                    continue
                
                min_col_name = min_col.name.lower()
                select = min_func.find_ancestor(exp.Select)
                if not select:
                    continue
                
                # Check if the check is already present
                where = select.args.get('where')
                has_null_check = False
                if where:
                    for is_not_null in where.find_all(exp.IsNotNull):
                        check_col = is_not_null.this
                        if isinstance(check_col, exp.Column) and check_col.name.lower() == min_col_name:
                            has_null_check = True
                            break
                
                if not has_null_check:
                    checks_to_add.setdefault(select, set()).add(min_col_name)
                    modified = True
            
            if not modified:
                return None
            
            # Apply the missing checks
            for select, col_names in checks_to_add.items():
                for col_name in col_names:
                    # Create the 'col IS NOT NULL' expression
                    filter_expr = exp.IsNotNull(this=exp.Column(this=exp.Identifier(this=col_name)))
                    # Add it to the WHERE clause (handles ANDing)
                    select.where(filter_expr, copy=False)

            return parsed.sql(dialect='sqlite')
        except Exception:
            return None

    # --- 4. DISTINCT Check (Auto-Fix) ---
    
    def needs_distinct(self, sql: str, db_id: str, engine) -> bool:
        """
        Check if query needs DISTINCT based on JOINs and N-side relationships.
        (Logic from your provided code, kept as-is)
        """
        try:
            parsed = sqlglot.parse_one(sql, read='sqlite')
            outermost_select = parsed if isinstance(parsed, exp.Select) else parsed.find(exp.Select)
            if not outermost_select:
                return False
            
            if outermost_select.args.get('distinct'):
                return False
            
            has_top_level_join = False
            for join in parsed.find_all(exp.Join):
                if join.find_ancestor(exp.Select) == outermost_select:
                    has_top_level_join = True
                    break
            
            if not has_top_level_join:
                return False
            
            if outermost_select.args.get('group'):
                return False
            
            main_table = self.get_main_table_from_query(parsed)
            selected_tables = self.get_selected_tables(outermost_select)
            
            tables_to_check = selected_tables if selected_tables else {main_table} if main_table else set()
            
            for table in tables_to_check:
                if table and self.is_n_side_of_relationship(table, db_id, engine):
                    pk_cols = self.get_primary_keys(db_id, table, engine)
                    alias_map = self.get_table_aliases(parsed)
                    
                    for projection in outermost_select.expressions:
                        col_name, col_table, is_aggregate = None, None, False
                        
                        if isinstance(projection, exp.Alias):
                            inner = projection.this
                            if isinstance(inner, (exp.Count, exp.Sum, exp.Avg, exp.Max, exp.Min)):
                                is_aggregate = True
                            elif isinstance(inner, exp.Column):
                                col_name = inner.name.lower()
                                col_table = inner.table.lower() if hasattr(inner, 'table') and inner.table else None
                        elif isinstance(projection, (exp.Count, exp.Sum, exp.Avg, exp.Max, exp.Min)):
                            is_aggregate = True
                        elif isinstance(projection, exp.Column):
                            col_name = projection.name.lower()
                            col_table = projection.table.lower() if hasattr(projection, 'table') and projection.table else None
                        
                        if is_aggregate or col_name == '*':
                            continue
                        
                        if col_table:
                            col_table = alias_map.get(col_table, col_table)
                        
                        if col_table == table or (not col_table and table == main_table):
                            if col_name and col_name not in pk_cols:
                                return True
            return False
        except Exception:
            return False

    @staticmethod
    def add_distinct(sql: str) -> Optional[str]:
        """Add DISTINCT to the outermost SELECT clause."""
        try:
            parsed = sqlglot.parse_one(sql, read='sqlite')
            
            select = parsed if isinstance(parsed, exp.Select) else parsed.find(exp.Select)
            if select and not select.args.get('distinct'):
                select.set('distinct', True)
                return parsed.sql(dialect='sqlite')
            
            return None
        except Exception:
            return None

    # --- Main Auto-Fixer Method ---

    def find_better_alternative(
        self,
        chosen_sql: str,
        all_queries: List[Dict],
        db_id: str,
        cache,
        gold_sql: str,
        db_path: str,
        engine
    ) -> Optional[Tuple[str, str, float]]:
        """
        Finds a better query or modifies the chosen_sql to fix common errors.
        Returns (better_sql, reason, score) or None.
        """
        if not chosen_sql or not all_queries:
            return None
        
        # Check for all auto-fixable errors
        needs_nl = self.needs_nulls_last(chosen_sql)
        needs_d = self.needs_distinct(chosen_sql, db_id, engine)
        needs_min_null = self.needs_min_null_check(chosen_sql)
        
        if not any([needs_nl, needs_d, needs_min_null]):
            return None  # Current query is fine
        
        modified_sql = chosen_sql
        reasons = []
        
        if needs_nl:
            result = self.add_nulls_last(modified_sql)
            if result:
                modified_sql = result
                reasons.append("Add NULLS LAST")
        
        if needs_d:
            result = self.add_distinct(modified_sql)
            if result:
                modified_sql = result
                reasons.append("Add DISTINCT")
        
        if needs_min_null:
            result = self.add_min_null_check(modified_sql)
            if result:
                modified_sql = result
                reasons.append("Add NULL check for MIN()")

        if reasons and modified_sql != chosen_sql:
            # Get the original score
            original_score = float('-inf')
            for query in all_queries:
                if query.get("sql_exec_info", {}).get("sql") == chosen_sql:
                    original_score = query.get("score", float('-inf'))
                    break
            
            return modified_sql, " + ".join(reasons), original_score
        
        return None