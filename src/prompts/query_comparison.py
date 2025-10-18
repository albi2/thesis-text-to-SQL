QUERY_COMPARISON_FEWSHOTS = """
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
Output: [{'student_name': 'Alice'}, {'student_name': 'Bob'}, {'student_name': 'Charlie'}]


**Query 2:**
```sql
SELECT T1.student_name
FROM students AS T1
JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id
JOIN courses AS T3 ON T2.course_id  =  T3.course_id
WHERE T3.course_name  =  'Computer Science'
```
Output:
[{'student_name': 'Alice'}, {'student_name': 'Charlie'}]

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
Output:
[{'Name': 'SingerA'}, {'Name': 'SingerA'}]

**Query 2:**
```sql
SELECT DISTINCT T1.Name
FROM singer AS T1
JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID
WHERE T2.Duration  >  400
```
Output:
[{'Name': 'SingerA'}]

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
Output:
[{'DepartmentName': 'HR', 'Name': 'John Doe', 'Salary': 90000}, {'DepartmentName': 'Engineering', 'Name': 'Jane Smith', 'Salary': 120000}]

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
Output:
[{'DepartmentName': 'HR', 'Name': 'John Doe', 'Salary': 90000}, {'DepartmentName': 'Engineering', 'Name': 'Jane Smith', 'Salary': 120000}]

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
   - The query should calculate the UnitPrie * Quantity and sum it grouping by genres
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
Output:
[{'Name': 'Rock', 'TotalRevenue': 150.00}, {'Name': 'Jazz', 'TotalRevenue': 75.50}]

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
Output:
[{'Name': 'Rock', 'TracksSold': 100}, {'Name': 'Jazz', 'TracksSold': 50}]

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
Output:
`[{'Name': 'Versatile Artist'}]

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
Output:
[{'Name': 'Versatile Artist'}, {'Name': 'Single Genre Artist'}]

**Output:**
reasoning: The core of the question is to find artists associated with 'more than one genre'. Query 1 correctly joins all the way to the genres table and then uses HAVING COUNT(DISTINCT g.GenreId) > 1. This correctly counts the unique genres for each artist and filters for those with a count greater than one. Query 2 only joins to the tracks table and uses HAVING COUNT(t.TrackId) > 1. This finds artists who have more than one track, regardless of genre. An artist could have 100 tracks all in the same genre and would be incorrectly included by Query 2. Thus, Query 1 is the only logically correct solution. winner: 1

---
**Example 6**

**Question**: "List all employees and their department names. If an employee is not assigned to a department, their department name should be shown as NULL."

**Schema:**
CREATE TABLE employees (
  EmployeeID INT PRIMARY KEY,
  Name VARCHAR(255),
  DepartmentID INT
);
CREATE TABLE departments (
  DepartmentID INT PRIMARY KEY,
  DepartmentName VARCHAR(255)
);

**Hint:** "To include all employees, even those without a department, a LEFT JOIN from employees to departments is necessary."

**Evaluation Criteria:**
1. Output Requirements:
   - Must return employee name and department name.
   - Must include all employees.

2. Mandatory Filters/Conditions:
   - No explicit filters, but the join condition is critical.

3. Required Operations:
   - Must JOIN employees and departments tables.
   - The join must be a LEFT JOIN to ensure all employees are listed.

4. Completeness Checks:
   - Addresses "all employees" -> LEFT JOIN.
   - Addresses "their department names" -> SELECT department name.

5. Correctness Checks:
   - An INNER JOIN is incorrect as it will exclude employees without a department.
   - The query must correctly return NULL for the department name when an employee has no matching department.

**Query 1:**
```sql
SELECT
  e.Name,
  d.DepartmentName
FROM employees AS e
JOIN departments AS d ON e.EmployeeID = d.DepartmentID
```
Output:
[{'Name': 'Alice', 'DepartmentName': 'Engineering'}]

**Query 2:**
```sql
SELECT
  e.Name,
  d.DepartmentName
FROM employees AS e
LEFT JOIN departments AS d ON e.DepartmentID = d.DepartmentID
```
Output:
[{'Name': 'Alice', 'DepartmentName': 'Engineering'}, {'Name': 'Bob', 'DepartmentName': None}]

**Output:**
reasoning: The question requires listing *all* employees, including those not assigned to a department. Query 1 uses an INNER JOIN, which only returns employees who have a matching department, thus excluding employees with a NULL DepartmentID. Query 2 correctly uses a LEFT JOIN, which ensures that all records from the employees table are returned, with the DepartmentName being NULL for employees who do not have a matching department. Therefore, Query 2 is the correct and complete solution. winner: 2
---
**Example 7**

**Question**: "Who is the shortest employee? List their name and height."

**Schema:**
CREATE TABLE employees (
  EmployeeID INT PRIMARY KEY,
  Name VARCHAR(255),
  HeightCM INT
);

**Hint:** "When ordering in ascending order, NULL values are often treated as the lowest value and will appear first. You must filter them out to find the true minimum."

**Evaluation Criteria:**
1. Output Requirements:
   - Must return the employee's name and height.
   - Should only return the employee(s) with the minimum non-null height.

2. Mandatory Filters/Conditions:
   - MUST exclude employees where HeightCM is NULL from the comparison.

3. Required Operations:
   - Must order the results by HeightCM in ascending order.
   - Must limit the result to the top record.

4. Completeness Checks:
   - Addresses "shortest employee" -> ORDER BY HeightCM ASC LIMIT 1.
   - Addresses "who" -> SELECT Name.

5. Correctness Checks:
   - A query that does not filter for `HeightCM IS NOT NULL` is incorrect because it might return an employee with a NULL height, which is not the shortest valid height.
   - The ordering must be ascending (`ASC`) to find the minimum value.

**Query 1:**
```sql
SELECT Name, HeightCM
FROM employees
ORDER BY HeightCM ASC
LIMIT 1
```
Output:
[{'Name': 'Charlie', 'HeightCM': None}]

**Query 2:**
```sql
SELECT Name, HeightCM
FROM employees
WHERE HeightCM IS NOT NULL
ORDER BY HeightCM ASC
LIMIT 1
```
Output:
[{'Name': 'Alice', 'HeightCM': 155}]

**Output:**
reasoning: The goal is to find the employee with the minimum valid height. In standard SQL, `NULL` values are often sorted first in an ascending order. Query 1 fails to filter out `NULL` heights, so it incorrectly identifies an employee with a `NULL` height as the shortest. Query 2 correctly adds the `WHERE HeightCM IS NOT NULL` clause, ensuring that only employees with a recorded height are considered. This allows the `ORDER BY` and `LIMIT` clauses to correctly identify the employee with the true minimum height. winner: 2
---
"""

NOHINT_QUERY_COMPARISON_FEWSHOTS = """
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
Output: [{'student_name': 'Alice'}, {'student_name': 'Bob'}, {'student_name': 'Charlie'}]

**Query 2:**
```sql
SELECT T1.student_name
FROM students AS T1
JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id
JOIN courses AS T3 ON T2.course_id  =  T3.course_id
WHERE T3.course_name  =  'Computer Science'
```
Output:
[{'student_name': 'Alice'}, {'student_name': 'Charlie'}]

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
Output:
[{'Name': 'SingerA'}, {'Name': 'SingerA'}]

**Query 2:**
```sql
SELECT DISTINCT T1.Name
FROM singer AS T1
JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID
WHERE T2.Duration  >  400
```
Output:
[{'Name': 'SingerA'}]

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
Output:
[{'DepartmentName': 'HR', 'Name': 'John Doe', 'Salary': 90000}, {'DepartmentName': 'Engineering', 'Name': 'Jane Smith', 'Salary': 120000}]

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
Output:
[{'DepartmentName': 'HR', 'Name': 'John Doe', 'Salary': 90000}, {'DepartmentName': 'Engineering', 'Name': 'Jane Smith', 'Salary': 120000}]

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
   - The query should calculate the UnitPrie * Quantity and sum it grouping by genres
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
Output:
[{'Name': 'Rock', 'TotalRevenue': 150.00}, {'Name': 'Jazz', 'TotalRevenue': 75.50}]

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
Output:
[{'Name': 'Rock', 'TracksSold': 100}, {'Name': 'Jazz', 'TracksSold': 50}]

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
Output:
[{'Name': 'Versatile Artist'}]

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
Output:
[{'Name': 'Versatile Artist'}, {'Name': 'Single Genre Artist'}]

**Output:**
reasoning: The core of the question is to find artists associated with 'more than one genre'. Query 1 correctly joins all the way to the genres table and then uses HAVING COUNT(DISTINCT g.GenreId) > 1. This correctly counts the unique genres for each artist and filters for those with a count greater than one. Query 2 only joins to the tracks table and uses HAVING COUNT(t.TrackId) > 1. This finds artists who have more than one track, regardless of genre. An artist could have 100 tracks all in the same genre and would be incorrectly included by Query 2. Thus, Query 1 is the only logically correct solution. winner: 1

---
**Example 6**

**Question**: "List all employees and their department names. If an employee is not assigned to a department, their department name should be shown as NULL."

**Schema:**
CREATE TABLE employees (
  EmployeeID INT PRIMARY KEY,
  Name VARCHAR(255),
  DepartmentID INT
);
CREATE TABLE departments (
  DepartmentID INT PRIMARY KEY,
  DepartmentName VARCHAR(255)
);

**Evaluation Criteria:**
1. Output Requirements:
   - Must return employee name and department name.
   - Must include all employees.

2. Mandatory Filters/Conditions:
   - No explicit filters, but the join condition is critical.

3. Required Operations:
   - Must JOIN employees and departments tables.
   - The join must be a LEFT JOIN to ensure all employees are listed.

4. Completeness Checks:
   - Addresses "all employees" -> LEFT JOIN.
   - Addresses "their department names" -> SELECT department name.

5. Correctness Checks:
   - An INNER JOIN is incorrect as it will exclude employees without a department.
   - The query must correctly return NULL for the department name when an employee has no matching department.

**Query 1:**
```sql
SELECT
  e.Name,
  d.DepartmentName
FROM employees AS e
JOIN departments AS d ON e.EmployeeID = d.DepartmentID
```
Output:
[{'Name': 'Alice', 'DepartmentName': 'Engineering'}]

**Query 2:**
```sql
SELECT
  e.Name,
  d.DepartmentName
FROM employees AS e
LEFT JOIN departments AS d ON e.DepartmentID = d.DepartmentID
```
Output:
[{'Name': 'Alice', 'DepartmentName': 'Engineering'}, {'Name': 'Bob', 'DepartmentName': None}]

**Output:**
reasoning: The question requires listing *all* employees, including those not assigned to a department. Query 1 uses an INNER JOIN, which only returns employees who have a matching department, thus excluding employees with a NULL DepartmentID. Query 2 correctly uses a LEFT JOIN, which ensures that all records from the employees table are returned, with the DepartmentName being NULL for employees who do not have a matching department. Therefore, Query 2 is the correct and complete solution. winner: 2
---
**Example 7**

**Question**: "Who is the shortest employee? List their name and height."

**Schema:**
CREATE TABLE employees (
  EmployeeID INT PRIMARY KEY,
  Name VARCHAR(255),
  HeightCM INT
);

**Evaluation Criteria:**
1. Output Requirements:
   - Must return the employee's name and height.
   - Should only return the employee(s) with the minimum non-null height.

2. Mandatory Filters/Conditions:
   - MUST exclude employees where HeightCM is NULL from the comparison.

3. Required Operations:
   - Must order the results by HeightCM in ascending order.
   - Must limit the result to the top record.

4. Completeness Checks:
   - Addresses "shortest employee" -> ORDER BY HeightCM ASC LIMIT 1.
   - Addresses "who" -> SELECT Name.

5. Correctness Checks:
   - A query that does not filter for `HeightCM IS NOT NULL` is incorrect because it might return an employee with a NULL height, which is not the shortest valid height.
   - The ordering must be ascending (`ASC`) to find the minimum value.

**Query 1:**
```sql
SELECT Name, HeightCM
FROM employees
ORDER BY HeightCM ASC
LIMIT 1
```
Output:
[{'Name': 'Charlie', 'HeightCM': None}]

**Query 2:**
```sql
SELECT Name, HeightCM
FROM employees
WHERE HeightCM IS NOT NULL
ORDER BY HeightCM ASC
LIMIT 1
```
Output:
[{'Name': 'Alice', 'HeightCM': 155}]

**Output:**
reasoning: The goal is to find the employee with the minimum valid height. In standard SQL, `NULL` values are often sorted first in an ascending order. Query 1 fails to filter out `NULL` heights, so it incorrectly identifies an employee with a `NULL` height as the shortest. Query 2 correctly adds the `WHERE HeightCM IS NOT NULL` clause, ensuring that only employees with a recorded height are considered. This allows the `ORDER BY` and `LIMIT` clauses to correctly identify the employee with the true minimum height. winner: 2
---
"""

NOCRITERIA_COMPARISON_FEWSHOTS = """
---
**Example 1:**

**Question:** 
"Find the names of all students from the 'Computer Science' department who are enrolled in more than 2 courses."

**Hint:**

**Schema:**
```sql
CREATE TABLE students (
  student_id INT PRIMARY KEY, -- Unique identifier for each student
  student_name VARCHAR(255), -- The full name of the student
  department_id INT, -- Foreign key to the departments table
  FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE departments (
  department_id INT PRIMARY KEY, -- Unique identifier for each department
  department_name VARCHAR(255) -- The name of the department, e.g., 'Computer Science', 'Physics'
);

CREATE TABLE courses (
  course_id INT PRIMARY KEY, -- Unique identifier for each course
  course_name VARCHAR(255) -- The name of the course
);

CREATE TABLE enrollments (
  student_id INT, -- Foreign key to the students table
  course_id INT, -- Foreign key to the courses table
  FOREIGN KEY (student_id) REFERENCES students(student_id),
  FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

**Query 1:**
```sql
SELECT s.student_name 
FROM students AS s 
JOIN departments AS d ON s.department_id = d.department_id 
JOIN enrollments AS e ON s.student_id = e.student_id 
WHERE d.department_name = 'Computer Science' 
GROUP BY s.student_name 
HAVING count(*) > 2
```
**Result:** 
[{'student_name': 'Alice'}, {'student_name': 'Bob'}]

**Query 2:**
```sql
SELECT s.student_name 
FROM students AS s 
JOIN departments AS d ON s.department_id = d.department_id 
JOIN enrollments AS e ON s.student_id = e.student_id 
WHERE d.department_name = 'Computer Science' 
GROUP BY s.student_name 
HAVING count(*) = 2
```
**Result:** 
[{'student_name': 'Charlie'}]

**Output:**

Evaluation:
- Column Selection: both - both queries select only student_name as required
- Table Relationships: both - both queries join all three necessary tables (students, departments, enrollments)
- Filtering Conditions: both - both queries correctly filter for 'Computer Science' department
- Data Grouping: both - both queries group by student_name correctly
- Aggregations and Calculations: 1 - Query 1 uses count(*) > 2 which matches 'more than 2 courses'; Query 2 uses count(*) = 2 which means 'exactly 2 courses', not 'more than 2'
- Result Ordering: N/A
- Result Limiting: N/A
- Hint Interpretation: N/A

```json
{
  "reasoning": "Both queries have the correct structure and joins, but Query 2 uses the wrong comparison operator in the HAVING clause. The question asks for students enrolled in 'more than 2 courses', which requires '> 2', not '= 2'. Query 1 correctly implements this condition.",
  "winner": 1
}
```

---
**Example 2:**

**Question:** "List the unique names of singers who have a song with a duration of more than 400."

**Hint:** "Duration more than 400 means song.Duration > 400"

**Schema:**
```sql
CREATE TABLE singer (
  Singer_ID INT PRIMARY KEY, -- Unique identifier for each singer
  Name VARCHAR(255) -- The name of the singer
);

CREATE TABLE song (
  Song_ID INT PRIMARY KEY, -- Unique identifier for each song
  Title VARCHAR(255), -- The title of the song
  Singer_ID INT, -- Foreign key to the singer table
  Duration INT, -- The duration of the song in seconds
  FOREIGN KEY (Singer_ID) REFERENCES singer(Singer_ID)
);
```


**Query 1:**
```sql
SELECT T1.Name
FROM singer AS T1
JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID
WHERE T2.Duration > 400
```
**Result:**
[{'Name': 'SingerA'}, {'Name': 'SingerA'}]

**Query 2:**
```sql
SELECT DISTINCT T1.Name
FROM singer AS T1
JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID
WHERE T2.Duration > 400
```
**Result:**
[{'Name': 'SingerA'}]

**Output:**

Evaluation:
- Column Selection: both - both queries select singer name as required
- Table Relationships: both - both queries correctly join singer and song tables
- Filtering Conditions: both - both queries correctly filter for Duration > 400
- Data Grouping: 2 - Query 1 is missing DISTINCT or GROUP BY and produces duplicate names; Query 2 uses DISTINCT to ensure unique names as required by the question
- Aggregations and Calculations: N/A
- Result Ordering: N/A
- Result Limiting: N/A
- Hint Interpretation: both - both queries correctly apply the hint

```json
{
  "reasoning": "Both queries correctly join the tables and filter for songs with duration greater than 400. However, the question explicitly asks for 'unique names'. If a singer has multiple songs meeting the criteria, Query 1 will list their name multiple times, resulting in duplicates. Query 2 correctly uses DISTINCT to ensure each singer appears only once.",
  "winner": 2
}
```

---
**Example 3:**

**Question:** "Show the number of new employees (hired after 2020) and experienced employees in each department."

**Schema:**
```sql
CREATE TABLE employees (
  EmployeeID INT PRIMARY KEY,
  FirstName VARCHAR(255),
  LastName VARCHAR(255),
  HireDate DATE,
  DepartmentID INT,
  FOREIGN KEY (DepartmentID) REFERENCES departments(DepartmentID)
);

CREATE TABLE departments (
  DepartmentID INT PRIMARY KEY,
  DepartmentName VARCHAR(255)
);
```

**Query 1:**
```sql
SELECT d.DepartmentName, e.FirstName, e.LastName, 
       CASE WHEN e.HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience
FROM employees AS e
JOIN departments AS d ON e.DepartmentID = d.DepartmentID
```
**Result:** 
[{'DepartmentName': 'Sales', 'FirstName': 'John', 'LastName': 'Doe', 'Experience': 'Experienced'}, {'DepartmentName': 'Sales', 'FirstName': 'Jane', 'LastName': 'Smith', 'Experience': 'New'}]

**Query 2:**
```sql
SELECT d.DepartmentName,
       SUM(CASE WHEN e.HireDate > '2020-12-31' THEN 1 ELSE 0 END) AS NewEmployees,
       SUM(CASE WHEN e.HireDate <= '2020-12-31' THEN 1 ELSE 0 END) AS ExperiencedEmployees
FROM employees AS e
JOIN departments AS d ON e.DepartmentID = d.DepartmentID
GROUP BY d.DepartmentName
```
**Result:**
[{'DepartmentName': 'Sales', 'NewEmployees': 5, 'ExperiencedEmployees': 10}]

**Output:**

Evaluation:
- Column Selection: 2 - Query 1 includes FirstName and LastName which were not requested; Query 2 correctly selects department name and counts for each category
- Table Relationships: both - both queries correctly join employees and departments tables
- Filtering Conditions: both - both queries correctly categorize based on HireDate > '2020-12-31'
- Data Grouping: 2 - Query 1 returns individual rows instead of grouped counts per department; Query 2 groups by department as required by 'in each department'
- Aggregations and Calculations: 2 - Query 1 is missing COUNT aggregation for each category; Query 2 correctly counts employees in each category using SUM with CASE
- Result Ordering: N/A
- Result Limiting: N/A
- Hint Interpretation: N/A

```json
{
  "reasoning": "The question asks for 'the number of' employees in each category 'in each department', which requires aggregation and grouping. Query 1 lists individual employee rows without counting, and includes unnecessary columns (FirstName, LastName). Query 2 correctly groups by department and counts employees in each category, fully answering the question.",
  "winner": 2
}
```

---
**Example 4:**

**Question:** "List all students and the courses they are enrolled in."

**Hint:**

**Schema:**
```sql
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
  course_id INT,
  FOREIGN KEY (student_id) REFERENCES students(student_id),
  FOREIGN KEY (course_id) REFERENCES courses(course_id)
);
```

**Query 1:**
```sql
SELECT DISTINCT T1.student_name 
FROM students AS T1 
JOIN enrollments AS T2 ON T1.student_id = T2.student_id
```
**Result:**
[{'student_name': 'Alice'}, {'student_name': 'Bob'}]

**Query 2:**
```sql
SELECT T1.student_name, T3.course_name
FROM students AS T1 
JOIN enrollments AS T2 ON T1.student_id = T2.student_id
JOIN courses AS T3 ON T2.course_id = T3.course_id
```
**Result:**
[{'student_name': 'Alice', 'course_name': 'Math'}, {'student_name': 'Alice', 'course_name': 'Physics'}, {'student_name': 'Bob', 'course_name': 'Chemistry'}]

**Output:**

Evaluation:
- Column Selection: 2 - Query 1 only selects student_name but is missing course_name; Query 2 selects both student_name and course_name as required
- Table Relationships: 2 - Query 1 joins students and enrollments but is missing the courses table; Query 2 joins all three necessary tables (students, enrollments, courses)
- Filtering Conditions: N/A
- Data Grouping: N/A
- Aggregations and Calculations: N/A
- Result Ordering: N/A
- Result Limiting: N/A
- Hint Interpretation: N/A

```json
{
  "reasoning": "The question asks for 'students AND the courses they are enrolled in', requiring both pieces of information. Query 1 only returns student names without course information and doesn't join the courses table. Query 2 correctly joins all three tables and selects both student names and their corresponding courses.",
  "winner": 2
}
```

---
**Example 5:**

**Question:** "What is the percentage of movies directed by 'Christopher Nolan' that were released after the year 2000?"

**Hint:** "To calculate the percentage, divide the count of movies by Christopher Nolan after 2000 by the total number of directors."

**Schema:**
```sql
CREATE TABLE movie (
  MId INT PRIMARY KEY,
  Title VARCHAR(255),
  Year INT,
  DirectorID INT,
  FOREIGN KEY (DirectorID) REFERENCES directors(DirectorID)
);

CREATE TABLE directors (
  DirectorID INT PRIMARY KEY,
  DirectorName VARCHAR(255)
);
```

**Query 1:**
```sql
SELECT CAST(SUM(CASE WHEN T2.DirectorName = 'Christopher Nolan' AND T1.Year > 2000 THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(T2.DirectorID) 
FROM movie AS T1 
JOIN directors AS T2 ON T1.DirectorID = T2.DirectorID
```
**Result:**
[{'percentage': 0.5}]

**Query 2:**
```sql
SELECT CAST(SUM(CASE WHEN T1.Year > 2000 THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(*) 
FROM movie AS T1 
JOIN directors AS T2 ON T1.DirectorID = T2.DirectorID 
WHERE T2.DirectorName = 'Christopher Nolan'
```
**Result:** 
[{'percentage': 75.0}]

**Output:**

Evaluation:
- Column Selection: both - both queries return percentage calculation
- Table Relationships: both - both queries correctly join movie and directors tables
- Filtering Conditions: both - Query 1 filters for 'Christopher Nolan' and Year > 2000 in CASE statement; Query 2 filters for 'Christopher Nolan' in WHERE clause
- Data Grouping: N/A
- Aggregations and Calculations: 2 - Query 1 has denominator as COUNT of all directors, not Christopher Nolan's total movies; Query 2 has denominator as COUNT of all Christopher Nolan's movies, numerator is those after 2000
- Result Ordering: N/A
- Result Limiting: N/A
- Hint Interpretation: 2 - Query 1 blindly follows the flawed hint without validating logic; Query 2 recognizes the hint is flawed and uses correct logic

```json
{
  "reasoning": "The question asks for the percentage of Christopher Nolan's movies released after 2000. Query 1 blindly follows the flawed hint and divides by the count of all directors, which is logically incorrect. Query 2 correctly filters for only Christopher Nolan's movies first, then calculates what percentage of those were released after 2000.",
  "winner": 2
}
```

---
**Example 6:**

**Question:** "Show the 5 highest-grossing movies."

**Schema:**
```sql
CREATE TABLE movie (
  MId INT PRIMARY KEY,
  Title VARCHAR(255),
  Year INT,
  Revenue DECIMAL(10, 2)
);
```

**Query 1:**
```sql
SELECT Title, Revenue 
FROM movie 
LIMIT 5
```
**Result:** 
[{'Title': 'Movie A', 'Revenue': 100.00}, {'Title': 'Movie B', 'Revenue': 50.00}, {'Title': 'Movie C', 'Revenue': 300.00}, {'Title': 'Movie D', 'Revenue': 25.00}, {'Title': 'Movie E', 'Revenue': 150.00}]

**Query 2:**
```sql
SELECT Title, Revenue 
FROM movie 
ORDER BY Revenue DESC 
LIMIT 5
```
**Result:** 
[{'Title': 'Movie C', 'Revenue': 300.00}, {'Title': 'Movie E', 'Revenue': 150.00}, {'Title': 'Movie A', 'Revenue': 100.00}, {'Title': 'Movie F', 'Revenue': 95.00}, {'Title': 'Movie G', 'Revenue': 80.00}]

**Output:**

Evaluation:
- Column Selection: both - both queries select Title and Revenue as required
- Table Relationships: both - both queries use only the movie table which is sufficient
- Filtering Conditions: N/A
- Data Grouping: N/A
- Aggregations and Calculations: N/A
- Result Ordering: 2 - Query 1 is missing ORDER BY Revenue DESC; Query 2 correctly orders by Revenue DESC to get highest-grossing first
- Result Limiting: both - both queries correctly use LIMIT 5
- Hint Interpretation: N/A
```json
{
  "reasoning": "The question asks for the '5 highest-grossing' movies, which implies ordering by revenue in descending order. Query 1 returns 5 arbitrary movies without sorting, so it's unlikely to return the correct results. Query 2 correctly sorts by Revenue DESC before limiting, ensuring the 5 highest-grossing movies are returned.",
  "winner": 2
}
```
"""

QUERY_COMPARISON_PROMPT = """
You are an expert in text-to-SQL. Your task is to compare two SQL queries based on a given question, database schema, and hint, and determine which one is better.

**Instructions:**
1.  Carefully analyze the question, schema, evaluation criteria and hint.
2.  Evaluate both queries based on correctness and completeness as described below.
3.  The query that better answers the question is the winner.
4.  If both queries output the same results, choose the one with that is most performant(JOINS are usually more performant than subqueries)
4.  Provide a step-by-step reasoning for your choice.

**Non-exhaustive list of query correctnes and completeness questions when evaluating:**
1. **Column Selection:**
    - Does the SQL select only the columns required by the question?
    - Does the SQL avoid formatting columns for readability when it's not required in the hint or question?

2. **Table Relationships:**
    - Does the SQL join all the required tables to answer the question?
    - Does the SQL avoid joining more tables than necessary?

3. **Filtering Conditions:**
    - Does the SQL correctly filter based on all the conditions provided in the question and evaluation criteria?
    - Does the SQL avoid filtering based on extra conditions not provided in the question and evaluation criteria?
    - Does the SQL use correct comparison operators (e.g., '=' instead of '<', or '>=' instead of '>')?
    - Does the SQL use correct literal values for filtering (e.g., filters for movies after 2012 when the question asks for movies after 2012)?
    - Does the SQL handle NULL values properly when they can affect the results?

4. **Data Grouping:**
    - Does the SQL use DISTINCT or GROUP BY to eliminate duplicates when necessary?
    - Does the SQL group results by the appropriate column(s) when required by the question (e.g., "per department", "by category")?

5. **Aggregations and Calculations:**
    - Does the SQL perform the correct aggregations as required by the question (e.g., SUM instead of AVG)?
    - Do the mathematical operations or calculations match the business logic described in the question?
    - Does the aggregation level match the question's intent (e.g., group-level aggregation when per-group results are needed)?

6. **Result Ordering:**
    - Does the SQL sort results when ordering is specified or implied in the question?
    - Does the SQL use the correct sort direction (ASC vs DESC)?

7. **Result Limiting:**
    - Does the SQL limit the rows when the question specifically requests n items to be returned (e.g., "top 5", "highest", "earliest")?

8. **Hint Interpretation:**
    - Does the SQL validate the hint's correctness against the question requirements rather than blindly following it?

**Output Format**

Before providing your final JSON output, you must first write out your evaluation of both queries against each criterion. Use this format:

**Evaluation:**
- Column Selection: 1/2/both/neither - explanation
- Table Relationships: 1/2/both/neither - explanation
- Filtering Conditions: 1/2/both/neither/N/A - explanation
- Data Grouping: 1/2/both/neither/N/A - explanation
- Aggregations and Calculations: 1/2/both/neither/N/A - explanation
- Result Ordering: 1/2/both/neither/N/A - explanation
- Result Limiting: 1/2/both/neither/N/A - explanation
- Hint Interpretation: 1/2/both/neither/N/A - explanation

After completing your evaluation, provide your final answer as a JSON object:
```json
{
  "reasoning": "2-4 sentence explanation comparing the queries and justifying the winner",
  "winner": "1 or 2"
}
```

**Notes On The Evaluation Step:**
- Use "1" if only Query 1 satisfies the criterion correctly
- Use "2" if only Query 2 satisfies the criterion correctly
- Use "both" if both queries satisfy the criterion correctly
- Use "neither" if both queries fail the criterion
- Use "N/A" when the criterion doesn't apply to the question
- The winner in the JSON must be either 1 or 2

Here are some examples to understand how the process should work:
{FEWSHOT_EXAMPLES}

Now it is your turn to choose the best query.

**Question:** 
{QUESTION}

**Hint**
{HINT}

**Schema:**
{DATABASE_SCHEMA}

**Evaluation Criteria:** 
{EVALUATION_CRITERIA}

**Query 1:**
```sql
{QUERY_1}
```
**Result:**
{QUERY_1_OUTPUT}

**Query 2:**
```sql
{QUERY_2}
```
**Result:**
{QUERY_2_OUTPUT}

**Output:**
"""