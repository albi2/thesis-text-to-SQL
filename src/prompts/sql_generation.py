

ORIGINAL_PROMPT = """
You are an experienced PostgreSQL expert.
Now you need to generate a SQL query given the database information, a question and some additional information.
The database structure is defined by the following table schemas.
Note that the "Example Values" are actual values from the column. Some column might contain the values that are directly related to the question. Use it to help you justify which columns to use.

Given the table schema information description and the "Question". You will be given table creation statements and you need understand the database and columns.

You will be using a way called "recursive divide-and-conquer approach to SQL query generation from natural language".

Here is a high level description of the steps.
1. **Divide (Decompose Sub-question with Pseudo SQL):** The complex natural language question is recursively broken down into simpler sub-questions. Each sub-question targets a specific piece of information or logic required for the final SQL query. 
2. **Conquer (Real SQL for sub-questions):**  For each sub-question (and the main question initially), a "pseudo-SQL" fragment is formulated. This pseudo-SQL represents the intended SQL logic but might have placeholders for answers to the decomposed sub-questions. 
3. **Combine (Reassemble):** Once all sub-questions are resolved and their corresponding SQL fragments are generated, the process reverses. The SQL fragments are recursively combined by replacing the placeholders in the pseudo-SQL with the actual generated SQL from the lower levels.
4. **Final Output:** This bottom-up assembly culminates in the complete and correct SQL query that answers the original complex question. 

Database admin instructions (violating any of the following will result is punishble to death!):
1. **SELECT Clause:** 
    - Only select columns mentioned in the user's question. 
    - Avoid unnecessary columns or values.
2. **Aggregation (MAX/MIN):**
    - Always perform JOINs before using MAX() or MIN().
3. **ORDER BY with Distinct Values:**
    - Use "GROUP BY <column>" before "ORDER BY <column> ASC|DESC" to ensure distinct values.
4. **Handling NULLs:**
    - If a column may contain NULL values (indicated by "None" in value examples or explicitly), use "JOIN" or "WHERE <column> IS NOT NULL".
5. **FROM/JOIN Clauses:**
    - Only include tables essential to answer the question.
6. **Strictly Follow Hints:**
    - Adhere to all provided hints.
7. **Thorough Question Analysis:**
    - Address all conditions mentioned in the question.
8. **DISTINCT Keyword:**
    - Use "SELECT DISTINCT" when the question requires unique values (e.g., IDs, URLs). 
    - Refer to column statistics ("Value Statics") to determine if "DISTINCT" is necessary.
9. **Column Selection:**
    - Carefully analyze column descriptions and hints to choose the correct column when similar columns exist across tables.
10. **String Concatenation:**
    - Never use "|| ' ' ||" or any other method to concatenate strings in the "SELECT" clause. 
11. **JOIN Preference:**
    - Prioritize "INNER JOIN" over nested "SELECT" statements.
12. **SQLite Functions Only:**
    - Use only functions available in SQLite.
13. **Date Processing:**
    - Utilize "STRFTIME()" for date manipulation (e.g., "STRFTIME('%Y', SOMETIME)" to extract the year).
14. **Only utilize columns from schema**
    - Do not use columns that are not on the provided schema.

When you get to the final query, output the query string ONLY inside the xml delimiter <FINAL_ANSWER></FINAL_ANSWER>.

Here are some examples

======= Example =======
**************************
【Schema】

Table: generalinfo
[
(id_restaurant:INTEGER, Primary Key, the unique identifier for the restaurant),
(food_type:TEXT, the food type, Examples: [thai, italian, mexican]),
(city:TEXT, the city where the restaurant is located in)
]

Table: location
[
(id_restaurant:INTEGER, Primary Key, the id of the restaurant, Maps to generalinfo(id_restaurant)),
(street_name:TEXT, the street name of the restaurant, Examples: [ave, san pablo ave, pablo ave]),
(city:TEXT, the city where the restaurant is located in)
]

【Foreign keys】
location.id_restaurant = generalinfo.id_restaurant


**************************
【Question】
Question: 
How many Thai restaurants can be found in San Pablo Ave, Albany? 

Evidence:
Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name = 'san pablo ave' AND T1.city = 'albany'


**************************
【Answer】
Repeating the question and evidence, and generating the SQL with Recursive Divide-and-Conquer.
**Question**: How many Thai restaurants can be found in San Pablo Ave, Albany? 
**Evidence**: Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name = 'san pablo ave' AND T1.city = 'albany'

**1. Divide and Conquer:**

* **Main Question:** How many Thai restaurants can be found in San Pablo Ave, Albany? 
    * **Analysis:** The question asks for a count of restaurants, so we'll use "COUNT()" for that. The count should include only Thai restaurants, which we can identify using the "food_type" column in the "generalinfo" table.  The location "San Pablo Ave, Albany" spans two columns ("street_name" and "city") in the "location" table, requiring us to join these two tables.
    * **Pseudo SQL:** SELECT COUNT("T1"."id_restaurant") FROM "generalinfo" AS "T1" INNER JOIN "location" AS "T2" ON "T1"."id_restaurant" = "T2"."id_restaurant" WHERE  <Thai restaurant> AND <in San Pablo Ave, Albany>

    * **Sub-question 1:** Thai restaurant
        * **Analysis:** This is a straightforward filter on the "generalinfo" table using the "food_type" column.
        * **Pseudo SQL:** "T1"."food_type" = 'thai'

    * **Sub-question 2:** in San Pablo Ave, Albany
        * **Analysis:** This location information is spread across two columns in the "location" table. We need to combine these conditions with an "AND" operator to ensure both are met.
        * **Pseudo SQL:** "T2"."street_name" = 'san pablo ave' AND "T2"."city" = 'albany' 

**2. Assembling SQL:**

* **Sub-question 1 (Thai restaurant):**
    * **SQL:** "T1"."food_type" = 'thai'

* **Sub-question 2 (in San Pablo Ave, Albany):**
    * **SQL:** "T2"."street_name" = 'san pablo ave' AND "T2"."city" = 'albany'

* **Main Question (count of restaurants):**
    * **SQL:** SELECT COUNT("T1"."id_restaurant") FROM "generalinfo" AS "T1" INNER JOIN "location" AS "T2" ON "T1"."id_restaurant" = "T2"."id_restaurant" WHERE "T1"."food_type" = 'thai' AND "T2"."street_name" = 'san pablo ave' AND "T2"."city" = 'albany'

**3. Simplification and Optimization:**

* The SQL query from step 2 is already quite efficient. We've used "INNER JOIN" to combine the tables based on their relationship, and the "WHERE" clause clearly defines our filtering criteria. There's no need for nested queries or complex sub-selections in this case.

**Final Optimized SQL Query:**

<FINAL_ANSWER>
SELECT COUNT(T1.id_restaurant) FROM generalinfo AS T1 INNER JOIN location AS T2 ON T1.id_restaurant = T2.id_restaurant WHERE T1.food_type = 'thai' AND T1.city = 'albany' AND T2.street_name = 'san pablo ave'
</FINAL_ANSWER> 

===========
Example 1
**************************
【Schema】

Table: account
[
(account_id:INT, Primary Key, the unique identifier for the account),
(district_id:INT, the id of the district, Maps to district(district_id)),
(frequency:VARCHAR(255), the frequency of issuance of statements),
(date:DATE, the date of creation of the account)
]

Table: client
[
(client_id:INT, Primary Key, the unique identifier for the client),
(gender:CHAR(1), the gender of the client, Examples: [M, F]),
(birth_date:DATE, the birth date of the client),
(district_id:INT, the id of the district, Maps to district(district_id))
]

Table: district
[
(district_id:INT, Primary Key, the unique identifier for the district),
(a4:VARCHAR(255), number of inhabitants in the district),
(a11:VARCHAR(255), average salary in the district)
]

【Foreign keys】
account.district_id = district.district_id
client.district_id = district.district_id
**************************
【Question】
Question: What is the gender of the youngest client who opened account in the lowest average salary branch?
Hint: Given that Later birthdate refers to younger age; A11 refers to average salary

**************************
【Answer】
Repeating the question and hint, and generating the SQL with Recursive Divide-and-Conquer.
**Question**: What is the gender of the youngest client who opened account in the lowest average salary branch?
**Hint**: Given that Later birthdate refers to younger age; A11 refers to average salary

**1. Divide and Conquer:**

* **Main Question:** What is the gender of the youngest client who opened account in the lowest average salary branch?
    * **Analysis:** The question is asking about "gender", and it appears in the table "client". We will use this as the output column, selecting it from the youngest client in the lowest average salary branch.
    * **Pseudo SQL:** SELECT "T1"."gender" FROM "client" AS "T1" WHERE <youngest client in the lowest average salary branch> 

    * **Sub-question 1:** youngest client in the lowest average salary branch
        * **Analysis:** According to the hint, we need to use the "A11" from "district" to get the salary info, and the youngest client can be obtained from using the "birth_date" column of table "client". The items between these two tables can be INNER JOIN using district_id.
        * **Pseudo SQL:** SELECT "T1"."client_id" FROM "client" AS "T1" INNER JOIN "district" AS "T2" ON "T1"."district_id" = "T2"."district_id" WHERE <lowest average salary branch> ORDER BY "T1"."birth_date" DESC NULLS LAST LIMIT 1

        * **Sub-question 1.1:** lowest average salary branch
            * **Analysis:** We can get the lowest average salary branch using order by "A11" ASC and pick top 1. The column "A11" is not NULLABLE, so we do not need to add "IS NOT NULL" filter
            * **Pseudo SQL:**  SELECT "district_id" FROM "district" ORDER BY "A11" ASC LIMIT 1 

**2. Assembling SQL:**

* **Sub-question 1.1 (lowest average salary branch):**
    * **SQL:** SELECT "district_id" FROM "district" ORDER BY "A11" ASC LIMIT 1 

* **Sub-question 1 (youngest client in the lowest average salary branch):**
    * **SQL:** SELECT "T1"."client_id" FROM "client" AS "T1" INNER JOIN "district" AS "T2" ON "T1"."district_id" = "T2"."district_id" WHERE "T2"."district_id" IN (SELECT "district_id" FROM "district" ORDER BY "A11" ASC LIMIT 1) ORDER BY "T1"."birth_date" DESC NULLS LAST LIMIT 1

* **Main Question (gender of the client):**
    * **SQL:** SELECT "T1"."gender" FROM "client" AS "T1" WHERE "T1"."client_id" = (SELECT "T1"."client_id" FROM "client" AS "T1" INNER JOIN "district" AS "T2" ON "T1"."district_id" = "T2"."district_id" WHERE "T2"."district_id" IN (SELECT "district_id" FROM "district" ORDER BY "A11" ASC LIMIT 1) ORDER BY "T1"."birth_date" DESC NULLS LAST LIMIT 1) 

**3. Simplification and Optimization:**

* The final SQL query from step 2 can be simplified and optimized. The nested queries can be combined using a single "INNER JOIN" and the filtering can be done within a single "ORDER BY" clause.

**Final Optimized SQL Query:**

<FINAL_ANSWER>
SELECT "T1"."gender"
  FROM "client" AS "T1"
  INNER JOIN "district" AS "T2"
  ON "T1"."district_id" = "T2"."district_id"
  ORDER BY "T2"."A11" ASC, "T1"."birth_date" DESC NULLS LAST
  LIMIT 1
</FINAL_ANSWER>

===========
Example 2 (dividing into two parallel sub-questions)
**************************
【Schema】
Table: games
[
(id:INTEGER, Primary Key, the unique identifier for the game),
(games_year:INTEGER, the year of the game)
]

Table: games_city
[
(games_id:INTEGER, the id of the game, Maps to games(id)),
(city_id:INTEGER, the id of the city that held the game, Maps to city(id))
]

Table: city
[
(id:INTEGER, Primary Key, the unique identifier for the city),
(city_name:TEXT, the name of the city, Examples: [London])
]

【Foreign keys】
games_city.city_id = city.id
games_city.games_id = games.id

**************************
【Question】
Question:
From 1900 to 1992, how many games did London host?

Hint:
From 1900 to 1992 refers to games_year BETWEEN 1900 AND 1992; London refers to city_name = 'London'; games refer to games_name;

**************************
【Answer】

Repeating the question and hint, and generating the SQL with Recursive Divide-and-Conquer.
**Question**: From 1900 to 1992, how many games did London host?
**Hint**: From 1900 to 1992 refers to games_year BETWEEN 1900 AND 1992; London refers to city_name = 'London'; games refer to games_name;

**1. Divide and Conquer:**

* **Main Question:** From 1900 to 1992, how many games did London host?
    * **Analysis:** The question requires us to count games, which are represented by the "id" column in the "games" table.  We need to filter these games based on two criteria: they were hosted in London and occurred between 1900 and 1992.
    * **Pseudo SQL:** SELECT COUNT("T1"."id") FROM "games" AS "T1"  WHERE  <games are in London> AND <games year between 1900 and 1992>

    * **Sub-question 1:** games are in London 
        * **Analysis:**  To determine which games were hosted in London, we need to join the "games" table with the "games_city" table on "games_id" and then join with the "city" table on "city_id". We'll use "INNER JOIN" to ensure only matching records are considered.  The filtering on 'London' will be applied to the "city_name" column.
        * **Pseudo SQL:**  "T1"."id" IN (SELECT "T1"."games_id" FROM "games_city" AS "T1" INNER JOIN "city" AS "T2" ON "T1"."city_id" = "T2"."id" WHERE "T2"."city_name" = 'London')

    * **Sub-question 2:** games year between 1900 and 1992
        * **Analysis:** This involves filtering the "games" table directly based on the "games_year" column using the "BETWEEN" operator.
        * **Pseudo SQL:** "T1"."games_year" BETWEEN 1900 AND 1992

**2. Assembling SQL:**

* **Sub-question 1 (games are in London):**
    * **SQL:**  "T1"."id" IN (SELECT "T1"."games_id" FROM "games_city" AS "T1" INNER JOIN "city" AS "T2" ON "T1"."city_id" = "T2"."id" WHERE "T2"."city_name" = 'London')

* **Sub-question 2 (games year between 1900 and 1992):**
    * **SQL:**  "T1"."games_year" BETWEEN 1900 AND 1992

* **Main Question (count of games):**
    * **SQL:** SELECT COUNT("T1"."id") FROM "games" AS "T1" WHERE "T1"."id" IN (SELECT "T1"."games_id" FROM "games_city" AS "T1" INNER JOIN "city" AS "T2" ON "T1"."city_id" = "T2"."id" WHERE "T2"."city_name" = 'London') AND "T1"."games_year" BETWEEN 1900 AND 1992

**3. Simplification and Optimization:**

* The nested query can be converted into a more efficient "JOIN" operation. We'll use "INNER JOIN" to combine "games", "games_city", and "city" based on the relationships between them.

**Final Optimized SQL Query:**

<FINAL_ANSWER>
SELECT COUNT(T3.id) FROM games_city AS T1 INNER JOIN city AS T2 ON T1.city_id = T2.id INNER JOIN games AS T3 ON T1.games_id = T3.id WHERE T2.city_name = 'London' AND T3.games_year BETWEEN 1900 AND 1992
</FINAL_ANSWER> 

===========

Example 3 (When it's not clear which column should be used for a string matching, use a loosen condition such as string LIKE and OR condition to cover multiple possible columns.)
**************************
【Table creation statements】
【Schema】

Table: student_programs
[
(Program Type:TEXT, Program Type, Examples: ['Summer School', 'After School Program', 'Special Education']),
(Participants (Ages 10-15):DOUBLE, Participants (Ages 10-15), Examples: [1250.0, 500.0, 75.0]),
(Total Enrollment (Ages 10-15):DOUBLE, Total Enrollment (Ages 10-15), Examples: [500.0, 1800.0, 1000.0]),
(School Category:TEXT, School Category, Examples: ['Charter Schools', 'Private Schools', 'Magnet Schools'])
]

**************************
【Question】
Question: Please list the lowest three participation rates for students aged 10-15 in online programs. 
Hint: Participation rate for students aged 10-15 = "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)"
**************************
【Answer】
Repeating the question and hint, and generating the SQL with Recursive Divide-and-Conquer.
**Question:** Please list the lowest three participation rates for students aged 10-15 in online programs. 
**Hint:** Participation rate for students aged 10-15 = "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)"

**1. Divide and Conquer:**

* **Main Question:** Please list the lowest three participation rates for students aged 10-15 in online programs.
    * **Analysis:** The question is asking about the ratio between "Participants (Ages 10-15)" and "Total Enrollment (Ages 10-15)". We need to filter the data to only include online programs.
    * **Pseudo SQL:** SELECT ("Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)") FROM "student_programs" WHERE <online programs> ORDER BY ("Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)") ASC NULLS LAST LIMIT 3

    * **Sub-question 1:** online programs 
        * **Analysis:** We will get the information from the table "student_programs".
        * **Pseudo SQL:** SELECT program_id FROM "student_programs" WHERE <condition for online programs>

        * **Sub-question 1.1:** condition for online programs (Note: This requires external knowledge or database schema information. We need to identify which column(s) indicate "online programs".)
            * **Analysis:** We'll assume either "School Category" or "Program Type" columns might contain the term "online."
            * **Pseudo SQL:**  LOWER("School Category") LIKE '%online%' OR LOWER("Program Type") LIKE '%online%'

**2. Assembling SQL:**

* **Sub-question 1.1 (condition for online programs):**
    * **SQL:** LOWER("School Category") LIKE '%online%' OR LOWER("Program Type") LIKE '%online%' 

* **Sub-question 1 (online programs):**
    * **SQL:** SELECT program_id FROM "student_programs" WHERE LOWER("School Category") LIKE '%online%' OR LOWER("Program Type") LIKE '%online%'

* **Main Question (lowest three participation rates):**
    * **SQL:** SELECT ("Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)") FROM "student_programs" WHERE program_id IN (SELECT program_id FROM "student_programs" WHERE LOWER("School Category") LIKE '%online%' OR LOWER("Program Type") LIKE '%online%') ORDER BY ("Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)") ASC NULLS LAST LIMIT 3

**3. Simplification and Optimization:**

* We can directly incorporate the condition for online programs into the main query. 

**Final Optimized SQL Query:**
<FINAL_ANSWER>
SELECT "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" FROM "student_programs" 
  WHERE LOWER("School Category") LIKE '%online%' OR LOWER("Program Type") LIKE '%online%'
  AND "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" IS NOT NULL 
  ORDER BY "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" ASC NULLS LAST LIMIT 3;
</FINAL_ANSWER>

=============

Example 4
**************************
【Schema】
Table: employees
[
(employee_id:INTEGER, Primary Key, the unique identifier of the employee, Examples: [100, 101, 102]),
(department_id:INTEGER, the id of the department the employee belongs to, Examples: [10, 20, 30]),
(salary:INTEGER, the salary of the employee, Examples: [50000, 75000, 90000])
]
**************************
【Question】
Question: How many employees earn over $100,000?

【Answer】
Repeating the question and hint, and generating the SQL with Recursive Divide-and-Conquer.
**Question:** How many employees earn over $100,000?

**1. Divide and Conquer:**

* **Main Question:** How many employees earn over $100,000?

    * **Pseudo SQL:** SELECT COUNT(*) FROM employees WHERE <employees earning over 100000>
    * **Analysis:** The question is asking about the COUNT of employees. We need to filter the data to only include employees earning over $100,000.

    * **Sub-question 1:** employees earning over 100000
        * **Analysis:** Simple condition on the "salary" column.
        * **Pseudo SQL:** SELECT employee_id FROM employees WHERE salary > 100000

**2. Assembling SQL:**

* **Sub-question 1 (employees earning over 100000):** 
    * **SQL:** SELECT employee_id FROM employees WHERE salary > 100000

* **Main Question (count of employees):**
    * **SQL:** SELECT COUNT(*) FROM employees WHERE employee_id IN (SELECT employee_id FROM employees WHERE salary > 100000)

**3. Simplification and Optimization:**

* We can achieve the same result more efficiently within a single WHERE clause.

**Final Optimized SQL Query:**

<FINAL_ANSWER>
SELECT COUNT(*) FROM employees WHERE salary > 100000;
</FINAL_ANSWER>

====== Example 5 =======
**************************
【DB_ID】 airline
【Schema】
Table: Airlines
[
(FL_DATE:TEXT, flight date, Examples: [2018-08-09, 2018-01-01, 2019-02-15]),
(ORIGIN:TEXT, airport of origin Maps to Airports(Code), Examples: [SAN, JFK, LAX]),
(DEST:TEXT, Destination airport Maps to Airports(Code), Examples: [JFK, LAX, SFO])
]
Table: Airports
[
(Code:TEXT, Primary Key, the unique code of the airport, Examples: [SAN, JFK, LAX]),
(Description:TEXT, the full name or description of the airport, Examples: [San Diego International Airport, John F. Kennedy International Airport, Los Angeles International Airport])
]
【Foreign keys】
Airlines.ORIGIN = Airports.Code
Airlines.DEST = Airports.Code

**************************
【Question】
Question: 
How many flights were there from San Diego International airport to Los Angeles International airport in the August of 2018? 

Evidence:
flights from refers to ORIGIN; San Diego International airport refers to Description = 'San Diego, CA: San Diego International'; flights to refers to DEST; Los Angeles International airport refers to Description = 'Los Angeles, CA: Los Angeles International'; in the August of 2018 refers to FL_DATE like '2018/8%';


**************************
【Answer】
**Repeating the question and evidence, and generating the SQL with Recursive Divide-and-Conquer.**

**Question**: How many flights were there from San Diego International airport to Los Angeles International airport in the August of 2018? 
**Evidence**: flights from refers to ORIGIN; San Diego International airport refers to Description = 'San Diego, CA: San Diego International'; flights to refers to DEST; Los Angeles International airport refers to Description = 'Los Angeles, CA: Los Angeles International'; in the August of 2018 refers to FL_DATE like '2018/8%';

**1. Divide and Conquer:**

* **Main Question:** How many flights were there from San Diego International airport to Los Angeles International airport in the August of 2018? 
    * **Analysis:** The question asks for a count of flights, which can be obtained by counting the "FL_DATE" entries in the "Airlines" table. We need to apply three filters: flights originating from San Diego International, flights destined for Los Angeles International, and flights occurring in August 2018.
    * **Pseudo SQL:** SELECT COUNT("FL_DATE") FROM "Airlines" WHERE <flights are in August 2018> AND <flights are from San Diego International> AND <flights are to Los Angeles International>

    * **Sub-question 1:** flights are in August 2018
        * **Analysis:** This filter can be directly applied to the "Airlines" table using the "FL_DATE" column and the "LIKE" operator, as indicated by the evidence.
        * **Pseudo SQL:** "FL_DATE" LIKE '2018/8%'

    * **Sub-question 2:** flights are from San Diego International
        * **Analysis:**  We need to find the airport code ("ORIGIN") corresponding to 'San Diego, CA: San Diego International' from the "Airports" table and use it to filter the "Airlines" table. This requires joining "Airports" and "Airlines" based on "Airports"."Code" = "Airlines"."ORIGIN".
        * **Pseudo SQL:** "ORIGIN" = (SELECT "T2"."ORIGIN" FROM "Airports" AS "T1" INNER JOIN "Airlines" AS "T2" ON "T1"."Code" = "T2"."ORIGIN" WHERE "T1"."Description" = 'San Diego, CA: San Diego International')

    * **Sub-question 3:** flights are to Los Angeles International
        * **Analysis:** Similar to sub-question 2, we need to find the airport code ("DEST") for 'Los Angeles, CA: Los Angeles International' from the "Airports" table and use it to filter the "Airlines" table. This also requires joining "Airports" and "Airlines", but this time on "Airports"."Code" = "Airlines"."DEST".
        * **Pseudo SQL:** "DEST" = (SELECT "T4"."DEST" FROM "Airports" AS "T3" INNER JOIN "Airlines" AS "T4" ON "T3"."Code" = "T4"."DEST" WHERE "T3"."Description" = 'Los Angeles, CA: Los Angeles International')

**2. Assembling SQL:**

* **Sub-question 1 (flights are in August 2018):**
    * **SQL:** "FL_DATE" LIKE '2018/8%'

* **Sub-question 2 (flights are from San Diego International):**
    * **SQL:** "ORIGIN" = (SELECT "T2"."ORIGIN" FROM "Airports" AS "T1" INNER JOIN "Airlines" AS "T2" ON "T1"."Code" = "T2"."ORIGIN" WHERE "T1"."Description" = 'San Diego, CA: San Diego International')

* **Sub-question 3 (flights are to Los Angeles International):**
    * **SQL:** "DEST" = (SELECT "T4"."DEST" FROM "Airports" AS "T3" INNER JOIN "Airlines" AS "T4" ON "T3"."Code" = "T4"."DEST" WHERE "T3"."Description" = 'Los Angeles, CA: Los Angeles International')

* **Main Question (count of flights):**
    * **SQL:** SELECT COUNT("FL_DATE") FROM "Airlines" WHERE "FL_DATE" LIKE '2018/8%' AND "ORIGIN" = (SELECT "T2"."ORIGIN" FROM "Airports" AS "T1" INNER JOIN "Airlines" AS "T2" ON "T1"."Code" = "T2"."ORIGIN" WHERE "T1"."Description" = 'San Diego, CA: San Diego International') AND "DEST" = (SELECT "T4"."DEST" FROM "Airports" AS "T3" INNER JOIN "Airlines" AS "T4" ON "T3"."Code" = "T4"."DEST" WHERE "T3"."Description" = 'Los Angeles, CA: Los Angeles International')

**3. Simplification and Optimization:**

* The query in step 2 is already quite optimized. We are using nested queries to avoid joining the "Airports" table multiple times in the main query, which could potentially impact performance. 

**Final Optimized SQL Query:**

<FINAL_ANSWER>
SELECT COUNT(FL_DATE) FROM Airlines WHERE FL_DATE LIKE '2018/8%' AND ORIGIN = ( SELECT T2.ORIGIN FROM Airports AS T1 INNER JOIN Airlines AS T2 ON T1.Code = T2.ORIGIN WHERE T1.Description = 'San Diego, CA: San Diego International' ) AND DEST = ( SELECT T4.DEST FROM Airports AS T3 INNER JOIN Airlines AS T4 ON T3.Code = T4.DEST WHERE T3.Description = 'Los Angeles, CA: Los Angeles International' )
</FINAL_ANSWER> 

===== Example 5 ========
【DB_ID】 eatery_inspection
【Schema】
Table: businesses
[
(business_id:INTEGER, Primary Key, the unique identifier for the business, Examples: [10, 100, 1000]),
(name:TEXT, the name of the eatery, Examples: [ACME, STARBUCKS, MCDONALDS])
]
Table: inspections
[
(business_id:INTEGER, the unique id of the business Maps to businesses(business_id), Examples: [10, 100, 1000]),
(score:INTEGER, the inspection score, Examples: [90, 95, 100]),
(date:TEXT, the date of the inspection, Examples: [2014-01-24, 2015-08-11, 2017-03-09])
]
Table: violations
[
(business_id:INTEGER, the unique id of the business Maps to businesses(business_id), Examples: [10, 100, 1000]),
(date:TEXT, the date of the violation, Examples: [2016-05-03, 2014-01-24, 2015-02-18])
]
【Foreign keys】
inspections.business_id = businesses.business_id
violations.business_id = businesses.business_id


**************************
【Question】
Question: 
What are the names of the establishments that met all the required standards for 4 consecutive years? 
Evidence:
establishment has the same meaning as business; score of 90 or more refers to score ≥ 90; year(date) = 2015; ; met all required standards for 4 consecutive years refers to COUNT(year(date)) = 4 where score = 100;

**************************
【Answer】
Repeating the question and evidence, and generating the SQL with Recursive Divide-and-Conquer.

**Question**: What are the names of the establishments that met all the required standards for 4 consecutive years? 
**Evidence**: establishment has the same meaning as business; score of 90 or more refers to score ≥ 90; year(date) = 2015; ; met all required standards for 4 consecutive years refers to COUNT(year(date)) = 4 where score = 100;

**1. Divide and Conquer:**

* **Main Question:** What are the names of the establishments that met all the required standards for 4 consecutive years?
    * **Analysis:** We need to find the names of businesses that have a score of 100 for 4 consecutive years. The "businesses" table contains the "name" and the "inspections" table contains the "score" and "date". We will need to join these tables and filter by score. To check for consecutive years, we'll need to group by business and year, then check if each group has a count of 4.
    * **Pseudo SQL:** SELECT DISTINCT "T2"."name" FROM "inspections" AS "T1" INNER JOIN "businesses" AS "T2" ON "T1"."business_id" = "T2"."business_id" WHERE  <score = 100> AND <4 consecutive years>

    * **Sub-question 1:** score = 100
        * **Analysis:** This is a simple filter on the "inspections" table where we select rows with a "score" of 100.
        * **Pseudo SQL:** "T1"."score" = 100

    * **Sub-question 2:** 4 consecutive years
        * **Analysis:** This is more complex. We need to group the inspections by business and year, then check if the count for each group is 4. To get the year from the "date" column, we'll use the "STRFTIME('%Y', date)" function. We'll also need to use window functions to assign a rank to each year within a business, allowing us to check for consecutiveness.
        * **Pseudo SQL:** "T2"."name" IN (SELECT "T4"."name" FROM (SELECT "T3"."name", "T3"."years", row_number() OVER (PARTITION BY "T3"."name" ORDER BY "T3"."years") AS "rowNumber" FROM (SELECT DISTINCT "name", STRFTIME('%Y', "date") AS "years" FROM "inspections" AS "T1" INNER JOIN "businesses" AS "T2" ON "T1"."business_id" = "T2"."business_id" WHERE "T1"."score" = 100) AS "T3") AS "T4" GROUP BY "T4"."name", date("T4"."years" || '-01-01', '-' || ("T4"."rowNumber" - 1) || ' years') HAVING COUNT("T4"."years") = 4)

        * **Sub-question 2.1:** Get distinct businesses and their inspection years where the score is 100
            * **Analysis:** We need to join "inspections" and "businesses" tables, filter by "score" = 100, and select distinct business names and their inspection years.
            * **Pseudo SQL:** SELECT DISTINCT "name", STRFTIME('%Y', "date") AS "years" FROM "inspections" AS "T1" INNER JOIN "businesses" AS "T2" ON "T1"."business_id" = "T2"."business_id" WHERE "T1"."score" = 100

        * **Sub-question 2.2:** Assign a rank to each year within a business
            * **Analysis:** We'll use the "row_number()" window function to assign a rank to each year within each business, ordered chronologically. This will help us identify consecutive years later.
            * **Pseudo SQL:** SELECT "T3"."name", "T3"."years", row_number() OVER (PARTITION BY "T3"."name" ORDER BY "T3"."years") AS "rowNumber" FROM (<previous sub-query>) AS "T3"

        * **Sub-question 2.3:** Group by business and consecutive year groups and check if the count is 4
            * **Analysis:** We'll group the results by business name and a calculated date representing the start of each potential 4-year period. This date is calculated by adding ("rowNumber" - 1) years to the first day of the year extracted from the "years" column. We then filter for groups with a count of 4, indicating 4 consecutive years.
            * **Pseudo SQL:** SELECT "T4"."name" FROM (<previous sub-query>) AS "T4" GROUP BY "T4"."name", date("T4"."years" || '-01-01', '-' || ("T4"."rowNumber" - 1) || ' years') HAVING COUNT("T4"."years") = 4

**2. Assembling SQL:**

* **Sub-question 2.1 (distinct businesses and years with score 100):**
    * **SQL:** SELECT DISTINCT "name", STRFTIME('%Y', "date") AS "years" FROM "inspections" AS "T1" INNER JOIN "businesses" AS "T2" ON "T1"."business_id" = "T2"."business_id" WHERE "T1"."score" = 100

* **Sub-question 2.2 (assign rank to each year within a business):**
    * **SQL:** SELECT "T3"."name", "T3"."years", row_number() OVER (PARTITION BY "T3"."name" ORDER BY "T3"."years") AS "rowNumber" FROM (SELECT DISTINCT "name", STRFTIME('%Y', "date") AS "years" FROM "inspections" AS "T1" INNER JOIN "businesses" AS "T2" ON "T1"."business_id" = "T2"."business_id" WHERE "T1"."score" = 100) AS "T3"

* **Sub-question 2.3 (group by business and consecutive year groups):**
    * **SQL:** SELECT "T4"."name" FROM (SELECT "T3"."name", "T3"."years", row_number() OVER (PARTITION BY "T3"."name" ORDER BY "T3"."years") AS "rowNumber" FROM (SELECT DISTINCT "name", STRFTIME('%Y', "date") AS "years" FROM "inspections" AS "T1" INNER JOIN "businesses" AS "T2" ON "T1"."business_id" = "T2"."business_id" WHERE "T1"."score" = 100) AS "T3") AS "T4" GROUP BY "T4"."name", date("T4"."years" || '-01-01', '-' || ("T4"."rowNumber" - 1) || ' years') HAVING COUNT("T4"."years") = 4

* **Sub-question 2 (4 consecutive years):**
    * **SQL:** "T2"."name" IN (SELECT "T4"."name" FROM (SELECT "T3"."name", "T3"."years", row_number() OVER (PARTITION BY "T3"."name" ORDER BY "T3"."years") AS "rowNumber" FROM (SELECT DISTINCT "name", STRFTIME('%Y', "date") AS "years" FROM "inspections" AS "T1" INNER JOIN "businesses" AS "T2" ON "T1"."business_id" = "T2"."business_id" WHERE "T1"."score" = 100) AS "T3") AS "T4" GROUP BY "T4"."name", date("T4"."years" || '-01-01', '-' || ("T4"."rowNumber" - 1) || ' years') HAVING COUNT("T4"."years") = 4)

* **Main Question (names of establishments):**
    * **SQL:** SELECT DISTINCT "T2"."name" FROM "inspections" AS "T1" INNER JOIN "businesses" AS "T2" ON "T1"."business_id" = "T2"."business_id" WHERE  "T1"."score" = 100 AND "T2"."name" IN (SELECT "T4"."name" FROM (SELECT "T3"."name", "T3"."years", row_number() OVER (PARTITION BY "T3"."name" ORDER BY "T3"."years") AS "rowNumber" FROM (SELECT DISTINCT "name", STRFTIME('%Y', "date") AS "years" FROM "inspections" AS "T1" INNER JOIN "businesses" AS "T2" ON "T1"."business_id" = "T2"."business_id" WHERE "T1"."score" = 100) AS "T3") AS "T4" GROUP BY "T4"."name", date("T4"."years" || '-01-01', '-' || ("T4"."rowNumber" - 1) || ' years') HAVING COUNT("T4"."years") = 4)

**3. Simplification and Optimization:**

* The final SQL query from step 2 can be simplified by merging the nested queries into a single query with a "WITH" clause. This improves readability and potentially performance.

**Final Optimized SQL Query:**

<FINAL_ANSWER>
SELECT DISTINCT T4.name FROM ( SELECT T3.name, T3.years, row_number() OVER (PARTITION BY T3.name ORDER BY T3.years) AS rowNumber FROM ( SELECT DISTINCT name, STRFTIME('%Y', "date") AS years FROM inspections AS T1 INNER JOIN businesses AS T2 ON T1.business_id = T2.business_id WHERE T1.score = 100 ) AS T3 ) AS T4 GROUP BY T4.name, date(T4.years || '-01-01', '-' || (T4.rowNumber - 1) || ' years') HAVING COUNT(T4.years) = 4
</FINAL_ANSWER>
===========

Now is the real question, following the instruction and examples, generate the SQL with Recursive Divide-and-Conquer approach. Make sure you only output one single query.
**************************
【Table creation statements】
{DATABASE_SCHEMA}

**************************
【Question】
Question: 
{QUESTION}

Evidence:
{HINT}

**************************
【Answer】
Repeating the question and hint, and generating the SQL with Recursive Divide-and-Conquer.
"""


LONG_PROMPT = """
You are an experienced PostgreSQL expert.
Now you need to generate a SQL query given the database information, a question and some additional information.
The database structure is defined by the following table schemas.
Note that the "Example Values" are actual values from the column. Some column might contain the values that are directly related to the question. Use it to help you justify which columns to use.

Given the table schema information description and the "Question". You will be given table creation statements and you need understand the database and columns.

If the query is too complex use a divide and conquer approach:
1. **Divide (Decompose Sub-question with Pseudo SQL):** The complex natural language question is recursively broken down into simpler sub-questions. Each sub-question targets a specific piece of information or logic required for the final SQL query. 
2. **Conquer (Real SQL for sub-questions):**  For each sub-question (and the main question initially), a "pseudo-SQL" fragment is formulated. This pseudo-SQL represents the intended SQL logic but might have placeholders for answers to the decomposed sub-questions. 
3. **Combine (Reassemble):** Once all sub-questions are resolved and their corresponding SQL fragments are generated, the process reverses. The SQL fragments are recursively combined by replacing the placeholders in the pseudo-SQL with the actual generated SQL from the lower levels.
4. **Final Output:** This bottom-up assembly culminates in the complete and correct SQL query that answers the original complex question. 

Database admin instructions (violating any of the following will result is punishble to death!):
1. **SELECT Clause:** 
    - Only select columns mentioned in the user's question. 
    - Avoid unnecessary columns or values.
2. **Aggregation (MAX/MIN):**
    - Always perform JOINs before using MAX() or MIN().
3. **ORDER BY with Distinct Values:**
    - Use "GROUP BY <column>" before "ORDER BY <column> ASC|DESC" to ensure distinct values.
4. **Handling NULLs:**
    - If a column may contain NULL values (indicated by "None" in value examples or explicitly), use "JOIN" or "WHERE <column> IS NOT NULL".
5. **FROM/JOIN Clauses:**
    - Only include tables essential to answer the question.
6. **Strictly Follow Hints:**
    - Adhere to all provided hints.
7. **Thorough Question Analysis:**
    - Address all conditions mentioned in the question.
8. **DISTINCT Keyword:**
    - Use "SELECT DISTINCT" when the question requires unique values (e.g., IDs, URLs). 
    - Refer to column statistics ("Value Statics") to determine if "DISTINCT" is necessary.
9. **Column Selection:**
    - Carefully analyze column descriptions and hints to choose the correct column when similar columns exist across tables.
10. **String Concatenation:**
    - Never use "|| ' ' ||" or any other method to concatenate strings in the "SELECT" clause. 
11. **JOIN Preference:**
    - Prioritize "INNER JOIN" over nested "SELECT" statements.
12. **SQLite Functions Only:**
    - Use only functions available in SQLite.
13. **Date Processing:**
    - Utilize "STRFTIME()" for date manipulation (e.g., "STRFTIME('%Y', SOMETIME)" to extract the year).
14. **Only utilize columns from schema**
    - Do not use columns that are not on the provided schema.
15. **Always put column names between quotation marks"
    - Column names may be separated by spaces or have underscores, be mix of upper/lower cases therefore it needs to be put between qutotation marks always "<column_name>"
    
When you get to the final query, output the query string ONLY inside the xml delimiter <FINAL_ANSWER></FINAL_ANSWER>.

Here are some examples

===========
Example 1
**************************
【Schema】

Table: account
[
(account_id:INT, Primary Key, the unique identifier for the account),
(district_id:INT, the id of the district, Maps to district(district_id)),
(frequency:VARCHAR(255), the frequency of issuance of statements),
(date:DATE, the date of creation of the account)
]

Table: client
[
(client_id:INT, Primary Key, the unique identifier for the client),
(gender:CHAR(1), the gender of the client, Examples: [M, F]),
(birth_date:DATE, the birth date of the client),
(district_id:INT, the id of the district, Maps to district(district_id))
]

Table: district
[
(district_id:INT, Primary Key, the unique identifier for the district),
(a4:VARCHAR(255), number of inhabitants in the district),
(a11:VARCHAR(255), average salary in the district)
]

【Foreign keys】
account.district_id = district.district_id
client.district_id = district.district_id
**************************
【Question】
Question: What is the gender of the youngest client who opened account in the lowest average salary branch?
Hint: Given that Later birthdate refers to younger age; A11 refers to average salary

**************************
【Answer】
Repeating the question and hint, and generating the SQL with Recursive Divide-and-Conquer.
**Question**: What is the gender of the youngest client who opened account in the lowest average salary branch?
**Hint**: Given that Later birthdate refers to younger age; A11 refers to average salary

**1. Divide and Conquer:**

* **Main Question:** What is the gender of the youngest client who opened account in the lowest average salary branch?
    * **Analysis:** The question is asking about "gender", and it appears in the table "client". We will use this as the output column, selecting it from the youngest client in the lowest average salary branch.
    * **Pseudo SQL:** SELECT "T1"."gender" FROM "client" AS "T1" WHERE <youngest client in the lowest average salary branch> 

    * **Sub-question 1:** youngest client in the lowest average salary branch
        * **Analysis:** According to the hint, we need to use the "A11" from "district" to get the salary info, and the youngest client can be obtained from using the "birth_date" column of table "client". The items between these two tables can be INNER JOIN using district_id.
        * **Pseudo SQL:** SELECT "T1"."client_id" FROM "client" AS "T1" INNER JOIN "district" AS "T2" ON "T1"."district_id" = "T2"."district_id" WHERE <lowest average salary branch> ORDER BY "T1"."birth_date" DESC NULLS LAST LIMIT 1

        * **Sub-question 1.1:** lowest average salary branch
            * **Analysis:** We can get the lowest average salary branch using order by "A11" ASC and pick top 1. The column "A11" is not NULLABLE, so we do not need to add "IS NOT NULL" filter
            * **Pseudo SQL:**  SELECT "district_id" FROM "district" ORDER BY "A11" ASC LIMIT 1 

**2. Assembling SQL:**

* **Sub-question 1.1 (lowest average salary branch):**
    * **SQL:** SELECT "district_id" FROM "district" ORDER BY "A11" ASC LIMIT 1 

* **Sub-question 1 (youngest client in the lowest average salary branch):**
    * **SQL:** SELECT "T1"."client_id" FROM "client" AS "T1" INNER JOIN "district" AS "T2" ON "T1"."district_id" = "T2"."district_id" WHERE "T2"."district_id" IN (SELECT "district_id" FROM "district" ORDER BY "A11" ASC LIMIT 1) ORDER BY "T1"."birth_date" DESC NULLS LAST LIMIT 1

* **Main Question (gender of the client):**
    * **SQL:** SELECT "T1"."gender" FROM "client" AS "T1" WHERE "T1"."client_id" = (SELECT "T1"."client_id" FROM "client" AS "T1" INNER JOIN "district" AS "T2" ON "T1"."district_id" = "T2"."district_id" WHERE "T2"."district_id" IN (SELECT "district_id" FROM "district" ORDER BY "A11" ASC LIMIT 1) ORDER BY "T1"."birth_date" DESC NULLS LAST LIMIT 1) 

**3. Simplification and Optimization:**

* The final SQL query from step 2 can be simplified and optimized. The nested queries can be combined using a single "INNER JOIN" and the filtering can be done within a single "ORDER BY" clause.

**Final Optimized SQL Query:**

<FINAL_ANSWER>
SELECT T1."gender"
  FROM client AS T1
  INNER JOIN district AS T2
  ON T1."district_id" = T2."district_id"
  ORDER BY T2."A11" ASC, T1."birth_date" DESC NULLS LAST
  LIMIT 1
</FINAL_ANSWER>

===========
Example 2 (dividing into two parallel sub-questions)
**************************
【Schema】
Table: games
[
(id:INTEGER, Primary Key, the unique identifier for the game),
(games_year:INTEGER, the year of the game)
]

Table: games_city
[
(games_id:INTEGER, the id of the game, Maps to games(id)),
(city_id:INTEGER, the id of the city that held the game, Maps to city(id))
]

Table: city
[
(id:INTEGER, Primary Key, the unique identifier for the city),
(city_name:TEXT, the name of the city, Examples: [London])
]

【Foreign keys】
games_city.city_id = city.id
games_city.games_id = games.id

**************************
【Question】
Question:
From 1900 to 1992, how many games did London host?

Hint:
From 1900 to 1992 refers to games_year BETWEEN 1900 AND 1992; London refers to city_name = 'London'; games refer to games_name;

**************************
【Answer】

Repeating the question and hint, and generating the SQL with Recursive Divide-and-Conquer.
**Question**: From 1900 to 1992, how many games did London host?
**Hint**: From 1900 to 1992 refers to games_year BETWEEN 1900 AND 1992; London refers to city_name = 'London'; games refer to games_name;

**1. Divide and Conquer:**

* **Main Question:** From 1900 to 1992, how many games did London host?
    * **Analysis:** The question requires us to count games, which are represented by the "id" column in the "games" table.  We need to filter these games based on TWO criteria: they were hosted in London and occurred between 1900 and 1992.
    * **Pseudo SQL:** SELECT COUNT("T1"."id") FROM "games" AS "T1"  WHERE  <games are in London> AND <games year between 1900 and 1992>

    * **Sub-question 1:** games are in London 
        * **Analysis:**  To determine which games were hosted in London, we need to join the "games" table with the "games_city" table on "games_id" and then join with the "city" table on "city_id". We'll use "INNER JOIN" to ensure only matching records are considered.  The filtering on 'London' will be applied to the "city_name" column.
        * **Pseudo SQL:**  "T1"."id" IN (SELECT "T1"."games_id" FROM "games_city" AS "T1" INNER JOIN "city" AS "T2" ON "T1"."city_id" = "T2"."id" WHERE "T2"."city_name" = 'London')

    * **Sub-question 2:** games year between 1900 and 1992
        * **Analysis:** This involves filtering the "games" table directly based on the "games_year" column using the "BETWEEN" operator.
        * **Pseudo SQL:** "T1"."games_year" BETWEEN 1900 AND 1992

**2. Assembling SQL:**

* **Sub-question 1 (games are in London):**
    * **SQL:**  "T1"."id" IN (SELECT "T1"."games_id" FROM "games_city" AS "T1" INNER JOIN "city" AS "T2" ON "T1"."city_id" = "T2"."id" WHERE "T2"."city_name" = 'London')

* **Sub-question 2 (games year between 1900 and 1992):**
    * **SQL:**  "T1"."games_year" BETWEEN 1900 AND 1992

* **Main Question (count of games):**
    * **SQL:** SELECT COUNT("T1"."id") FROM "games" AS "T1" WHERE "T1"."id" IN (SELECT "T1"."games_id" FROM "games_city" AS "T1" INNER JOIN "city" AS "T2" ON "T1"."city_id" = "T2"."id" WHERE "T2"."city_name" = 'London') AND "T1"."games_year" BETWEEN 1900 AND 1992

**3. Simplification and Optimization:**

* The nested query can be converted into a more efficient "JOIN" operation. We'll use "INNER JOIN" to combine "games", "games_city", and "city" based on the relationships between them.

**Final Optimized SQL Query:**

<FINAL_ANSWER>
SELECT COUNT(T3."id") FROM games_city AS T1 INNER JOIN city AS T2 ON T1."city_id" = T2."id" INNER JOIN games AS T3 ON T1."games_id" = T3."id" WHERE T2."city_name" = 'London' AND T3."games_year" BETWEEN 1900 AND 1992
</FINAL_ANSWER> 

Now is the real question, following the instruction and examples, generate the SQL with Recursive Divide-and-Conquer approach. Make sure you only output one single query.
**************************
【Table creation statements】
{DATABASE_SCHEMA}

**************************
【Question】
Question: 
{QUESTION}

Evidence:
{HINT}

**************************
【Answer】
Repeating the question and hint, and generating the SQL with Recursive Divide-and-Conquer.
"""


PROMPT = """
You are a SQLite expert. You need to read and understand the following database schema description, as well as the evidence that may be used,
 and use your SQLite knowledge to generate SQL statements to answer user questions.

The following examples are for your reference.

=========
Example 1 

[DB_ID] retalis 

[Schema]

Table: generalinfo
[
(id_restaurant:INTEGER, Primary Key, the unique identifier for the restaurant),
(food_type:TEXT, the food type, Examples: [thai, italian, mexican]),
(city:TEXT, the city where the restaurant is located in)
]

Table: location
[
(id_restaurant:INTEGER, Primary Key, the id of the restaurant, Maps to generalinfo(id_restaurant)),
(street_name:TEXT, the street name of the restaurant, Examples: [ave, san pablo ave, pablo ave]),
(city:TEXT, the city where the restaurant is located in)
]

【Foreign keys】
location.id_restaurant = generalinfo.id_restaurant

【Question】
How many Thai restaurants can be found in San Pablo Ave, Albany? 

【Evidence】
Thai restaurant refers to food_type = 'thai'; San Pablo Ave Albany refers to street_name = 'san pablo ave' AND T1.city = 'albany'

```sql
SELECT COUNT(T1."id_restaurant") FROM generalinfo AS T1 INNER JOIN location AS T2 ON T1."id_restaurant" = T2."id_restaurant" WHERE T1."food_type" = 'thai' AND T1."city" = 'albany' AND T2."street_name" = 'san pablo ave'
```
===========
Example 2
**************************
【Schema】

Table: account
[
(account_id:INT, Primary Key, the unique identifier for the account),
(district_id:INT, the id of the district, Maps to district(district_id)),
(frequency:VARCHAR(255), the frequency of issuance of statements),
(date:DATE, the date of creation of the account)
]

Table: client
[
(client_id:INT, Primary Key, the unique identifier for the client),
(gender:CHAR(1), the gender of the client, Examples: [M, F]),
(birth_date:DATE, the birth date of the client),
(district_id:INT, the id of the district, Maps to district(district_id))
]

Table: district
[
(district_id:INT, Primary Key, the unique identifier for the district),
(a4:VARCHAR(255), number of inhabitants in the district),
(a11:VARCHAR(255), average salary in the district)
]

【Foreign keys】
account.district_id = district.district_id
client.district_id = district.district_id

【Question】
Question: What is the gender of the youngest client who opened account in the lowest average salary branch?

【Evidence】
 Given that Later birthdate refers to younger age; A11 refers to average salary

```sql
SELECT T1."gender"
  FROM client AS T1
  INNER JOIN district AS T2
  ON T1."district_id" = T2."district_id"
  ORDER BY T2."A11" ASC, T1."birth_date" DESC NULLS LAST
  LIMIT 1
```
===========
Example 3 (dividing into two parallel sub-questions)

【Schema】
Table: games
[
(id:INTEGER, Primary Key, the unique identifier for the game),
(games_year:INTEGER, the year of the game)
]

Table: games_city
[
(games_id:INTEGER, the id of the game, Maps to games(id)),
(city_id:INTEGER, the id of the city that held the game, Maps to city(id))
]

Table: city
[
(id:INTEGER, Primary Key, the unique identifier for the city),
(city_name:TEXT, the name of the city, Examples: [London])
]

【Foreign keys】
games_city.city_id = city.id
games_city.games_id = games.id

【Question】
From 1900 to 1992, how many games did London host?

【Evidence】
From 1900 to 1992 refers to games_year BETWEEN 1900 AND 1992; London refers to city_name = 'London'; games refer to games_name;

```sql
SELECT COUNT(T3."id") FROM games_city AS T1 INNER JOIN city AS T2 ON T1."city_id" = T2."id" INNER JOIN games AS T3 ON T1."games_id" = T3."id" WHERE T2."city_name" = 'London' AND T3."games_year" BETWEEN 1900 AND 1992
```
===========
Example 4 (When it's not clear which column should be used for a string matching, use a loosen condition such as string LIKE and OR condition to cover multiple possible columns.)

【Table creation statements】
【Schema】

Table: student_programs
[
(Program Type:TEXT, Program Type, Examples: ['Summer School', 'After School Program', 'Special Education']),
(Participants (Ages 10-15):DOUBLE, Participants (Ages 10-15), Examples: [1250.0, 500.0, 75.0]),
(Total Enrollment (Ages 10-15):DOUBLE, Total Enrollment (Ages 10-15), Examples: [500.0, 1800.0, 1000.0]),
(School Category:TEXT, School Category, Examples: ['Charter Schools', 'Private Schools', 'Magnet Schools'])
]

【Question】
Question: Please list the lowest three participation rates for students aged 10-15 in online programs. 

【Evidence】
 Participation rate for students aged 10-15 = `Participants (Ages 10-15)` / `Total Enrollment (Ages 10-15)`

```sql
SELECT "Participants (Ages 10-15)" / "Total Enrollment (Ag"es 10-15)" FROM "student_programs"
  WHERE LOWER("School Category") LIKE '%online%' OR LOWER("Program Type") LIKE '%online%'
  AND "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" IS NOT NULL 
  ORDER BY "Participants (Ages 10-15)" / "Total Enrollment (Ages 10-15)" ASC NULLS LAST LIMIT 3;
```
=============
Example 5

【Schema】
Table: employees
[
(employee_id:INTEGER, Primary Key, the unique identifier of the employee, Examples: [100, 101, 102]),
(department_id:INTEGER, the id of the department the employee belongs to, Examples: [10, 20, 30]),
(salary:INTEGER, the salary of the employee, Examples: [50000, 75000, 90000])
]
**************************
【Question】
Question: How many employees earn over $100,000?

```sql
SELECT COUNT(*) FROM employees WHERE "salary" > 100000;
```

====== Example 6 =======
【DB_ID】 airline
【Schema】
Table: Airlines
[
(FL_DATE:TEXT, flight date, Examples: [2018-08-09, 2018-01-01, 2019-02-15]),
(ORIGIN:TEXT, airport of origin Maps to Airports(Code), Examples: [SAN, JFK, LAX]),
(DEST:TEXT, Destination airport Maps to Airports(Code), Examples: [JFK, LAX, SFO])
]
Table: Airports
[
(Code:TEXT, Primary Key, the unique code of the airport, Examples: [SAN, JFK, LAX]),
(Description:TEXT, the full name or description of the airport, Examples: [San Diego International Airport, John F. Kennedy International Airport, Los Angeles International Airport])
]
【Foreign keys】
Airlines.ORIGIN = Airports.Code
Airlines.DEST = Airports.Code

【Question】
How many flights were there from San Diego International airport to Los Angeles International airport in the August of 2018? 

【Evidence】
flights from refers to ORIGIN; San Diego International airport refers to Description = 'San Diego, CA: San Diego International'; flights to refers to DEST; Los Angeles International airport refers to Description = 'Los Angeles, CA: Los Angeles International'; in the August of 2018 refers to FL_DATE like '2018/8%';

```sql
SELECT COUNT(FL_DATE) FROM Airlines WHERE FL_DATE LIKE '2018/8%' AND ORIGIN = ( SELECT T2.ORIGIN FROM Airports AS T1 INNER JOIN Airlines AS T2 ON T1.Code = T2.ORIGIN WHERE T1.Description = 'San Diego, CA: San Diego International' ) AND DEST = ( SELECT T4.DEST FROM Airports AS T3 INNER JOIN Airlines AS T4 ON T3.Code = T4.DEST WHERE T3.Description = 'Los Angeles, CA: Los Angeles International' )
```

===== Example 6 ========
【DB_ID】 eatery_inspection
【Schema】
Table: businesses
[
(business_id:INTEGER, Primary Key, the unique identifier for the business, Examples: [10, 100, 1000]),
(name:TEXT, the name of the eatery, Examples: [ACME, STARBUCKS, MCDONALDS])
]
Table: inspections
[
(business_id:INTEGER, the unique id of the business Maps to businesses(business_id), Examples: [10, 100, 1000]),
(score:INTEGER, the inspection score, Examples: [90, 95, 100]),
(date:TEXT, the date of the inspection, Examples: [2014-01-24, 2015-08-11, 2017-03-09])
]
Table: violations
[
(business_id:INTEGER, the unique id of the business Maps to businesses(business_id), Examples: [10, 100, 1000]),
(date:TEXT, the date of the violation, Examples: [2016-05-03, 2014-01-24, 2015-02-18])
]
【Foreign keys】
inspections.business_id = businesses.business_id
violations.business_id = businesses.business_id

【Question】
What are the names of the establishments that met all the required standards for 4 consecutive years? 

【Evidence】:
establishment has the same meaning as business; score of 90 or more refers to score ≥ 90; year(date) = 2015; ; met all required standards for 4 consecutive years refers to COUNT(year(date)) = 4 where score = 100;

```sql
SELECT DISTINCT T4."name" FROM ( SELECT T3."name", T3."years", row_number() OVER (PARTITION BY T3."name" ORDER BY T3."years") AS rowNumber FROM ( SELECT DISTINCT "name", STRFTIME('%Y', "date") AS years FROM inspections AS T1 INNER JOIN businesses AS T2 ON T1."business_id" = T2."business_id" WHERE T1."score" = 100 ) AS T3 ) AS T4 GROUP BY T4."name", date(T4."years" || '-01-01', '-' || (T4."rowNumber" - 1) || ' years') HAVING COUNT(T4."years") = 4
```

Now is the real question:

【User Question】
{QUESTION}

【Database Schema】
{DATABASE_SCHEMA}

【Evidence】
{HINT}

【Rules】
- Always use double quotes for column names in the constructed query(E.g T1."column_name")
- Do not ABSOLUTELY use any column name inside the query that does not appear in the provided schema. Only answer using the column names in the schema.

Wrap the resulting SQL in 
```sql
```
"""

OMNI_PROMPT = """
'''Task Overview:
You are a data science expert. Below, you are provided with a database schema and a natural language question. Your task is to understand the schema and generate a valid SQL query to answer the question.

Database Engine:
SQLite

Database Schema:
{DATABASE_SCHEMA}

This schema describes the database's structure, including tables, columns, primary keys, foreign keys, and any relevant relationships or constraints.

Question:
{QUESTION}

Hint:
{HINT}

Instructions:
- Make sure you only output the information that is asked in the question. If the question asks for a specific column, make sure to only include that column in the SELECT clause, nothing more.
- The generated query should return all of the information asked in the question without any missing or extra information.
- Before generating the final SQL query, please think through the steps of how to write the query.
- Always use double quotes for column names in the constructed query(E.g Given a column with name "Column Name" use SELECT T1."Column Name")
- Do not ABSOLUTELY use any column name inside the query that does not appear in the provided schema. Only answer using the column names in the schema.

Output Format:
In your answer, please enclose the generated SQL query in a code block:
```sql
-- Your SQL query
```

Take a deep breath and think step by step to find the correct SQL query.'''
"""

DEFOG_PROMPT="""
### Task
Generate a SQL query to answer [QUESTION]{QUESTION}[/QUESTION]

Database Engine:
SQLite

### Instructions
- If you cannot answer the question with the available database schema, return 'I do not know'
- The resulting SQL must be wrapped in ```<generated-sql>```
- Always use double quotes for column names in the constructed query(E.g Given a column with name "Column Name" use SELECT T1."Column Name")
- Do not ABSOLUTELY use any column name inside the query that does not appear in the provided schema. Only answer using the column names in the schema.

### Database Schema
The query will run on a database with the following schema:
{DATABASE_SCHEMA}

### Answer
Given the database schema, here is the SQL query that answers [QUESTION]{QUESTION}[/QUESTION]
```
[SQL]
```
"""