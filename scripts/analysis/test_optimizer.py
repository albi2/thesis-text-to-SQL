import sqlglot
import sys
from typing import Optional
from sql_optimizer import SQLOptimizer


def normalize_sql(sql: Optional[str]) -> str:
    """Parses and regenerates SQL to ignore formatting differences."""
    if not sql:
        return "None"
    try:
        # Use 'pretty=False' for a compact, single-line representation
        return sqlglot.parse_one(sql, read='sqlite').sql(dialect='sqlite', pretty=False)
    except Exception as e:
        print(f"Error normalizing SQL: {e}\nSQL: {sql}")
        return sql

def run_test(test_name: str, original_sql: str, expected_sql: Optional[str], func_to_test):
    """Helper function to run a single test and print results."""
    print(f"--- Running Test: {test_name} ---")
    print(f"Original: {original_sql}")
    
    try:
        # Call the static method
        modified_sql = func_to_test(original_sql)
        
        # Normalize for comparison
        norm_modified = normalize_sql(modified_sql)
        norm_expected = normalize_sql(expected_sql)
        
        print(f"Expected: {norm_expected}")
        print(f"Actual:   {norm_modified}")
        
        if norm_modified == norm_expected:
            print("Result:   PASS ✅")
        else:
            print("Result:   FAIL ❌")
            
    except Exception as e:
        print(f"Result:   ERROR 💥 ({e})")
    
    print("-" * (len(test_name) + 22) + "\n")

def run_needs_test(test_name: str, original_sql: str, expected_sql: Optional[str], func_to_test):
    """Helper function to run a single test and print results."""
    print(f"--- Running Test: {test_name} ---")
    print(f"Original: {original_sql}")
    
    try:
        # Call the static method
        needs_change = func_to_test(original_sql)
        
        # Normalize for comparison
        
        expected = expected_sql != None
        
        print(f"Expected: {needs_change}")
        print(f"Actual:   {expected}")
        
        if needs_change == expected:
            print("Result:   PASS ✅")
        else:
            print("Result:   FAIL ❌")
            
    except Exception as e:
        print(f"Result:   ERROR 💥 ({e})")
    
    print("-" * (len(test_name) + 22) + "\n")

# --- Test Cases for add_nulls_last ---
print("====================================")
print("🧪 Testing add_nulls_last...")
print("====================================")

nulls_last_tests = [
    (
        "Simple implicit ASC",
        "SELECT name FROM users ORDER BY age",
        "SELECT name FROM users WHERE age IS NOT NULL ORDER BY age"
    ),
    (
        "Simple explicit ASC",
        "SELECT name FROM users ORDER BY age ASC",
        "SELECT name FROM users WHERE age IS NOT NULL ORDER BY age ASC"
    ),
    (
        "DESC (should not change)",
        "SELECT name FROM users ORDER BY age DESC",
        None  # Expect no modification
    ),
    (
        "Already has NULLS LAST (should not change)",
        "SELECT name FROM users ORDER BY age ASC NULLS LAST",
        None  # Expect no modification
    ),
    (
        "Existing WHERE clause",
        "SELECT name FROM users WHERE country = 'USA' ORDER BY age",
        "SELECT name FROM users WHERE country = 'USA' AND age IS NOT NULL ORDER BY age"
    ),
    (
        "Multiple ASC columns",
        "SELECT name FROM users ORDER BY age, score ASC",
        "SELECT name FROM users WHERE age IS NOT NULL AND score IS NOT NULL ORDER BY age, score ASC"
    ),
    (
        "Mixed ASC and DESC",
        "SELECT name FROM users ORDER BY age ASC, score DESC",
        "SELECT name FROM users WHERE age IS NOT NULL ORDER BY age ASC, score DESC"
    ),
    (
        "Column inside CAST (should skip)",
        "SELECT name FROM users ORDER BY CAST(age AS INT)",
        None # Expect no modification
    ),
    (
        "Column inside function",
        "SELECT name FROM users ORDER BY ABS(age)",
        "SELECT name FROM users WHERE age IS NOT NULL ORDER BY ABS(age)"
    ),
    (
        "Nested query with ORDER BY",
        "SELECT T1.name FROM users AS T1 JOIN (SELECT id, age FROM details ORDER BY age) AS T2 ON T1.id = T2.id",
        "SELECT T1.name FROM users AS T1 JOIN (SELECT id, age FROM details WHERE age IS NOT NULL ORDER BY age) AS T2 ON T1.id = T2.id"
    )
]

for name, original, expected in nulls_last_tests:
    run_test(name, original, expected, SQLOptimizer.add_nulls_last)


# --- Test Cases for add_min_null_check ---
print("\n=======================================")
print("🧪 Testing add_min_null_check...")
print("=======================================")

min_null_tests = [
    (
        "Simple MIN()",
        "SELECT MIN(age) FROM users",
        "SELECT MIN(age) FROM users WHERE age IS NOT NULL"
    ),
    (
        "MIN() with existing WHERE",
        "SELECT MIN(age) FROM users WHERE country = 'USA'",
        "SELECT MIN(age) FROM users WHERE country = 'USA' AND age IS NOT NULL"
    ),
    (
        "Check already exists (should not change)",
        "SELECT MIN(age) FROM users WHERE age IS NOT NULL",
        None  # Expect no modification
    ),
    (
        "Check exists on other col",
        "SELECT MIN(age) FROM users WHERE score IS NOT NULL",
        "SELECT MIN(age) FROM users WHERE score IS NOT NULL AND age IS NOT NULL"
    ),
    (
        "Multiple MIN() calls",
        "SELECT MIN(age), MIN(score) FROM users",
        "SELECT MIN(age), MIN(score) FROM users WHERE age IS NOT NULL AND score IS NOT NULL"
    ),
    (
        "Multiple MIN() one check exists",
        "SELECT MIN(age), MIN(score) FROM users WHERE score IS NOT NULL",
        "SELECT MIN(age), MIN(score) FROM users WHERE score IS NOT NULL AND age IS NOT NULL"
    ),
    (
        "MAX() (should not change)",
        "SELECT MAX(age) FROM users",
        None  # Expect no modification
    ),
    (
        "MIN(expression) (should not change)",
        "SELECT MIN(age * 2) FROM users",
        None  # Expect no modification
    ),
    (
        "MIN() in subquery",
        "SELECT name FROM users WHERE age = (SELECT MIN(age) FROM details)",
        "SELECT name FROM users WHERE age = (SELECT MIN(age) FROM details WHERE age IS NOT NULL)"
    )
]

for name, original, expected in min_null_tests:
    run_test(name, original, expected, SQLOptimizer.add_min_null_check)
    run_needs_test(name, original, expected, SQLOptimizer.needs_min_null_check)

print("\nAll tests complete.")