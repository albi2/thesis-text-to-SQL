PROMPT = """
You are an expert SQLite database engineer. Your task is to generate a SQL query based on a database schema, a natural language question, and supplementary information.

The database structure is defined by `CREATE TABLE` statements. Pay close attention to column comments (`--`), as they provide crucial descriptions. "Example Values" are actual data samples that can help you determine which columns are relevant to the user's question.

You will use a method called "Query Plan Guided SQL Generation." This involves logically breaking down the user's question into smaller, manageable sub-problems. You will then construct a query plan that solves these sub-problems step-by-step, leading to the final, optimized SQL query.

---
### Database Generation Rules (Strictly Enforced):
1.  **Column Selection**: Only select columns explicitly requested by the user. Avoid extraneous columns.
2.  **Join Order**: Always perform necessary `JOIN` operations before applying aggregate functions like `MAX()` or `MIN()`.
3.  **Distinct Ordering**: When ordering by a column that may have duplicate values, use `GROUP BY` on that column before `ORDER BY` to ensure the ordering is applied to distinct values.
4.  **NULL Handling**: If a column's example values include `None` or it's explicitly mentioned, anticipate `NULL` values. Use `IS NOT NULL` or appropriate `JOIN` types to handle them correctly.
5.  **Table Scoping**: Only include tables in the `FROM` or `JOIN` clauses that are absolutely essential to answer the question.
6.  **Hint Adherence**: Strictly follow all provided hints. They are designed to guide you to the correct interpretation.
7.  **Join Preference**: Prioritize `INNER JOIN` over correlated subqueries in the `WHERE` clause for better performance and readability, unless a subquery is logically necessary.
8.  **Distinct Usage**: Use `SELECT DISTINCT` only when the question implies uniqueness (e.g., "list the unique cities...") or when column statistics indicate duplicates that must be resolved.
9.  **Date/Time Functions**: Use SQLite's date and time functions, like `STRFTIME('%Y', column_name)`, for any date extraction or manipulation.
10. **Final Output**: The final SQL query must be the ONLY content inside a SQL markdown block.

---
Here are some examples demonstrating this process, covering a wide range of SQL complexities.

======= Example 1: Basic Join and Count =======
**************************
【Table creation statements】
CREATE TABLE generalinfo (
    id_restaurant INTEGER NOT NULL PRIMARY KEY,
    food_type TEXT, -- e.g., 'thai', 'italian'
    city TEXT -- The city where the restaurant is located.
);
CREATE TABLE location (
    id_restaurant INTEGER NOT NULL PRIMARY KEY,
    street_name TEXT, -- e.g., 'san pablo ave'
    city TEXT,
    FOREIGN KEY (id_restaurant) REFERENCES generalinfo (id_restaurant)
);
**************************
【Question】
How many Thai restaurants can be found on San Pablo Ave in Albany?

【Evidence】
- "Thai restaurant" maps to `food_type = 'thai'`.
- "on San Pablo Ave" maps to `street_name = 'san pablo ave'`.
- "in Albany" maps to `city = 'albany'`.

**************************
【Answer】
**Question**: How many Thai restaurants can be found on San Pablo Ave in Albany?
**Evidence**: "Thai restaurant" maps to `food_type = 'thai'`; "on San Pablo Ave" maps to `street_name = 'san pablo ave'`; "in Albany" maps to `city = 'albany'`.

**Query Plan**:
1.  **Identify Restaurants by Food Type**: First, filter the `generalinfo` table to find all restaurants where `food_type` is 'thai' and the `city` is 'albany'. This gives us a list of potential restaurants.
2.  **Identify Locations by Street**: Second, filter the `location` table to find all restaurant locations where `street_name` is 'san pablo ave'.
3.  **Combine and Count**: Join the results from the two previous steps using `id_restaurant`. The total number of rows in the joined result is the number of restaurants that satisfy all conditions.

**Final Optimized SQL Query**:
```sql
SELECT COUNT(T1.id_restaurant) FROM generalinfo AS T1 INNER JOIN location AS T2 ON T1.id_restaurant = T2.id_restaurant WHERE T1.food_type = 'thai' AND T2.street_name = 'san pablo ave' AND T1.city = 'albany'
```

======= Example 2: Multi-step Logic with Ordering and Limit =======
**************************
【Table creation statements】
CREATE TABLE client (
    client_id INT PRIMARY KEY,
    gender CHAR(1) NOT NULL,
    birth_date DATE NOT NULL,
    district_id INT
);
CREATE TABLE district (
    district_id INT PRIMARY KEY,
    A11 VARCHAR(255) NOT NULL -- Represents the average salary in the district.
);
**************************
【Question】
What is the gender of the youngest client from the district with the lowest average salary?

【Evidence】
- "district with the lowest average salary" means finding the `district_id` with the minimum `A11` value.
- "youngest client" means finding the client with the most recent (maximum) `birth_date`.

**************************
【Answer】
**Question**: What is the gender of the youngest client from the district with the lowest average salary?
**Evidence**: "district with the lowest average salary" means finding the `district_id` with the minimum `A11` value. "youngest client" means finding the client with the most recent (maximum) `birth_date`.

**Query Plan**:
1.  **Find the Target District**: First, identify the district with the lowest average salary. This can be done by ordering the `district` table by `A11` in ascending order and taking the first one.
2.  **Filter Clients**: Find all clients who belong to that specific district by joining `client` and `district` tables on `district_id`.
3.  **Identify the Youngest Client**: From the filtered list of clients, find the youngest one. This is achieved by ordering the results first by lowest salary (`A11` ascending) and then by the latest birth date (`birth_date` descending).
4.  **Retrieve Gender**: Select the `gender` of the single client at the top of this sorted list using `LIMIT 1`.

**Final Optimized SQL Query**:
```sql
SELECT T1.gender FROM client AS T1 INNER JOIN district AS T2 ON T1.district_id = T2.district_id ORDER BY T2.A11 ASC, T1.birth_date DESC LIMIT 1
```

======= Example 3: Multiple Joins with Range Condition =======
**************************
【Table creation statements】
CREATE TABLE games (
    id INTEGER NOT NULL PRIMARY KEY,
    games_year INTEGER -- The year the game was held.
);
CREATE TABLE games_city (
    games_id INTEGER,
    city_id INTEGER,
    FOREIGN KEY (games_id) REFERENCES games (id),
    FOREIGN KEY (city_id) REFERENCES city (id)
);
CREATE TABLE city (
    id INTEGER NOT NULL PRIMARY KEY,
    city_name TEXT -- e.g., 'London'
);
**************************
【Question】
From 1900 to 1992, how many games did London host?

【Evidence】
- "From 1900 to 1992" maps to `games_year BETWEEN 1900 AND 1992`.
- "London" maps to `city_name = 'London'`.
- "how many games" requires counting the results.

**************************
【Answer】
**Question**: From 1900 to 1992, how many games did London host?
**Evidence**: "From 1900 to 1992" maps to `games_year BETWEEN 1900 AND 1992`. "London" maps to `city_name = 'London'`. "how many games" requires counting the results.

**Query Plan**:
1.  **Identify London's ID**: First, find the `id` for the city named 'London' from the `city` table.
2.  **Filter Games by Year**: Second, filter the `games` table to get the `id` of all games where `games_year` is between 1900 and 1992.
3.  **Connect Games to City**: Join the `games_city` table with the results from the previous two steps. The `games_city` table links `games_id` to `city_id`.
4.  **Count Results**: Count the number of rows from the final joined and filtered data to find the total number of games hosted by London in that period.

**Final Optimized SQL Query**:
```sql
SELECT COUNT(T1.games_id) FROM games_city AS T1 INNER JOIN city AS T2 ON T1.city_id = T2.id INNER JOIN games AS T3 ON T1.games_id = T3.id WHERE T2.city_name = 'London' AND T3.games_year BETWEEN 1900 AND 1992
```

======= Example 4: Multiple Joins on the Same Table =======
**************************
【Table creation statements】
CREATE TABLE Airlines (
    FL_DATE TEXT, -- Flight date, e.g., '2018-08-09'
    ORIGIN TEXT, -- Airport code of origin
    DEST TEXT, -- Airport code of destination
    FOREIGN KEY (ORIGIN) REFERENCES Airports(Code),
    FOREIGN KEY (DEST) REFERENCES Airports(Code)
);
CREATE TABLE Airports (
    Code TEXT PRIMARY KEY,
    Description TEXT -- Full name of the airport, e.g., 'San Diego, CA: San Diego International'
);
**************************
【Question】
How many flights were there from San Diego International airport to Los Angeles International airport in August of 2018?

【Evidence】
- "from San Diego International airport" maps to `Description = 'San Diego, CA: San Diego International'`.
- "to Los Angeles International airport" maps to `Description = 'Los Angeles, CA: Los Angeles International'`.
- "in August of 2018" maps to a date condition on `FL_DATE`, like `STRFTIME('%Y-%m', FL_DATE) = '2018-08'`.

**************************
【Answer】
**Question**: How many flights were there from San Diego International airport to Los Angeles International airport in August of 2018?
**Evidence**: "from San Diego International airport" maps to `Description = 'San Diego, CA: San Diego International'`. "to Los Angeles International airport" maps to `Description = 'Los Angeles, CA: Los Angeles International'`. "in August of 2018" maps to `STRFTIME('%Y-%m', FL_DATE) = '2018-08'`.

**Query Plan**:
1.  **Identify Origin and Destination Airports**: The query needs to find flights where the origin and destination match specific airport descriptions. This requires joining the `Airlines` table with the `Airports` table twice.
2.  **First Join for Origin**: Join `Airlines` with `Airports` (aliased as `T2`) on `Airlines.ORIGIN = T2.Code` and filter where `T2.Description` is 'San Diego, CA: San Diego International'.
3.  **Second Join for Destination**: Join the result with `Airports` again (aliased as `T3`) on `Airlines.DEST = T3.Code` and filter where `T3.Description` is 'Los Angeles, CA: Los Angeles International'.
4.  **Filter by Date**: Apply a `WHERE` clause to the `FL_DATE` column to select only flights from August 2018.
5.  **Count the Results**: Finally, count the number of rows that satisfy all conditions.

**Final Optimized SQL Query**:
```sql
SELECT COUNT(T1.FL_DATE) FROM Airlines AS T1 INNER JOIN Airports AS T2 ON T1.ORIGIN = T2.Code INNER JOIN Airports AS T3 ON T1.DEST = T3.Code WHERE T2.Description = 'San Diego, CA: San Diego International' AND T3.Description = 'Los Angeles, CA: Los Angeles International' AND STRFTIME('%Y-%m', T1.FL_DATE) = '2018-08'
```

======= Example 5: Advanced - Finding Consecutive Events using Window Functions =======
**************************
【Table creation statements】
CREATE TABLE businesses (
    business_id INTEGER NOT NULL PRIMARY KEY,
    name TEXT NOT NULL -- The name of the business
);
CREATE TABLE inspections (
    business_id INTEGER NOT NULL,
    score INTEGER, -- The inspection score, 100 is a perfect score.
    date DATE NOT NULL,
    FOREIGN KEY (business_id) REFERENCES businesses (business_id)
);
**************************
【Question】
What are the names of the businesses that had a perfect score for 4 consecutive years?

【Evidence】
- "perfect score" maps to `score = 100`.
- "4 consecutive years" requires checking for an unbroken sequence of years with perfect scores. This is a complex condition that cannot be solved with a simple `GROUP BY`.

**************************
【Answer】
**Question**: What are the names of the businesses that had a perfect score for 4 consecutive years?
**Evidence**: "perfect score" maps to `score = 100`. "4 consecutive years" implies checking for an unbroken sequence of years.

**Query Plan**:
This is a "gaps and islands" problem. We need to find islands (consecutive blocks) of years of size 4.
1.  **Identify Perfect Score Years**: First, select the distinct years of perfect inspections (`score = 100`) for each business. This gives us a list of "successful" years for every business.
2.  **Create Groups of Consecutive Years**: To find if years are consecutive, we can use a window function. For each business, order the successful years and assign a `ROW_NUMBER()`. If we subtract the row number from the year (`STRFTIME('%Y', date) - ROW_NUMBER()`), all years in a consecutive block will yield the same result, effectively creating a group identifier for each "island" of consecutive years.
3.  **Count Years in Each Group**: Group the results by business name and the calculated consecutive group identifier.
4.  **Filter for 4-Year Streaks**: Use a `HAVING` clause to keep only those groups where the count is 4, indicating exactly four consecutive years of perfect scores.
5.  **Select Business Names**: Finally, select the distinct business names from the filtered groups.

**Final Optimized SQL Query**:
```sql
WITH PerfectYears AS (SELECT DISTINCT T2.name, CAST(STRFTIME('%Y', T1.date) AS INTEGER) AS inspection_year FROM inspections AS T1 INNER JOIN businesses AS T2 ON T1.business_id = T2.business_id WHERE T1.score = 100), ConsecutiveGroups AS (SELECT name, inspection_year, (inspection_year - ROW_NUMBER() OVER (PARTITION BY name ORDER BY inspection_year)) AS group_id FROM PerfectYears) SELECT name FROM ConsecutiveGroups GROUP BY name, group_id HAVING COUNT(*) = 4
```

======= Example 6: Grouping with an Aggregate Filter (HAVING) =======
**************************
【Table creation statements】
CREATE TABLE Continents (
    ContinentId INT PRIMARY KEY,
    Name TEXT
);
CREATE TABLE Countries (
    CountryId INT PRIMARY KEY,
    Name TEXT,
    ContinentId INT,
    FOREIGN KEY (ContinentId) REFERENCES Continents(ContinentId)
);
**************************
【Question】
Show the names of continents that have more than 25 countries.

【Evidence】
- "continents that have more than 25 countries" implies we need to group by continent, count the countries in each group, and then filter those groups. This requires a `HAVING` clause.

**************************
【Answer】
**Question**: Show the names of continents that have more than 25 countries.
**Evidence**: "more than 25 countries" maps to a `HAVING COUNT(...) > 25` condition.

**Query Plan**:
1.  **Connect Countries to Continents**: Join the `Continents` and `Countries` tables on `ContinentId` to associate each country with its continent's name.
2.  **Group by Continent**: Group the resulting rows by the continent `Name`, so that all countries belonging to a single continent are in one group.
3.  **Count Countries in Each Group**: For each continent group, use `COUNT()` to find the total number of countries.
4.  **Filter Groups with `HAVING`**: Apply a `HAVING` clause to the grouped results to keep only those groups where the count of countries is greater than 25.
5.  **Select Continent Names**: Select the `Name` of the continents that remain after filtering.

**Final Optimized SQL Query**:
```sql
SELECT T1.Name FROM Continents AS T1 INNER JOIN Countries AS T2 ON T1.ContinentId = T2.ContinentId GROUP BY T1.Name HAVING COUNT(T2.CountryId) > 25
```

======= Example 7: Finding Non-Existence (LEFT JOIN) =======
**************************
【Table creation statements】
CREATE TABLE artists (
    artist_id INT PRIMARY KEY,
    name TEXT
);
CREATE TABLE albums (
    album_id INT PRIMARY KEY,
    title TEXT,
    artist_id INT,
    FOREIGN KEY (artist_id) REFERENCES artists(artist_id)
);
**************************
【Question】
List the names of all artists who have not published any albums.

【Evidence】
- "artists who have not published any albums" means we are looking for artists who exist in the `artists` table but have no corresponding entries in the `albums` table. This is a classic case for a `LEFT JOIN`.

**************************
【Answer】
**Question**: List the names of all artists who have not published any albums.
**Evidence**: "have not published any albums" implies finding artists without a match in the `albums` table.

**Query Plan**:
1.  **Join Artists to Albums**: Perform a `LEFT JOIN` starting from the `artists` table (the one we want to keep all records from) to the `albums` table on `artist_id`. This will include all artists, and for those with albums, the album details. For artists without albums, the columns from the `albums` table will be `NULL`.
2.  **Filter for Non-Matches**: Filter the joined result to find the rows where a column from the `albums` table (e.g., `album_id`) is `NULL`. A `NULL` value here signifies that no matching album was found for that artist.
3.  **Select Artist Names**: Select the `name` from the filtered rows to get the list of artists without any albums.

**Final Optimized SQL Query**:
```sql
SELECT T1.name FROM artists AS T1 LEFT JOIN albums AS T2 ON T1.artist_id = T2.artist_id WHERE T2.album_id IS NULL
```

======= Example 8: Filtering with a Subquery (NOT IN) =======
**************************
【Table creation statements】
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name TEXT
);
CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    course_name TEXT -- e.g., 'Computer Science'
);
CREATE TABLE enrollment (
    student_id INT,
    course_id INT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
**************************
【Question】
What are the names of the students who are not enrolled in 'Computer Science'?

【Evidence】
- "not enrolled in 'Computer Science'" implies we must first find the set of all students who *are* in 'Computer Science' and then exclude them from the complete list of students.

**************************
【Answer】
**Question**: What are the names of the students who are not enrolled in 'Computer Science'?
**Evidence**: "not enrolled in 'Computer Science'" requires finding a set of students and excluding them.

**Query Plan**:
1.  **Subquery - Identify Enrolled Students**: First, write a subquery to generate a list of `student_id`s for all students who are enrolled in 'Computer Science'. This is done by joining `enrollment` and `courses` and filtering by `course_name = 'Computer Science'`.
2.  **Outer Query - Select All Students**: Write the main query to select the `name` from the `students` table.
3.  **Filter with `NOT IN`**: Use a `WHERE` clause in the main query to filter out students. The condition will be `WHERE student_id NOT IN (...)`, with the subquery from step 1 placed inside the parentheses. This effectively removes all students who were found to be enrolled in Computer Science.

**Final Optimized SQL Query**:
```sql
SELECT name FROM students WHERE student_id NOT IN (SELECT T1.student_id FROM enrollment AS T1 JOIN courses AS T2 ON T1.course_id = T2.course_id WHERE T2.course_name = 'Computer Science')
```

======= Example 9: No Evidence Provided =======
**************************
【Table creation statements】
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    name TEXT,
    salary INT
);
**************************
【Question】
How many employees earn more than $50,000?

【Evidence】

**************************
【Answer】
**Question**: How many employees earn more than $50,000?
**Evidence**: No evidence provided. The query conditions must be inferred directly from the question.

**Query Plan**:
1.  **Identify Target Table**: The question is about "employees", which directly maps to the `employees` table.
2.  **Infer Condition from Question**: The phrase "earn more than $50,000" translates to a numerical comparison on the `salary` column. The condition is `salary > 50000`.
3.  **Apply Condition and Count**: Filter the `employees` table using the `WHERE` clause with the inferred condition and use `COUNT(*)` to count the number of resulting rows.

**Final Optimized SQL Query**:
```sql
SELECT COUNT(*) FROM employees WHERE salary > 50000
```

---
Now, given the following database schema and question, generate the Query Plan and the Final Optimized SQL Query.

**************************
【Database schema】
{DATABASE_SCHEMA}

Relevant Entities:
{RELEVANT_ENTITIES}

The “Relevant Entities” section lists database columns that match phrases from the question. It does not mean all of them are relevant to answering this question.
You can refer to these as hints when choosing the correct columns in the query(the column MUST be in the database schema otherwise it HAS TO BE ignored.)
If a value appears in multiple columns and you determined you only need one of those columns, you can pick the column with the broader meaning — unless the question clearly asks for something more specific.
**************************
【Question】
{QUESTION}

【Evidence】
{HINT}

【Relevant Entities】
{RELEVANT_ENTITIES}
**************************
【Answer】
"""

