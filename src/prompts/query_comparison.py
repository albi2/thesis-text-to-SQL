QUERY_COMPARISON_PROMPT = """
You are an expert in text-to-SQL. Your task is to compare two SQL queries based on a given question, database schema, and hint, and determine which one is better.

**Instructions:**
1.  Carefully analyze the question, schema, evaluation criteria and hint.
2.  Evaluate both queries based on correctness, relevance, and efficiency.
3.  The query that better answers the question is the winner.
4.  Provide a step-by-step reasoning for your choice.
5.  Provide the output in the format `reasoning: [your reasoning] winner: [1 or 2]`.

Here are some examples:
---
**Example 1**

**Question**: "Find the names of all students who are enrolled in the 'Computer Science' course."

**Schema:**
CREATE TABLE students (
  student_id INT PRIMARY KEY,
  student_name VARCHAR(255)
);
CREATE TABLE courses (
  course_id INT PRIMARY KEY,
  course_name VARCHAR(255)
);
CREATE TABLE enrollments (
  student_id INT,
  course_id INT
);

**Hint:** 

**Evaluation Criteria:** 
1. Output Requirements:
   - Must return a list of student names.

2. Mandatory Filters/Conditions:
   - MUST filter for the course_name being 'Computer Science'.

3. Required Operations:
   - Must JOIN students, enrollments, and courses tables to link students to course names.

4. Completeness Checks:
   - Addresses "who" by selecting student name.
   - Addresses "which course" by filtering on course name.

5. Correctness Checks:
   - Results must be filtered based on the course 'Computer Science;

**Query 1:**
```sql
SELECT T1.student_name
FROM students AS T1
JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id
```

**Query 2:**
```sql
SELECT T1.student_name
FROM students AS T1
JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id
JOIN courses AS T3 ON T2.course_id  =  T3.course_id
WHERE T3.course_name  =  'Computer Science'
```

**Output:**
reasoning: Query 1 only joins the students and enrollments tables, so it finds all students who are in *any* course, but it fails to filter for the 'Computer Science' course specifically. Query 2 correctly joins all three tables and includes the necessary WHERE clause to filter by the course name. Therefore, Query 2 is the only one that completely and correctly answers the question. winner: 2

---
**Example 2**

**Question**: "List the unique names of singers who have a song with a duration of more than 400."

**Schema:**
CREATE TABLE singer (
  Singer_ID INT PRIMARY KEY,
  Name VARCHAR(255)
);
CREATE TABLE song (
  Song_ID INT PRIMARY KEY,
  Title VARCHAR(255),
  Singer_ID INT,
  Duration INT
);

**Hint:** "Duration more than 400 means song.Duration > 400"

**Evaluation Criteria:** 
1. Output Requirements:
   - Must return a list of singer names.
   - The list must not contain duplicate names.

2. Mandatory Filters/Conditions:
   - MUST filter for Duration > 400.

3. Required Operations:
   - JOIN singer and song tables.
   - Use DISTINCT to ensure unique names are returned.

4. Completeness Checks:
   - Addresses "unique names" -> DISTINCT keyword.
   - Addresses the condition "duration of more than 400" -> WHERE clause.

5. Correctness Checks:
   - Must use the '>' operator, not '=' or '<'.
   - Omitting DISTINCT is a flaw as it fails the "unique" requirement.
   - Must make sure duration more than 400

**Query 1:**
```sql
SELECT T1.Name
FROM singer AS T1
JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID
WHERE T2.Duration  >  400
```

**Query 2:**
```sql
SELECT DISTINCT T1.Name
FROM singer AS T1
JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID
WHERE T2.Duration  >  400
```

**Output:**
reasoning: Both queries correctly join the tables and filter for songs with a duration greater than 400. However, the question asks for the 'unique names'. If a singer has two or more songs that fit the criteria, Query 1 will list their name for each song, resulting in duplicates. Query 2 correctly uses the DISTINCT keyword to ensure that each singer's name appears only once in the final result. Query 2 is better because it adheres to the uniqueness requirement. winner: 2
---
**Example 3**

**Question**: "For each department, find the employee with the highest salary."

**Schema:**
CREATE TABLE employees (
  EmployeeID INT PRIMARY KEY,
  Name VARCHAR(255),
  Salary DECIMAL(10, 2),
  DepartmentID INT
);
CREATE TABLE departments (
  DepartmentID INT PRIMARY KEY,
  DepartmentName VARCHAR(255)
);

**Hint:** "A window function is often more efficient than a correlated subquery for ranking within groups."

**Evaluation Criteria:** 
1. Output Requirements:
   - Must return department name, employee name, and his salary.

2. Mandatory Filters/Conditions:
   - No explicit filters, but must correctly identify the top salary record within each department group.

3. Required Operations:
   - Must connect employees and departments.
   - Must determine the MAX(Salary) for each department group.
   - Grouping based on department is needed


4. Completeness Checks:
   - Addresses "for each department" by grouping or partitioning by department.
   - Addresses "highest salary" by ranking or using a MAX subquery.
   - Returns all three requested columns.

5. Correctness Checks:
   - The logic must correctly handle ties for the highest salary. 
   - Only one result per department must be returned
   - Efficiency is a secondary criterion; a correct but less efficient query is better than an incorrect one, but a correct and efficient one is best.

**Query 1:**
```sql
WITH RankedEmployees AS (
  SELECT
    d.DepartmentName,
    e.Name,
    e.Salary,
    RANK() OVER(PARTITION BY e.DepartmentID ORDER BY e.Salary DESC) as rn
  FROM employees AS e
  JOIN departments AS d ON e.DepartmentID = d.DepartmentID
)
SELECT DepartmentName, Name, Salary FROM RankedEmployees WHERE rn = 1
```

**Query 2:**
```sql
SELECT
  d.DepartmentName,
  e.Name,
  e.Salary
FROM employees AS e
JOIN departments AS d ON e.DepartmentID = d.DepartmentID
WHERE e.Salary = (
  SELECT MAX(Salary)
  FROM employees AS e2
  WHERE e2.DepartmentID = e.DepartmentID
)
```

**Output:**
reasoning: Both queries correctly identify the employee(s) with the highest salary in each department. Query 1 uses a modern and generally more performant approach with a Common Table Expression (CTE) and the RANK() window function. This is highly readable and scalable. Query 2 uses a correlated subquery, which forces the subquery to be re-executed for every single row in the outer query's result set. While correct, this is often less efficient on large datasets. Therefore, Query 1 is the better choice for its performance and readability. winner: 1

---
**Example 4**

**Question**: "What is the total sales revenue for each music genre for sales that occurred in the USA?"

**Schema:**
CREATE TABLE genres (
  GenreId INT PRIMARY KEY,
  Name VARCHAR(255)
);
CREATE TABLE tracks (
  TrackId INT PRIMARY KEY,
  GenreId INT,
  FOREIGN KEY (GenreId) REFERENCES genres(GenreId)
);
CREATE TABLE invoice_lines (
  InvoiceLineId INT PRIMARY KEY,
  InvoiceId INT,
  TrackId INT,
  UnitPrice DECIMAL(10, 2),
  Quantity INT,
  FOREIGN KEY (TrackId) REFERENCES tracks(TrackId),
  FOREIGN KEY (InvoiceId) REFERENCES invoices(InvoiceId)
);
CREATE TABLE invoices (
  InvoiceId INT PRIMARY KEY,
  BillingCountry VARCHAR(255)
);

**Hint:** "Total revenue for a line item is its UnitPrice multiplied by its Quantity."

**Evaluation Criteria:** 
1. Output Requirements:
   - Must return the genre name.
   - Must return a calculated field for total revenue.

2. Mandatory Filters/Conditions:
   - MUST filter invoices  sent to 'USA'.

3. Required Operations:
   - Must calculate revenue as SUM(UnitPrice * Quantity).
   - Must return results grouped by each music genre.

4. Completeness Checks:
   - Addresses "for each music genre" -> GROUP BY genre.
   - Addresses "total sales revenue" -> SUM of price * quantity.
   - Addresses "in the USA" -> WHERE clause on destination of invoice.

5. Correctness Checks:
   - The query should calculate the UnitPrie * Quantity and sum it over group by genres
   - Filtering for invoices in USA is required

**Query 1:**
```sql
SELECT
  g.Name,
  SUM(il.UnitPrice * il.Quantity) AS TotalRevenue
FROM genres AS g
JOIN tracks AS t ON g.GenreId = t.GenreId
JOIN invoice_lines AS il ON t.TrackId = il.TrackId
JOIN invoices AS i ON il.InvoiceId = i.InvoiceId
WHERE i.BillingCountry = 'USA'
GROUP BY g.Name
```

**Query 2:**
```sql
SELECT
  g.Name,
  COUNT(t.TrackId) AS TracksSold
FROM genres AS g
JOIN tracks AS t ON g.GenreId = t.GenreId
JOIN invoice_lines AS il ON t.TrackId = il.TrackId
JOIN invoices AS i ON il.InvoiceId = i.InvoiceId
WHERE i.BillingCountry = 'USA'
GROUP BY g.Name
```

**Output:**
reasoning: Both queries correctly join the four required tables and filter for sales in the USA. However, the question asks for the 'total sales revenue', which requires calculating the sum of UnitPrice * Quantity. Query 1 correctly performs this calculation. Query 2 incorrectly calculates the COUNT of tracks sold, which answers a different question ("How many tracks of each genre were sold?"). Therefore, Query 1 is the only one that provides the correct metric. winner: 1
---
**Example 5**

**Question**: "Find the names of all artists who have created albums containing tracks from more than one genre."

**Schema:**
CREATE TABLE artists (
  ArtistId INT PRIMARY KEY,
  Name VARCHAR(255)
);
CREATE TABLE albums (
  AlbumId INT PRIMARY KEY,
  ArtistId INT,
  FOREIGN KEY (ArtistId) REFERENCES artists(ArtistId)
);
CREATE TABLE genres (
  GenreId INT PRIMARY KEY,
  Name VARCHAR(255)
);
CREATE TABLE tracks (
  TrackId INT PRIMARY KEY,
  AlbumId INT,
  GenreId INT,
  FOREIGN KEY (AlbumId) REFERENCES albums(AlbumId),
  FOREIGN KEY (GenreId) REFERENCES genres(GenreId)
);

**Hint:** "An artist might have many tracks in the same genre. You need to count the number of distinct genres for each artist."

**Evaluation Criteria:** 
1. Output Requirements:
   - Must return a list of artist names.

2. Mandatory Filters/Conditions:
   - The final list must only include artists who are associated with more than one unique genre.

3. Required Operations:
   - Must connect artists, albums, tracks
   - Must group results by artist.
   - Must make sure the artists have more than one genre
   - The count of genres per artist has otb e distinct

4. Completeness Checks:
   - Addresses "names of all artists" -> SELECT <artist-name>
   - Addresses "more than one genre" -> HAVING <count-of-albums> > 1

5. Correctness Checks:
   - A simple COUNT in the HAVING clause is a critical logical error. For example, `COUNT(tracks.TrackId) > 1` would find artists with more than one song, not artists with more than one genre.

**Query 1:**
```sql
SELECT
  ar.Name
FROM artists AS ar
JOIN albums AS al ON ar.ArtistId = al.ArtistId
JOIN tracks AS t ON al.AlbumId = t.AlbumId
JOIN genres AS g ON t.GenreId = g.GenreId
GROUP BY ar.ArtistId, ar.Name
HAVING COUNT(DISTINCT g.GenreId) > 1
```

**Query 2:**
```sql
SELECT
  ar.Name
FROM artists AS ar
JOIN albums AS al ON ar.ArtistId = al.ArtistId
JOIN tracks AS t ON al.AlbumId = t.AlbumId
GROUP BY ar.ArtistId, ar.Name
HAVING COUNT(t.TrackId) > 1
```

**Output:**
reasoning: The core of the question is to find artists associated with 'more than one genre'. Query 1 correctly joins all the way to the genres table and then uses HAVING COUNT(DISTINCT g.GenreId) > 1. This correctly counts the unique genres for each artist and filters for those with a count greater than one. Query 2 only joins to the tracks table and uses HAVING COUNT(t.TrackId) > 1. This finds artists who have more than one track, regardless of genre. An artist could have 100 tracks all in the same genre and would be incorrectly included by Query 2. Thus, Query 1 is the only logically correct solution. winner: 1

---

Now it is your turn to choose the best query.

**Question:** "{QUESTION}"

**Schema:**
{DATABASE_SCHEMA}

**Hint:** "{HINT}"

**Evaluation Criteria:** 
{EVALUATION_CRITERIA}

**Query 1:**
```sql
{QUERY_1}
```

**Query 2:**
```sql
{QUERY_2}
```

**Output:**
"""