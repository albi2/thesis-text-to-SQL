FEWSHOT_EXAMPLES = """
---
**Example 1:**

**Question:** 
"Find the names of all students from the 'Computer Science' department who are enrolled in more than 2 courses."

**Hint:**
"You should use COUNT(*) > 2 with GROUP BY"

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

**Query:**
SELECT s.student_name FROM students AS s JOIN departments AS d ON s.department_id  =  d.department_id JOIN enrollments AS e ON s.student_id  =  e.student_id WHERE d.department_name  =  'Computer Science' GROUP BY s.student_name HAVING count(*)  >  2

**Result:**
[{'student_name': 'Alice'}, {'student_name': 'Bob'}]

**Output:**
```json
{
  "chain_of_thought": "This is a perfect query. It correctly joins all three necessary tables, filters for the 'Computer Science' department, and groups by student to correctly apply the course count condition. Using GROUP BY on the selected column `student_name` ensures the output is already distinct.",
  "score": 4
}
```
---
**Example 2:**

**Question:** 
"List the names of students who are enrolled in exactly 3 courses."

**Hint:**

**Schema:**
```sql
CREATE TABLE students (
  student_id INT PRIMARY KEY, -- Unique identifier for each student
  student_name VARCHAR(255) -- The full name of the student
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

**Query:**
SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING COUNT(*)  >  3

**Result:**
[{'student_name': 'Charlie'}, {'student_name': 'David'}]

**Output:**
```json
{
  "chain_of_thought": "This query uses the wrong comparison operator (`>` instead of `=`) in the `HAVING` clause, so it returns students with more than 3 courses instead of exactly 3.",
  "score": 1
}
```
---
**Example 3:**

**Question:** 
"Find the title and director of the movie with the highest budget released in 2012."

**Hint:**
"You should use COUNT(*) > 2 with GROUP BY"

**Schema:**
```sql
CREATE TABLE movie (
  MId INT PRIMARY KEY, -- Unique identifier for each movie
  Title VARCHAR(255), -- The title of the movie
  Year INT, -- The release year of the movie
  Director VARCHAR(255), -- The name of the director
  Budget DECIMAL(10, 2), -- The budget of the movie in millions of USD
  Revenue DECIMAL(10, 2) -- The total revenue of the movie in millions of USD
);
```

**Query:**
SELECT T1.Title, T1.Director FROM movie AS T1 WHERE T1.Year  =  2013 AND T1.Revenue  =  (SELECT MAX(Revenue) FROM movie WHERE Year  =  2012)

**Result:**
[{'Title': 'Maze Runner', 'Director': 'Wes Ball'}]

**Output:**
```json
{
  "chain_of_thought": "This query contains multiple critical errors. It filters for the wrong year (2013 instead of 2012) and incorrectly uses the `Revenue` column instead of `Budget` to determine the maximum value. This will likely return no results or incorrect results.",
  "score": 1
}
```

---
**Example 4:**

**Question:** "Show the number of new employees (hired after 2020) and experienced employees in each department."

**Hint:**
"Should filter by employees.HireDate > 2020"

**Schema:**
```sql
CREATE TABLE employees (
  EmployeeID INT PRIMARY KEY, -- Unique identifier for each employee
  FirstName VARCHAR(255), -- The first name of the employee
  LastName VARCHAR(255), -- The last name of the employee
  HireDate DATE, -- The date the employee was hired
  DepartmentID INT, -- Foreign key to the departments table
  FOREIGN KEY (DepartmentID) REFERENCES departments(DepartmentID)
);

CREATE TABLE departments (
  DepartmentID INT PRIMARY KEY, -- Unique identifier for each department
  DepartmentName VARCHAR(255) -- The name of the department
);
```

**Query:**
SELECT d.DepartmentName, e.FirstName, e.LastName, CASE WHEN e.HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID

**Result:**
[{'DepartmentName': 'Sales', 'FirstName': 'John', 'LastName': 'Doe', 'Experience': 'Experienced'}, {'DepartmentName': 'Sales', 'FirstName': 'Jane', 'LastName': 'Smith', 'Experience': 'New'}]

**Output:**
```json
{
  "chain_of_thought": "This query correctly categorizes each employee and follows the hint but fails to perform the required aggregation (COUNT(*)). It also includes extra columns (FirstName, LastName) that were not requested in the final output.",
  "score": 2
}
```

---
**Example 5:**

**Question:** "What is the total duration of all songs for each singer?"

**Hint:**
"Use SUM(song.Duration) with GROUP BY to calculate the duration of all songs per singer".

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

**Query:**
SELECT T1.Name ,  AVG(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID GROUP BY T1.Name

**Result:**
[{'Name': 'Singer A', 'AVG(T2.Duration)': 250.5}, {'Name': 'Singer B', 'AVG(T2.Duration)': 310.0}]

**output:**
```json
{
  "chain_of_thought": "This query correctly joins and groups, but it calculates the AVG of durations instead of the SUM, answering a different question than what was asked.",
  "score": 2
}
```

---
**Example 6:**

**Question:** "List all students and the courses they are enrolled in."

**Hint:**

**Schema:**
```sql
CREATE TABLE students (
  student_id INT PRIMARY KEY, -- Unique identifier for each student
  student_name VARCHAR(255) -- The full name of the student
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

**Query:**
SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id

**Result:**
[{'student_name': 'Alice'}, {'student_name': 'Bob'}]

**Output:**
```json
{
  "chain_of_thought": "This query joins the tables but fails to select the course name, which was a required part of the output. It only partially addresses the question.",
  "score": 2
}
```

---
**Example 7:**

**Question:** 
"What is the percentage of movies directed by 'Christopher Nolan' that were released after the year 2000?"

**Hint:** 
"To calculate the percentage, divide the count of movies by Christopher Nolan after 2000 by the total number of directors."

**Schema:**
```sql
CREATE TABLE movie (
  MId INT PRIMARY KEY, -- Unique identifier for each movie
  Title VARCHAR(255), -- The title of the movie
  Year INT, -- The release year of the movie
  DirectorID INT, -- Foreign key to the directors table
  FOREIGN KEY (DirectorID) REFERENCES directors(DirectorID)
);
CREATE TABLE directors (
  DirectorID INT PRIMARY KEY, -- Unique identifier for each director
  DirectorName VARCHAR(255) -- The name of the director
);
```

**Query:**
SELECT CAST(SUM(CASE WHEN T2.DirectorName = 'Christopher Nolan' AND T1.Year > 2000 THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(T2.DirectorID) FROM movie AS T1 JOIN directors AS T2 ON T1.DirectorID  =  T2.DirectorID

**Result:**
[{'CAST(SUM(CASE WHEN T2.DirectorName = 'Christopher Nolan' AND T1.Year > 2000 THEN 1 ELSE 0 END) AS REAL) * 100 / COUNT(T2.DirectorID)': 0.5}]

**Output:**
```json
{
  "chain_of_thought": "The query blindly follows a logically flawed hint. To calculate the percentage of a director's movies, the denominator should be the total count of that director's movies, not the total count of all directors. The query correctly filters and counts the numerator but uses the wrong denominator based on the bad hint.",
  "score": 1
}
```

---
**Example 8:**

**Question:** "List the unique names of all students."

**Hint:**

**Schema:**
```sql
CREATE TABLE students (
  student_id INT PRIMARY KEY, -- Unique identifier for each student
  student_name VARCHAR(255), -- The full name of the student, which may not be unique
  age INT -- The age of the student
);
```

**Query:**
SELECT student_name FROM students WHERE age > 20

**Result:**
[{'student_name': 'John Smith'}, {'student_name': 'John Smith'}, {'student_name': 'Jane Doe'}]

**Output:**
```json
{
  "chain_of_thought": "This query has two errors. First, it fails to use the `DISTINCT` keyword, which will produce duplicate names if they exist. Second, it adds an unnecessary `WHERE age > 20` clause that was not requested in the question, incorrectly filtering the results.",
  "score": 2
}
```

---
**Example 9:**

**Question:** 
"What is the total revenue generated by all movies?"

**Hint:**

**Schema:**
```sql
CREATE TABLE movie (
  MId INT PRIMARY KEY, -- Unique identifier for each movie
  Title VARCHAR(255), -- The title of the movie
  Year INT, -- The release year of the movie
  Budget DECIMAL(10, 2), -- The budget of the movie in millions of USD
  Revenue DECIMAL(10, 2) -- The total revenue of the movie in millions of USD. Can be NULL if data is unavailable
);
```

**Query:**
SELECT SUM(Revenue) FROM movie

**Result:**
[{'SUM(Revenue)': 5000.00}]

**Output:**
```json
{
  "chain_of_thought": "This query does not handle NULL values properly. If some movies have NULL revenue, they will be excluded from the sum, potentially giving an incorrect total. The query should use COALESCE(Revenue, 0) or explicitly handle NULLs to ensure all movies are counted.",
  "score": 3
}
```

---
**Example 10:**

**Question:** 
"Show the 5 highest-grossing movies."

**Hint:**

**Schema:**
```sql
CREATE TABLE movie (
  MId INT PRIMARY KEY, -- Unique identifier for each movie
  Title VARCHAR(255), -- The title of the movie
  Year INT, -- The release year of the movie
  Revenue DECIMAL(10, 2) -- The total revenue of the movie in millions of USD
);
```

**Query:**
SELECT Title, Revenue FROM movie LIMIT 5

**Result:**
[{'Title': 'Movie A', 'Revenue': 100.00}, {'Title': 'Movie B', 'Revenue': 50.00}, {'Title': 'Movie C', 'Revenue': 300.00}, {'Title': 'Movie D', 'Revenue': 25.00}, {'Title': 'Movie E', 'Revenue': 150.00}]

**Output:**
```json
{
  "chain_of_thought": "This query is missing the ORDER BY clause. Without ordering by Revenue in descending order, it returns 5 arbitrary movies rather than the highest-grossing ones. The query should include ORDER BY Revenue DESC.",
  "score": 1
}
```
"""


QUERY_SCORING_PROMPT = """
You are an expert in text-to-SQL. Your task is to evaluate a SQL query based on a given question, database schema, a hint and a set of evaluation criteria. You must assign a score from 0 to 4 to the query, where 4 is the best score.

**Scoring Criteria (1-4):**
- **4 (Excellent):** The query directly and completely answers the question, and makes optimal use of the provided schema and hint.
- **3 (Good):** The query answers the question well, but might have minor issues like not fully utilizing the hint or having a slightly inefficient structure.
- **2 (Fair):** The query only partially answers the question or has significant inefficiencies.
- **1 (Poor):** The query does not answer the question in any meaningful way.

**Non-exhaustive list of score deduction criteria:
1. **Column Selection:**
    - The SQL is selecting more columns than required in the criteria.
    - The SQL is formatting columns in the response that provide state information for better readability when it's not required in the hint or question.

2. **Table Relationships:**
    - The SQL is joining more tables than necessary or is not joining all the required tables to answer the question.

3. **Filtering Conditions:**
    - The SQL is not correctly filtering based on all the conditions provided in the question and evaluation criteria.
    - The SQL query is filtering based on extra conditions not provided in the question and evaluation criteria.
    - The SQL query uses incorrect comparison operators or incorrect aggregation operators('<' instead of '=' or 'COUNT' instead of 'AVG' or calculating average through division).
    - The SQL query uses incorrect literal values for filtering out the results (e.g filters for movies after 2013 when query asks for movies after 2012).
    - The SQL query does not handle NULL values properly when they can affect the results.
t
4. **Data Grouping:**
    - The SQL output has duplicates query is not using DISTINCT or GROUP BY.
    - The SQL query does not group results based on a specific column when it is required in the question or evaluation criteria(e.g number of employees per department, schools per district etc).

5. **Aggregations and Calculations:**
    - The SQL is not performing the required aggregations(e.g., COUNT instead of AVG)
    - Mathematical operations or calculations don't match the business logic described in the question.(sometimes can be caused by wrong hint from user)
    - The aggregation level doesn't match the question's intent (e.g., aggregating at row level when group level is needed).

6. **Result Ordering:**
    - The SQL query doesn't sort results when ordering is specified or implied in the question.
    - The SQL query uses incorrect sort direction (ASC instead of DESC or vice versa).

7. **Result Limiting:**
    - The SQL query does not limit the rows when the question specifically request n items to be returned (e.g., "top 5", "highest", "earliest").

8. **Hint Interpretation:**
    - The SQL query blindly does what is provided in the hint without questioning whether it is correct.

**Instructions:**
1.  Carefully analyze the question, schema, and hint.
2.  Evaluate the correctness and relevance of the query using the list of score deduction criteria.
3.  Assign a score from 0 to 4 based on the scoring criteria. If a query does not have any of the issues in the criteria it is a strong candidate for a 4.
4.  Provide a step-by-step reasoning for your score for the query.

**Output Format**
Provide the output in the following format:
```json
{{
  "chain_of_thought": "<reasoning logic for scoring>",
  "score": <score number 0-4>
}}
```

Here are some examples:
{FEWSHOT_EXAMPLES}

To understand the question requirements better, below are some evaluation criteria:
{EVALUATION_CRITERIA}

Given the following information, score the provided query.

**Question:** 
"{QUESTION}"

**Hint:** 
"{HINT}"

**Schema:**
{DATABASE_SCHEMA}

**Query:**
{QUERY}

**Output:**
"""
