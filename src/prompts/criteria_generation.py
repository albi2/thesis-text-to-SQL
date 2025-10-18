PROMPT = """
You are an expert at analyzing database questions and creating evaluation criteria. Your task is to read a natural language question with its evidence, then generate specific criteria to evaluate whether a SQL query correctly answers that question.

## Guidelines for Criteria Generation

Focus on:
1. **Output requirements**: What type and how many results expected based on what the question is asking for?
2. **Mandatory filters and conditions**: Every filter/condition from question and evidence that has to be applied
3. **Operations needed**: Aggregations, calculations, transformations or other logical operations
4. **Completeness**: All question parts are addressed completely
5. **Correctness**: Logical consistency and proper interpretation

Keep criteria focused on requirements, not implementation details. 

Tips:
- Do NOT name any explicit entities that might affect the selection of the database schema. Always use the most general entity names you can think of to describe the criteria.
- Do NOT provide any specific instructions about how the query should be constructed or that might affect teh generation process.
- Do NOT use whole SQL clauses to describe the criteria
- Sometimes the provided hint will not be 100% correct and it needs to be corrected and reflected in the generated criteria

## Output Format

Your entire response must be enclosed in `<CRITERIA></CRITERIA>` tags. Generate criteria in this structured format:

<CRITERIA>
EVALUATION CRITERIA:

1. Output Requirements:
   - What must be returned: [describe expected output].
   - Output format: [single value, multiple value, list, calculated field, percentage etc.]

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


## EXAMPLES 

## Example 1

**Question**: How many Thai restaurants can be found in San Pablo Ave, Albany?

**Evidence**: Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name = 'san pablo ave' AND city = 'albany'

<CRITERIA>
1. **Output Requirements:**
   - Must return a COUNT (single numeric value)
   - Output represents the number of establishments matching all criteria

2. **Mandatory Filters/Conditions:**
   - MUST filter for Thai cuisine type
   - MUST filter for San Pablo Ave street location
   - MUST filter for Albany city location
   - All three conditions must be combined with AND logic (not OR)

3. **Required Operations:**
   - COUNT aggregation to count matching establishments

4. **Completeness Checks:**
   - Addresses "how many" → COUNT operation
   - Addresses "Thai restaurants" → cuisine type filter
   - Addresses location "San Pablo Ave, Albany" → both street and city filters
   - All evidence hints are incorporated

5. **Correctness Checks:**
   - Must use AND logic (location requires both street AND city)
   - Must not count establishments that only match 1 or 2 of the 3 conditions
</CRITERIA>

---

## Example 2

**Question**: What is the gender of the youngest client who opened account in the lowest average salary branch?

**Evidence**: Later birthdate means younger age; A11 refers to average salary

<CRITERIA>
1. **Output Requirements:**
   - Must return gender value (single text/character value)
   - Output is for ONE specific client (not multiple, not a count)

2. **Mandatory Filters/Conditions:**
   - MUST identify the branch with the LOWEST average salary
   - Within that specific branch, MUST identify the YOUNGEST client
   - Must be a client who has opened an account
   - Must handle NULL values appropriately during comparisons

3. **Required Operations:**
   - Finding minimum average salary across branches
   - Finding maximum (latest) birthdate within the qualifying branch

4. **Completeness Checks:**
   - Addresses "gender" → must return gender value
   - Addresses "youngest client" → must use birthdate comparison
   - Addresses "lowest average salary branch" → must use salary metric
   - Addresses "who has opened account" → must consider account opening status

5. **Correctness Checks:**
   - "Youngest" means latest birth_date (later date = younger)
   - "Lowest" means minimum salary value
   - Must be scoped to the lowest salary branch first, then find youngest within it
   - Must return exactly one gender value (single result)
   - NULL values must not distort the superlative comparisons
</CRITERIA>

---

## Example 3

**Question**: Please list the lowest three participation rates for students aged 10-15 in online programs.

**Evidence**: Participation rate = "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)"

<CRITERIA>
1. **Output Requirements:**
   - Must return calculated participation rates (division result)
   - Must return exactly THREE values (not more, not less)
   - Must be the LOWEST three rates (not highest)

2. **Mandatory Filters/Conditions:**
   - MUST filter for online programs
   - Should use case-insensitive matching for "online"
   - Must use age-appropriate metrics (10-15 age group)
   - Must exclude NULL or division-by-zero results

3. **Required Operations:**
   - Division calculation: Participants / Total Enrollment
   - Ordering by calculated rate in ascending order (lowest first)
   - Limiting results to exactly 3

4. **Completeness Checks:**
   - Addresses "lowest three" → return exactly 3 values ordered ascending
   - Addresses "participation rates" → calculate division
   - Addresses "students aged 10-15" → use age-specific metrics
   - Addresses "online programs" → filter for online program type
   - Evidence calculation formula is used

5. **Correctness Checks:**
   - Must calculate division (not just return one metric)
   - Must order ascending for "lowest" (not descending)
   - Must limit to exactly 3 results
   - Must handle potential NULL values in division
</CRITERIA>

---

## Example 4

**Question**: How many flights were there from San Diego International airport to Los Angeles International airport in August 2018?

**Evidence**: flights from refers to ORIGIN; San Diego International airport refers to Description = 'San Diego, CA: San Diego International'; flights to refers to DEST; Los Angeles International airport refers to Description = 'Los Angeles, CA: Los Angeles International'; August 2018 refers to FL_DATE like '2018/8%'

<CRITERIA>
1. **Output Requirements:**
   - Must return a COUNT (single numeric value)
   - Output represents number of flights matching all criteria

2. **Mandatory Filters/Conditions:**
   - MUST filter origin airport to San Diego International
   - MUST filter destination airport to Los Angeles International
   - MUST filter for August 2018 time period
   - All three conditions must be satisfied simultaneously

3. **Required Operations:**
   - COUNT aggregation to count flights
   - Pattern matching for the date/month filtering
   - Airport identification for both origin and destination

4. **Completeness Checks:**
   - Addresses "how many flights" → counting flights
   - Addresses "from San Diego International" → origin filter
   - Addresses "to Los Angeles International" → destination filter
   - Addresses "in August 2018" → date filter
   - All evidence mappings are incorporated

5. **Correctness Checks:**
   - Must filter to August 2018 specifically
   - Must distinguish between origin and destination airports
   - Must count flight records, not airports
   - Both airport filters must be applied correctly
</CRITERIA>

---

## Example 5

**Question**: What is the average score for each restaurant type in California?

**Evidence**: California refers to state = 'CA'

<CRITERIA>
1. **Output Requirements:**
   - Must return AVG scores (calculated values)
   - Must return results for EACH restaurant type (multiple rows expected)
   - Should include restaurant type identifier in output

2. **Mandatory Filters/Conditions:**
   - MUST filter for California state
   - Must group results by restaurant type

3. **Required Operations:**
   - AVG aggregation to calculate average scores
   - GROUP BY restaurant type to get separate averages

4. **Completeness Checks:**
   - Addresses "average score" → AVG calculation
   - Addresses "for each restaurant type" → GROUP BY type
   - Addresses "in California" → state filter
   - Evidence hint incorporated

5. **Correctness Checks:**
   - Must use AVG (not SUM, COUNT, or other aggregations)
   - Must group by restaurant type (not aggregate all together)
   - Must filter to California only
   - Should return multiple rows (one per type)
   - Must include type identifier to distinguish results
</CRITERIA>

---

## Example 6

**Question:**
What is the average salary of employees born after 2000?

**Evidence**
average salary refers to `(SUM(CASE WHEN birth_date > '2000-01-01' THEN salary ELSE 0 END) / COUNT(department_id))`; employees born after 2000 refers to `birth_date > '2000-01-01'`

<CRITERIA>
1. **Output Requirements:**
   - Must return a numeric value representing the average salary (rounded to 2 decimal places if necessary)
   - Single value (one specific average)

2. **Mandatory Filters/Conditions:**
   - MUST filter for employees born after 2000 (`birth_date > '2000-01-01'`)
   - MUST calculate average only over qualifying employees

3. **Required Operations:**
   - Use `AVG(salary)` or equivalent (`SUM(salary) / COUNT(*)`) over employees with `birth_date > '2000-01-01'`
   - Filter strictly by `birth_date > '2000-01-01'`

4. **Completeness Checks:**
   - Addresses "average salary" → `AVG(salary)` calculation
   - Addresses "employees born after 2000" → `birth_date > '2000-01-01'`
   - Evidence hints incorporated only if logical; otherwise ignore

5. **Correctness Checks:**
   - "Average salary" means `SUM(salary) / COUNT(*)` for qualifying employees (or `AVG(salary)`), not divided by department count
   - The hint correctly identifies `birth_date > '2000-01-01'` for filtering employees born after 2000
   - The hint suggested `(SUM(CASE WHEN birth_date > '2000-01-01' THEN salary ELSE 0 END) / COUNT(department_id))`, but dividing by `COUNT(department_id)` uses the wrong denominator (total departments instead of count of qualifying employees), which would skew the average incorrectly and should be ignored; use `COUNT(*)` or `COUNT(employee_id)` for the filtered set instead
   - Must return the actual average salary value (not a sum, count, or ratio involving departments)
   - Should focus on salary average for the specified birth cohort (not include unrelated metrics like department totals)
</CRITERIA>

**************************
Extract the evaluation criteria from the user question and evidence.

** USER QUESTION **
{QUESTION}

** EVIDENCE **
{HINT}
"""