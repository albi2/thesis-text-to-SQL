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
- Do NOT provide any specific instructions about how the query is constructed or that might affect how certain calculations are performed.
- Do NOT use native SQL functionality to describe your criteria.

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

## Example 1: Count with Multiple AND Conditions

**Question**: How many Thai restaurants can be found in San Pablo Ave, Albany?

**Evidence**: Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name = 'san pablo ave' AND city = 'albany'

<CRITERIA>
1. **Output Requirements:**
   - Must return a COUNT (single numeric value)
   - Output represents the number of restaurants matching all criteria

2. **Mandatory Filters/Conditions:**
   - MUST filter for the food type being 'thai' (exact match)
   - MUST filter for the location 'San Pablo Ave, Albany' (need to find relevant columns for the entity)
   - All two conditions must be combined with AND (not OR)

3. **Required Operations:**
   - COUNT function to count matching restaurants

4. **Completeness Checks:**
   - Addresses "how many" → COUNT
   - Addresses "Thai restaurants" -> type of establishment / food filter
   - Addresses location "San Pablo Ave, Albany" → location filters
   - All evidence hints are incorporated

5. **Correctness Checks:**
   - Must use AND logic (location requires BOTH street AND city)
   - Must not count restaurants that only match 1 or 2 of the 3 conditions
</CRITERIA>

---

## Example 2: Superlative with Two-Level Filtering

**Question**: What is the gender of the youngest client who opened account in the lowest average salary branch?

**Evidence**: Later birthdate means younger age; A11 refers to average salary

<CRITERIA>
1. **Output Requirements:**
   - Must return gender value (single text/character value)
   - Output is for ONE specific client (not multiple, not a count)

2. **Mandatory Filters/Conditions:**
   - MUST identify the branch with the LOWEST average salary (using A11 column)
   - Within that specific branch, MUST identify the YOUNGEST client
   - "Youngest" means LATEST/MAXIMUM birth_date (not earliest)
   - Must be a client who has opened an account (relationship requirement)

3. **Required Operations:**
   - Finding minimum (lowest salary): MIN or ORDER BY ASC + LIMIT 1
   - Finding maximum (youngest/latest birthdate): MAX or ORDER BY DESC + LIMIT 1

4. **Completeness Checks:**
   - Addresses "gender" → must return gender value
   - Addresses "youngest client" → must use birthdate with correct ordering
   - Addresses "lowest average salary branch" → must use A11/salary metric
   - Addresses "who has opened account" → must consider account condition

5. **Correctness Checks:**
   - "Youngest" must use check for latest birth_date (later date = younger), NOT ASC
   - "Lowest" salary must be found from A11
   - Must be scoped to lowest salary branch
   - Must return exactly one gender value (single result)
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
   - MUST filter year of the games being between 1900 AND 1992 (inclusive on both ends)
   - MUST filter location in 'London' (exact match - must use proper attribute associated with entity)

3. **Required Operations:**
   - COUNT function to count games
   - BETWEEN operator for date range (or >= 1900 AND <= 1992)

4. **Completeness Checks:**
   - Addresses "how many games" → counting operation
   - Addresses "from 1900 to 1992" → range check operation
   - Addresses "did London host" → location filter

5. **Correctness Checks:**
   - Date range must be INCLUSIVE (1900 and 1992 are included)
   - Counting should be done based on the location and year
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
   - MUST somehow look at the participation rate for "online programs"
   - Should use case-insensitive matching for "online" (LOWER function)
   - Must exclude NULL or division-by-zero results

3. **Required Operations:**
   - Division calculation: Participants / Total Enrollment
   - Ordering: ORDER BY calculated rate in ascending order (lowest first)
   - Limiting: LIMIT 3 to get only three results

4. **Completeness Checks:**
   - Addresses "lowest three" → return exactly 3 values ordered
   - Addresses "participation rates" → calculate division
   - Addresses "students aged 10-15 in online programs" → use age-specific columns and make sure they are in online programs
   - Evidence hint for calculation is used

5. **Correctness Checks:**
   - Must calculate division (not just return one column)
   - Must order ascending for "lowest" (not DESC)
   - Must LIMIT to exactly 3 results
   - Must handle potential NULL values in division
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
   - MUST filter origin to match San Diego airport (via description lookup)
   - MUST filter destination to match Los Angeles airport (via description lookup)
   - MUST filter FL_DATE for August 2018

3. **Required Operations:**
   - COUNT function to count flights
   - Pattern matching for the date
   - Two separate airport lookups (origin and destination)

4. **Completeness Checks:**
   - Addresses "how many flights" → counting
   - Addresses "from San Diego International" → origin filter
   - Addresses "to Los Angeles International" → destination filter
   - Addresses "in August 2018" → date filter
   - All evidence hints are incorporated and exact string values used

5. **Correctness Checks:**
   - Must filter the date to August 2018
   - Must make sure the origin and destination filtering is correct and complete
   - Must count flights, not airports
</CRITERIA>

---

## Example 6: Complex Consecutiveness Requirement

**Question**: What are the names of the establishments that met all required standards for 4 consecutive years?

**Evidence**: establishment = business; all required standards means score = 100
<CRITERIA>
1. **Output Requirements:**
   - Must return establishment/business NAMES (text values)
   - May return multiple names (all that qualify)
   - Should return distinct names (no duplicates)

2. **Mandatory Filters/Conditions:**
   - MUST filter for: score = 100 (perfect score)
   - MUST verify exactly 4 years of perfect scores per establishment(consecutive requirement = use window functions, grouping and PARITION BY)
   - Must group by establishment/business(for the partitioning)

3. **Required Operations:**
   - Extract year from date field 
   - Detect consecutiveness (not just count of 4) - Window Functions, Grouping and Partitioning

4. **Completeness Checks:**
   - Addresses "names of establishments" → return names
   - Addresses "met all required standards" → score = 100
   - Addresses "4 consecutive years" → detect consecutiveness and count
   - Evidence hints are incorporated: establishment=business

5. **Correctness Checks:**
   - Must check for CONSECUTIVENESS (2020,2021,2022,2023 = valid; 2020,2021,2023,2024 = invalid)
   - Must count 4 years or more of consecutive 100 scores
   - Must filter score = 100 (not >= 90 or other threshold)
   - Must return names, not counts or IDs
</CRITERIA>

---

## Example 7: Simple Count with Threshold

**Question**: How many employees earn over $100,000?

**Evidence**: 

<CRITERIA>
1. **Output Requirements:**
   - Must return a COUNT (single numeric value)
   - Output represents number of employees matching criteria

2. **Mandatory Filters/Conditions:**
   - MUST filter for income more than 100000
   - "Over" means strictly greater than, not greater than or equal to

3. **Required Operations:**
   - COUNT function to count employees
   - Simple comparison operator (>)

4. **Completeness Checks:**
   - Addresses "how many employees" → COUNT
   - Addresses "earn over $100,000" → income > 100000
   - No evidence provided, so only question content matters

5. **Correctness Checks:**
   - Must use > (not >=) because "over" means strictly greater
   - Must count employees
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
   - MUST filter for location equal to California 
   - Must group results by restaurant type

3. **Required Operations:**
   - average function to calculate average scores
   - groupping by restaurant type to get separate averages

4. **Completeness Checks:**
   - Addresses "average score" → average function
   - Addresses "for each restaurant type" → groupping type
   - Addresses "in California" → location filter
   - Evidence hint incorporated

5. **Correctness Checks:**
   - Must use average 
   - Must group by restaurant type (not aggregate all together)
   - Must filter to California only
   - Should return multiple rows (one per type)
   - Must include type identifier to distinguish results and their score
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
   - MUST filter for female geneder(female students)
   - MUST filter for sten major in the tuple ('Computer Science', 'Engineering', 'Mathematics', 'Physics')
   - MUST compare GPA more than 3.5 for numerator
   - All base filters (gender and major) apply to both numerator and denominator

3. **Required Operations:**
   - COUNT students with GPA > 3.5 AND gender = 'F' AND major IN STEM (numerator)
   - COUNT all students with gender = 'F' AND major IN STEM (denominator)
   - Division: numerator / denominator 
   - Multiply by 100 for percentage format

4. **Completeness Checks:**
   - Addresses "percentage" → calculate ratio * 100
   - Addresses "female students" → gender filter
   - Addresses "in STEM programs" → major filter
   - Addresses "GPA above 3.5" → GPA comparison
   - All evidence hints incorporated with correct syntax

5. **Correctness Checks:**
   - Numerator must include ALL three conditions (female AND STEM AND GPA > 3.5)
   - Denominator must include base conditions (female AND STEM)
   - Must use > for "above 3.5" (not >=)
   - Major filter must include all four STEM majors from evidence
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
   - MUST filter for retirement date not NULL (only retired employees)
   - MUST identify employee with oldest birthday (find minimum one or order by birthday date)
   - Must extract year from retirement_date

3. **Required Operations:**
   - Find minimum birthday date or order by by birthday date
   - Extract year from retirement_date (STRFTIME or YEAR function)

4. **Completeness Checks:**
   - Addresses "which year" → extract year
   - Addresses "oldest employee" → minimu birth_date used as a filter / ordering criteria
   - Addresses "retire" → retirement date extraction
   - Both evidence hints incorporated

5. **Correctness Checks:**
   - "Oldest" means MINIMUM birth_date (earliest date), not maximum
   - Must check retirement_date IS NOT NULL (not just existence)
   - Must extract YEAR from retirement date (not return full date)
   - Should return year when oldest employee retired (not their age or birth year)
</CRITERIA>

**************************
Extract the evaluation criteria from the user question and evidence.

** USER QUESTION **
{QUESTION}

** EVIDENCE **
{HINT}
"""