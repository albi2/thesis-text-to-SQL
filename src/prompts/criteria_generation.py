PROMPT = """
# SQL Query Evaluation Criteria Generation

You are an expert at analyzing database questions and creating evaluation criteria. Your task is to read a natural language question with its evidence/hints, then generate specific criteria to evaluate whether a SQL query correctly answers that question.

**IMPORTANT**: You will NOT know the database schema or which tables exist. Focus only on:
- What the question is asking for (output requirements)
- What filters/conditions must be applied
- What logical operations are needed
- Whether all parts of the question are addressed

## Output Format

Your entire response must be enclosed in `<CRITERIA></CRITERIA>` tags. Generate criteria in this structured format:

<CRITERIA>
EVALUATION CRITERIA:

1. Output Requirements:
   - What must be returned: [describe expected output]
   - Output format: [single value, list, calculated field, etc.]

2. Mandatory Filters/Conditions:
   - [List all conditions that MUST be present]
   - [Specify AND vs OR logic]
   - [Note comparison operators: =, >, <, >=, <=, BETWEEN, LIKE]

3. Required Operations:
   - [Aggregations: COUNT, SUM, AVG, MAX, MIN, etc.]
   - [Calculations: division, multiplication, etc.]
   - [String operations: case-insensitive matching, pattern matching]
   - [Date operations: year extraction, date ranges, etc.]

4. Completeness Checks:
   - [Verify all question parts are addressed]
   - [Check that evidence/hints are incorporated]

5. Correctness Checks:
   - [Verify logical consistency]
   - [Check for correct interpretation of superlatives]
   - [Validate comparison directions]
</CRITERIA>


---

## Example 1: Count with Multiple AND Conditions

**Question**: How many Thai restaurants can be found in San Pablo Ave, Albany?

**Evidence**: Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name = 'san pablo ave' AND city = 'albany'

<CRITERIA>
1. **Output Requirements:**
   - Must return a COUNT (single numeric value)
   - Output represents the number of restaurants matching all criteria

2. **Mandatory Filters/Conditions:**
   - MUST filter for: food_type = 'thai' (exact match)
   - MUST filter for: street_name = 'san pablo ave' (exact match)
   - MUST filter for: city = 'albany' (exact match)
   - All three conditions must be combined with AND (not OR)
   - String comparisons should match the exact values from evidence

3. **Required Operations:**
   - COUNT function to count matching restaurants
   - No calculations or string manipulations needed

4. **Completeness Checks:**
   - ✓ Addresses "how many" → COUNT
   - ✓ Addresses "Thai restaurants" → food_type filter
   - ✓ Addresses location "San Pablo Ave, Albany" → both street and city filters
   - All evidence hints are incorporated

5. **Correctness Checks:**
   - Must use AND logic (location requires BOTH street AND city)
   - Must not count restaurants that only match 1 or 2 of the 3 conditions
   - String values should match evidence exactly (case-sensitive as specified)
</CRITERIA>

---

## Example 2: Superlative with Two-Level Filtering

**Question**: What is the gender of the youngest client who opened account in the lowest average salary branch?

**Evidence**: Later birthdate refers to younger age; A11 refers to average salary

<CRITERIA>
1. **Output Requirements:**
   - Must return gender value (single text/character value)
   - Output is for ONE specific client (not multiple, not a count)

2. **Mandatory Filters/Conditions:**
   - MUST identify the branch/district with the LOWEST average salary (using A11 column)
   - Within that specific branch, MUST identify the YOUNGEST client
   - "Youngest" means LATEST/MAXIMUM birth_date (not earliest)
   - Must be a client who has an account (relationship requirement)

3. **Required Operations:**
   - Finding minimum (lowest salary): MIN or ORDER BY ASC + LIMIT 1
   - Finding maximum (youngest/latest birthdate): MAX or ORDER BY DESC + LIMIT 1
   - Two-level filtering: first find lowest salary branch, then youngest client in that branch

4. **Completeness Checks:**
   - ✓ Addresses "gender" → must return gender value
   - ✓ Addresses "youngest client" → must use birthdate with correct ordering
   - ✓ Addresses "lowest average salary branch" → must use A11/salary metric
   - ✓ Addresses "who opened account" → must consider account relationship
   - Both evidence hints incorporated correctly

5. **Correctness Checks:**
   - "Youngest" must use DESC on birth_date (later date = younger), NOT ASC
   - "Lowest" salary must use ASC on A11 (or MIN function)
   - Must NOT find youngest client globally - must be scoped to lowest salary branch
   - Must return exactly one gender value (single result)
   - Both superlatives must be applied in correct sequence
</CRITERIA>

---

## Example 3: Count with Date Range and Geographic Filter

**Question**: From 1900 to 1992, how many games did London host?

**Evidence**: From 1900 to 1992 refers to games_year BETWEEN 1900 AND 1992; London refers to city_name = 'London'

<CRITERIA>
1. **Output Requirements:**
   - Must return a COUNT (single numeric value)
   - Output represents number of games matching all criteria

2. **Mandatory Filters/Conditions:**
   - MUST filter for: games_year BETWEEN 1900 AND 1992 (inclusive on both ends)
   - MUST filter for: city_name = 'London' (exact match)
   - Both conditions must be satisfied simultaneously (AND logic)

3. **Required Operations:**
   - COUNT function to count games
   - BETWEEN operator for date range (or >= 1900 AND <= 1992)
   - No calculations needed

4. **Completeness Checks:**
   - ✓ Addresses "how many games" → COUNT
   - ✓ Addresses "from 1900 to 1992" → date range filter
   - ✓ Addresses "London host" → city filter
   - Both evidence hints are incorporated

5. **Correctness Checks:**
   - Date range must be INCLUSIVE (1900 and 1992 are included)
   - Must use AND between date and city conditions (not OR)
   - BETWEEN should include both boundary values
   - City name match should be exact: 'London'
</CRITERIA>

---

## Example 4: Calculated Field with Pattern Matching and Ordering

**Question**: Please list the lowest three participation rates for students aged 10-15 in online programs.

**Evidence**: Participation rate = "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)"

<CRITERIA>
1. **Output Requirements:**
   - Must return calculated participation rates (division result)
   - Must return exactly THREE values (not more, not less)
   - Must be the LOWEST three rates (not highest)

2. **Mandatory Filters/Conditions:**
   - MUST filter for "online programs" (likely using LIKE '%online%' pattern)
   - Should use case-insensitive matching for "online" (LOWER function)
   - May need to check multiple fields for "online" keyword (OR condition)
   - Must exclude NULL or division-by-zero results

3. **Required Operations:**
   - Division calculation: Participants / Total Enrollment
   - Pattern matching: LIKE '%online%' with LOWER() for case-insensitivity
   - Ordering: ORDER BY calculated rate ASC (lowest first)
   - Limiting: LIMIT 3 to get only three results

4. **Completeness Checks:**
   - ✓ Addresses "list" → return multiple values
   - ✓ Addresses "lowest three" → ORDER BY ASC + LIMIT 3
   - ✓ Addresses "participation rates" → calculate division
   - ✓ Addresses "students aged 10-15" → use age-specific columns
   - ✓ Addresses "online programs" → filter for online
   - Evidence hint for calculation is used

5. **Correctness Checks:**
   - Must calculate division (not just return one column)
   - Must order ASC for "lowest" (not DESC)
   - Must LIMIT to exactly 3 results
   - Must handle potential NULL values in division
   - "Online" matching should be flexible (LIKE, not exact =)
   - Should use case-insensitive matching
</CRITERIA>

---

## Example 5: Count with Multiple Lookup Conditions

**Question**: How many flights were there from San Diego International airport to Los Angeles International airport in August 2018?

**Evidence**: flights from refers to ORIGIN; San Diego International airport refers to Description = 'San Diego, CA: San Diego International'; flights to refers to DEST; Los Angeles International airport refers to Description = 'Los Angeles, CA: Los Angeles International'; August 2018 refers to FL_DATE like '2018/8%'

<CRITERIA>
1. **Output Requirements:**
   - Must return a COUNT (single numeric value)
   - Output represents number of flights matching all criteria

2. **Mandatory Filters/Conditions:**
   - MUST filter ORIGIN to match San Diego airport (via description lookup)
   - MUST filter DEST to match Los Angeles airport (via description lookup)
   - MUST filter FL_DATE for August 2018 using pattern: '2018/8%'
   - All three conditions must be combined with AND
   - Airport matching requires resolving full descriptions to codes

3. **Required Operations:**
   - COUNT function to count flights
   - String pattern matching: LIKE '2018/8%' for date
   - Lookup operations: resolve airport descriptions to codes
   - Two separate airport lookups (origin and destination)

4. **Completeness Checks:**
   - ✓ Addresses "how many flights" → COUNT
   - ✓ Addresses "from San Diego International" → ORIGIN filter
   - ✓ Addresses "to Los Angeles International" → DEST filter
   - ✓ Addresses "in August 2018" → date filter
   - All evidence hints are incorporated and exact string values used

5. **Correctness Checks:**
   - Must distinguish between ORIGIN and DEST (from vs to)
   - Both airports must be filtered (not just one)
   - Date pattern must match '2018/8%' (not '2018-08%' or other format)
   - Must use exact airport descriptions from evidence
   - Must count flights, not airports
   - All conditions must use AND logic
</CRITERIA>

---

## Example 6: Complex Consecutiveness Requirement

**Question**: What are the names of the establishments that met all required standards for 4 consecutive years?

**Evidence**: establishment = business; met all required standards for 4 consecutive years means COUNT(year(date)) = 4 where score = 100

<CRITERIA>
1. **Output Requirements:**
   - Must return establishment/business NAMES (text values)
   - May return multiple names (all that qualify)
   - Should return distinct names (no duplicates)

2. **Mandatory Filters/Conditions:**
   - MUST filter for: score = 100 (perfect score)
   - MUST verify exactly 4 years of perfect scores per establishment
   - Years must be CONSECUTIVE (not just any 4 years)
   - Must group results by establishment/business

3. **Required Operations:**
   - Extract year from date field (STRFTIME('%Y', date) or equivalent)
   - COUNT years per establishment
   - Detect consecutiveness (not just count of 4)
   - May require window functions or grouping logic
   - Filter to only establishments with COUNT = 4 consecutive years

4. **Completeness Checks:**
   - ✓ Addresses "names of establishments" → return names
   - ✓ Addresses "met all required standards" → score = 100
   - ✓ Addresses "4 consecutive years" → count AND consecutiveness check
   - Evidence hints are incorporated: establishment=business, perfect score requirement

5. **Correctness Checks:**
   - Must check for CONSECUTIVENESS (2020,2021,2022,2023 = valid; 2020,2021,2023,2024 = invalid)
   - Must count exactly 4 years (not more, not less)
   - Must filter score = 100 (not >= 90 or other threshold)
   - Must return names, not counts or IDs
   - Must handle multiple establishments (not just one)
   - Cannot include establishments with 4 non-consecutive years of perfect scores
</CRITERIA>

---

## Example 7: Simple Count with Threshold

**Question**: How many employees earn over $100,000?

**Evidence**: None

<CRITERIA>
1. **Output Requirements:**
   - Must return a COUNT (single numeric value)
   - Output represents number of employees matching criteria

2. **Mandatory Filters/Conditions:**
   - MUST filter for: salary > 100000
   - Must use > (greater than), not >= (greater than or equal)
   - "Over" means strictly greater than, not equal to

3. **Required Operations:**
   - COUNT function to count employees
   - Simple comparison operator (>)

4. **Completeness Checks:**
   - ✓ Addresses "how many employees" → COUNT
   - ✓ Addresses "earn over $100,000" → salary > 100000
   - No evidence provided, so only question content matters

5. **Correctness Checks:**
   - Must use > (not >=) because "over" means strictly greater
   - Must count employees, not sum salaries
   - Threshold value must be 100000 (not 100 or other)
</CRITERIA>

---

## Example 8: Average with Multiple Grouping

**Question**: What is the average score for each restaurant type in California?

**Evidence**: California refers to state = 'CA'

<CRITERIA>
1. **Output Requirements:**
   - Must return average scores (calculated values)
   - Must return results for EACH restaurant type (multiple rows expected)
   - Should include restaurant type identifier in output

2. **Mandatory Filters/Conditions:**
   - MUST filter for: state = 'CA' (California only)
   - Must group results by restaurant type

3. **Required Operations:**
   - AVG function to calculate average scores
   - GROUP BY restaurant type to get separate averages
   - No LIMIT (want all restaurant types)

4. **Completeness Checks:**
   - ✓ Addresses "average score" → AVG function
   - ✓ Addresses "for each restaurant type" → GROUP BY type
   - ✓ Addresses "in California" → state filter
   - Evidence hint incorporated

5. **Correctness Checks:**
   - Must use AVG (not SUM or COUNT)
   - Must GROUP BY restaurant type (not aggregate all together)
   - Must filter to California only
   - Should return multiple rows (one per type)
   - Must include type identifier to distinguish results
</CRITERIA>

---

## Example 9: Percentage/Ratio Calculation with Multiple Conditions

**Question**: What percentage of female students in STEM programs have a GPA above 3.5?

**Evidence**: female refers to gender = 'F'; STEM programs refers to major IN ('Computer Science', 'Engineering', 'Mathematics', 'Physics')

<CRITERIA>
1. **Output Requirements:**
   - Must return a percentage value (calculated from ratio)
   - Single numeric value (may need to multiply by 100 for percentage)

2. **Mandatory Filters/Conditions:**
   - MUST filter for: gender = 'F' (female students)
   - MUST filter for: major IN ('Computer Science', 'Engineering', 'Mathematics', 'Physics')
   - MUST compare GPA > 3.5 for numerator
   - All base filters (gender and major) apply to both numerator and denominator

3. **Required Operations:**
   - COUNT students with GPA > 3.5 AND gender = 'F' AND major IN STEM (numerator)
   - COUNT all students with gender = 'F' AND major IN STEM (denominator)
   - Division: numerator / denominator
   - Optional: multiply by 100 for percentage format

4. **Completeness Checks:**
   - ✓ Addresses "percentage" → calculate ratio * 100
   - ✓ Addresses "female students" → gender filter
   - ✓ Addresses "in STEM programs" → major filter
   - ✓ Addresses "GPA above 3.5" → GPA comparison
   - All evidence hints incorporated with correct syntax

5. **Correctness Checks:**
   - Numerator must include ALL three conditions (female AND STEM AND GPA > 3.5)
   - Denominator must include base conditions (female AND STEM)
   - Must use > for "above 3.5" (not >=)
   - Major filter must include all four STEM majors from evidence
   - Must use IN operator (or multiple OR conditions) for major list
   - Division should handle potential zero denominator
</CRITERIA>

---

## Example 10: Maximum with Date Extraction

**Question**: In which year did the oldest employee retire?

**Evidence**: oldest employee refers to MIN(birth_date); retire refers to retirement_date IS NOT NULL

<CRITERIA>
1. **Output Requirements:**
   - Must return a YEAR value (4-digit number or extracted year)
   - Single value (one specific year)

2. **Mandatory Filters/Conditions:**
   - MUST filter for: retirement_date IS NOT NULL (only retired employees)
   - MUST identify employee with MIN(birth_date) = oldest
   - Must extract year from retirement_date

3. **Required Operations:**
   - Find MIN(birth_date) to identify oldest employee
   - Extract year from retirement_date (STRFTIME or YEAR function)
   - May need to order by birth_date ASC + LIMIT 1

4. **Completeness Checks:**
   - ✓ Addresses "which year" → extract year
   - ✓ Addresses "oldest employee" → MIN birth_date
   - ✓ Addresses "retire" → retirement_date check
   - Both evidence hints incorporated

5. **Correctness Checks:**
   - "Oldest" means MINIMUM birth_date (earliest date), not maximum
   - Must check retirement_date IS NOT NULL (not just existence)
   - Must extract YEAR from retirement date (not return full date)
   - Should return year when oldest employee retired (not their age or birth year)
</CRITERIA>

---

Now its your turn to analyze real question:

【User Question】
{QUESTION}

【Evidence】
{HINT}

## Guidelines for Criteria Generation

Focus on:
1. **Output format**: What type and how many results expected?
2. **All conditions**: Every filter from question and evidence
3. **Logical operators**: AND vs OR, comparison operators
4. **Operations needed**: Aggregations, calculations, transformations
5. **Superlatives interpretation**: Highest/lowest/oldest/newest ordering
6. **Completeness**: All question parts addressed
7. **Correctness**: Logical consistency and proper interpretation

Keep criteria focused on requirements, not implementation details. Avoid specifying exact syntax or table / column names. Otherwise therew will be severe consequences.
"""