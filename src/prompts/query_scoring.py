FEWSHOT_EXAMPLES = """
---

**Example 1:**

**Question:** "Find the names of all students who are enrolled in more than 3 courses."

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

**Hint:** 

**Queries:**
1. SELECT student_name FROM students WHERE student_id IN (SELECT student_id FROM enrollments GROUP BY student_id HAVING COUNT(course_id) > 3)
Output:
[{'student_name': 'Alice'}, {'student_name': 'Bob'}]

2. SELECT COUNT(T1.student_id) FROM students AS T1
Output:
[{'COUNT(T1.student_id)': 10}]

3. SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id
Output:
[{'student_name': 'Alice'}, {'student_name': 'Bob'}, {'student_name': 'Charlie'}, {'student_name': 'David'}]

4. SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3
Output:
[{'student_name': 'Alice'}, {'student_name': 'Bob'}]

5. SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3
Output:
[{'student_name': 'Alice'}, {'student_name': 'Bob'}]

6. SELECT T1.student_name, count(*) FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3
Output:
[{'student_name': 'Alice', 'count(*)': 4}, {'student_name': 'Bob', 'count(*)': 5}]

7. SELECT T1.student_name FROM students AS T1
Output:
[{'student_name': 'Alice'}, {'student_name': 'Bob'}, {'student_name': 'Charlie'}, {'student_name': 'David'}, {'student_name': 'Eve'}]

8. SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  =  3
Output:
[{'student_name': 'Charlie'}]

9. SELECT T1.course_name FROM courses AS T1 JOIN enrollments AS T2 ON T1.course_id  =  T2.course_id GROUP BY T1.course_name HAVING count(*)  >  3
Output:
[{'course_name': 'Introduction to Programming'}]

**Output:**
```json
[
  {
    "query": "SELECT student_name FROM students WHERE student_id IN (SELECT student_id FROM enrollments GROUP BY student_id HAVING COUNT(course_id) > 3)",
    "chain_of_thought": "Uses a subquery to achieve the same result. It correctly answers the question, but without `DISTINCT` it may produce duplicates.",
    "score": 3
  },
  {
    "query": "SELECT COUNT(T1.student_id) FROM students AS T1",
    "chain_of_thought": "Only counts the total number of students. This is irrelevant to the question.",
    "score": 1
  },
  {
    "query": "SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id",
    "chain_of_thought": "Joins the tables but doesn't group or filter. This only partially addresses the question.",
    "score": 2
  },
  {
    "query": "SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3",
    "chain_of_thought": "This query is missing the `DISTINCT` keyword, which will lead to duplicate results. The query is otherwise correct.",
    "score": 3
  },
  {
    "query": "SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3",
    "chain_of_thought": "Correctly joins `students` and `enrollments`, groups by `student_name`, and filters for students with more than 3 courses. This is a perfect answer.",
    "score": 4
  },
  {
    "query": "SELECT T1.student_name, count(*) FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3",
    "chain_of_thought": "This query returns an extra column (the count), which was not requested.",
    "score": 3
  },
  {
    "query": "SELECT T1.student_name FROM students AS T1",
    "chain_of_thought": "This query only returns the student names without any filtering or aggregation.",
    "score": 1
  },
  {
    "query": "SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  =  3",
    "chain_of_thought": "This query uses `=` instead of `>` in the `HAVING` clause, which is a critical error.",
    "score": 1
  },
  {
    "query": "SELECT T1.course_name FROM courses AS T1 JOIN enrollments AS T2 ON T1.course_id  =  T2.course_id GROUP BY T1.course_name HAVING count(*)  >  3",
    "chain_of_thought": "This query is completely irrelevant as it is querying courses instead of students.",
    "score": 0
  }
]
```

---

**Example 2:**

**Question:** "Categorize employees as 'New' or 'Experienced' based on their hire date. New employees were hired after 2020. Also show the number of new and experienced employees in each department."

**Schema:**
```sql
CREATE TABLE employees (
  EmployeeID INT PRIMARY KEY,
  FirstName VARCHAR(255),
  LastName VARCHAR(255),
  HireDate DATE,
  DepartmentID INT
);

CREATE TABLE departments (
  DepartmentID INT PRIMARY KEY,
  DepartmentName VARCHAR(255)
);
```

**Hint:** "A 'New' employee is one where the HireDate column is greater than '2020-12-31'."

**Queries:**
1. SELECT d.DepartmentName, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID GROUP BY d.DepartmentName
Output:
[{'DepartmentName': 'HR', 'COUNT(*)': 10}, {'DepartmentName': 'Engineering', 'COUNT(*)': 15}]

2. SELECT CASE WHEN HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience, COUNT(*) FROM employees GROUP BY Experience
Output:
[{'Experience': 'New', 'COUNT(*)': 8}, {'Experience': 'Experienced', 'COUNT(*)': 17}]

3. SELECT d.DepartmentName, CASE WHEN e.HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID GROUP BY d.DepartmentName, Experience
Output:
[{'DepartmentName': 'HR', 'Experience': 'New', 'COUNT(*)': 3}, {'DepartmentName': 'HR', 'Experience': 'Experienced', 'COUNT(*)': 7}, {'DepartmentName': 'Engineering', 'Experience': 'New', 'COUNT(*)': 5}, {'DepartmentName': 'Engineering', 'Experience': 'Experienced', 'COUNT(*)': 10}]

4. SELECT d.DepartmentName, e.FirstName, e.LastName, CASE WHEN e.HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID
Output:
[{'DepartmentName': 'HR', 'FirstName': 'John', 'LastName': 'Doe', 'Experience': 'Experienced'}, {'DepartmentName': 'Engineering', 'FirstName': 'Jane', 'LastName': 'Smith', 'Experience': 'New'}]

5. SELECT d.DepartmentName, CASE WHEN e.HireDate < '2021-01-01' THEN 'New' ELSE 'Experienced' END AS Experience, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID GROUP BY d.DepartmentName, Experience
Output:
[{'DepartmentName': 'HR', 'Experience': 'New', 'COUNT(*)': 7}, {'DepartmentName': 'HR', 'Experience': 'Experienced', 'COUNT(*)': 3}, {'DepartmentName': 'Engineering', 'Experience': 'New', 'COUNT(*)': 10}, {'DepartmentName': 'Engineering', 'Experience': 'Experienced', 'COUNT(*)': 5}]

6. SELECT d.DepartmentName, 'New' as Experience, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID WHERE e.HireDate > '2020-12-31' GROUP BY d.DepartmentName
Output:
[{'DepartmentName': 'HR', 'Experience': 'New', 'COUNT(*)': 3}, {'DepartmentName': 'Engineering', 'Experience': 'New', 'COUNT(*)': 5}]

**Output:**
```json
[
  {
    "query": "SELECT d.DepartmentName, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID GROUP BY d.DepartmentName",
    "chain_of_thought": "This query counts the total number of employees in each department but fails to categorize them as 'New' or 'Experienced'. This is a partial answer.",
    "score": 2
  },
  {
    "query": "SELECT CASE WHEN HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience, COUNT(*) FROM employees GROUP BY Experience",
    "chain_of_thought": "This query correctly categorizes and counts employees as 'New' or 'Experienced' but fails to break down these counts by department. This is a partial answer.",
    "score": 2
  },
  {
    "query": "SELECT d.DepartmentName, CASE WHEN e.HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID GROUP BY d.DepartmentName, Experience",
    "chain_of_thought": "This query correctly joins the tables, uses a CASE statement to categorize employees based on the hire date, and groups by both department and the new category to get the required counts. It perfectly answers the question.",
    "score": 4
  },
  {
    "query": "SELECT d.DepartmentName, e.FirstName, e.LastName, CASE WHEN e.HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID",
    "chain_of_thought": "This query correctly categorizes each individual employee but fails to perform the aggregation (COUNT(*)) to show the number of employees in each category. This is a partial answer.",
    "score": 2
  },
  {
    "query": "SELECT d.DepartmentName, CASE WHEN e.HireDate < '2021-01-01' THEN 'New' ELSE 'Experienced' END AS Experience, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID GROUP BY d.DepartmentName, Experience",
    "chain_of_thought": "This query has a critical logic flaw. e.HireDate < '2021-01-01' is the same as being hired in or before 2020, so it incorrectly labels 'Experienced' employees as 'New'.",
    "score": 1
  },
  {
    "query": "SELECT d.DepartmentName, 'New' as Experience, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID WHERE e.HireDate > '2020-12-31' GROUP BY d.DepartmentName",
    "chain_of_thought": "This query incorrectly uses a WHERE clause to filter for only 'New' employees. As a result, it completely omits the counts for 'Experienced' employees, failing to answer the full question.",
    "score": 1
  }
]
```

**Example 3:**

**Question:** "The average duration can be calculated using the AVG() function on the Duration column."

**Schema:**
```sql
CREATE TABLE singer (
  Singer_ID INT PRIMARY KEY,
  Name VARCHAR(255)
);

CREATE TABLE song (
  Song_ID INT PRIMARY KEY,
  Title VARCHAR(255),
  Singer_ID INT,
  Duration INT,
  FOREIGN KEY (Singer_ID) REFERENCES singer(Singer_ID)
);
```

**Hint:** "Join singer and song tables, group by singer, and use the AVG() function on the duration."

**Queries:**
1. SELECT T1.Name , AVG(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID GROUP BY T1.Name
Output:
[{'Name': 'SingerA', 'AVG(T2.Duration)': 450.0}, {'Name': 'SingerB', 'AVG(T2.Duration)': 300.0}]

2. SELECT T1.Name FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID
Output:
[{'Name': 'SingerA'}, {'Name': 'SingerA'}, {'Name': 'SingerB'}]

3. SELECT AVG(Duration) FROM song
Output:
[{'AVG(Duration)': 375.0}]

4. SELECT T1.Name , T2.Duration FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID
Output:
[{'Name': 'SingerA', 'Duration': 400}, {'Name': 'SingerA', 'Duration': 500}, {'Name': 'SingerB', 'Duration': 300}]

5. SELECT T1.Name , SUM(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID GROUP BY T1.Name
Output:
[{'Name': 'SingerA', 'SUM(T2.Duration)': 900}, {'Name': 'SingerB', 'SUM(T2.Duration)': 300}]

**Output:**
```json
[
  {
    "query": "SELECT T1.Name ,  AVG(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID GROUP BY T1.Name",
    "chain_of_thought": "This query correctly joins the tables, groups by singer name, and calculates the average duration. The INNER JOIN correctly filters for singers with at least one song. It perfectly answers the question.",
    "score": 4
  },
  {
    "query": "SELECT T1.Name FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID",
    "chain_of_thought": "This query joins the tables but is missing the aggregation (AVG) and the GROUP BY clause. It only returns a list of singers for each song they have. This is a poor answer.",
    "score": 1
  },
  {
    "query": "SELECT AVG(Duration) FROM song",
    "chain_of_thought": "This query calculates the average duration of all songs in the table, but it doesn't break it down by singer. This is a partial answer.",
    "score": 2
  },
  {
    "query": "SELECT T1.Name ,  T2.Duration FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID",
    "chain_of_thought": "This query returns the duration for each individual song alongside the singer's name but misses the aggregation (AVG) and GROUP BY. It does not calculate the average.",
    "score": 1
  },
  {
    "query": "SELECT T1.Name ,  SUM(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID GROUP BY T1.Name",
    "chain_of_thought": "This query correctly joins and groups, but it calculates the SUM of durations instead of the AVG. This answers a different question.",
    "score": 1
  }
]
```
---
"""

NOHINT_FEWSHOT_EXAMPLES = """
---

**Example 1:**

**Question:** "Find the names of all students who are enrolled in more than 3 courses."

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

**Queries:**
1. SELECT student_name FROM students WHERE student_id IN (SELECT student_id FROM enrollments GROUP BY student_id HAVING COUNT(course_id) > 3)
Output:
[{'student_name': 'Alice'}, {'student_name': 'Bob'}]

2. SELECT COUNT(T1.student_id) FROM students AS T1
Output:
[{'COUNT(T1.student_id)': 10}]

3. SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id
Output:
[{'student_name': 'Alice'}, {'student_name': 'Bob'}, {'student_name': 'Charlie'}, {'student_name': 'David'}]

4. SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3
Output:
[{'student_name': 'Alice'}, {'student_name': 'Bob'}]

5. SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3
Output:
[{'student_name': 'Alice'}, {'student_name': 'Bob'}]

6. SELECT T1.student_name, count(*) FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3
Output:
[{'student_name': 'Alice', 'count(*)': 4}, {'student_name': 'Bob', 'count(*)': 5}]

7. SELECT T1.student_name FROM students AS T1
Output:
[{'student_name': 'Alice'}, {'student_name': 'Bob'}, {'student_name': 'Charlie'}, {'student_name': 'David'}, {'student_name': 'Eve'}]

8. SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  =  3
Output:
[{'student_name': 'Charlie'}]

9. SELECT T1.course_name FROM courses AS T1 JOIN enrollments AS T2 ON T1.course_id  =  T2.course_id GROUP BY T1.course_name HAVING count(*)  >  3
Output:
[{'course_name': 'Introduction to Programming'}]

**Output:**
```json
[
  {
    "query": "SELECT student_name FROM students WHERE student_id IN (SELECT student_id FROM enrollments GROUP BY student_id HAVING COUNT(course_id) > 3)",
    "chain_of_thought": "Uses a subquery to achieve the same result. It correctly answers the question, but without `DISTINCT` it may produce duplicates.",
    "score": 3
  },
  {
    "query": "SELECT COUNT(T1.student_id) FROM students AS T1",
    "chain_of_thought": "Only counts the total number of students. This is irrelevant to the question.",
    "score": 1
  },
  {
    "query": "SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id",
    "chain_of_thought": "Joins the tables but doesn't group or filter. This only partially addresses the question.",
    "score": 2
  },
  {
    "query": "SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3",
    "chain_of_thought": "This query is missing the `DISTINCT` keyword, which will lead to duplicate results. The query is otherwise correct.",
    "score": 3
  },
  {
    "query": "SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3",
    "chain_of_thought": "Correctly joins `students` and `enrollments`, groups by `student_name`, and filters for students with more than 3 courses. This is a perfect answer.",
    "score": 4
  },
  {
    "query": "SELECT T1.student_name, count(*) FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3",
    "chain_of_thought": "This query returns an extra column (the count), which was not requested.",
    "score": 3
  },
  {
    "query": "SELECT T1.student_name FROM students AS T1",
    "chain_of_thought": "This query only returns the student names without any filtering or aggregation.",
    "score": 1
  },
  {
    "query": "SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  =  3",
    "chain_of_thought": "This query uses `=` instead of `>` in the `HAVING` clause, which is a critical error.",
    "score": 1
  },
  {
    "query": "SELECT T1.course_name FROM courses AS T1 JOIN enrollments AS T2 ON T1.course_id  =  T2.course_id GROUP BY T1.course_name HAVING count(*)  >  3",
    "chain_of_thought": "This query is completely irrelevant as it is querying courses instead of students.",
    "score": 0
  }
]
```

---

**Example 2:**

**Question:** "Find the title of the movie with the highest budget in the year 2012 and list who wrote the movies."

**Schema:**
```sql
CREATE TABLE movie (
  MId INT PRIMARY KEY,
  Title VARCHAR(255),
  Year INT,
  Director VARCHAR(255),
  Budget DECIMAL(10, 2),
  Revenue DECIMAL(10, 2)
);

CREATE TABLE writer (
  WId INT PRIMARY KEY,
  Name VARCHAR(255)
);

CREATE TABLE movie_writer (
  MId INT,
  WId INT,
  FOREIGN KEY (MId) REFERENCES movie(MId),
  FOREIGN KEY (WId) REFERENCES writer(WId)
);
```

**Queries:**
1. SELECT T1.Title FROM movie AS T1 WHERE T1.Year  =  2012 ORDER BY T1.Budget DESC LIMIT 1
Output:
[{'Title': 'The Avengers'}]

2. SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012
Output:
[{'Title': 'The Avengers', 'Name': 'Joss Whedon'}, {'Title': 'Skyfall', 'Name': 'Neal Purvis'}]

3. SELECT MAX(Budget) FROM movie WHERE Year  =  2012
Output:
[{'MAX(Budget)': 220000000}]

4. SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012 AND T1.Budget  =  (SELECT min(Budget) FROM movie WHERE Year  =  2012)
Output:
[]

5. SELECT T1.Title FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012
Output:
[{'Title': 'The Avengers'}, {'Title': 'Skyfall'}]

6. SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2013 AND T1.Budget  =  (SELECT MAX(Budget) FROM movie WHERE Year  =  2012)
Output:
[]

**Output:**
```json
[
  {
    "query": "SELECT T1.Title FROM movie AS T1 WHERE T1.Year  =  2012 ORDER BY T1.Budget DESC LIMIT 1",
    "chain_of_thought": "This query finds the title of the movie with the highest budget in 2012, but it doesn't return the writer's name. This is a partial answer, missing a column.",
    "score": 2
  },
  {
    "query": "SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012",
    "chain_of_thought": "This query returns all movies from 2012 with their writers, but it doesn't find the one with the highest budget. This is a partial answer.",
    "score": 2
  },
  {
    "query": "SELECT MAX(Budget) FROM movie WHERE Year  =  2012",
    "chain_of_thought": "This query only returns the maximum budget for movies in 2012, not the title or the writer. This is a partial answer.",
    "score": 2
  },
  {
    "query": "SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012 AND T1.Budget  =  (SELECT min(Budget) FROM movie WHERE Year  =  2012)",
    "chain_of_thought": "This query is incorrect because it uses `min(Budget)` instead of `MAX(Budget)`.",
    "score": 1
  },
  {
    "query": "SELECT T1.Title FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012",
    "chain_of_thought": "This query is missing the writer's name and the budget filter.",
    "score": 1
  },
  {
    "query": "SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2013 AND T1.Budget  =  (SELECT MAX(Budget) FROM movie WHERE Year  =  2012)",
    "chain_of_thought": "This query has a mismatch in the year filter, which makes it incorrect.",
    "score": 1
  }
]
```

**Example 3:**

**Question:** "The average duration can be calculated using the AVG() function on the Duration column."

**Schema:**
```sql
CREATE TABLE singer (
  Singer_ID INT PRIMARY KEY,
  Name VARCHAR(255)
);

CREATE TABLE song (
  Song_ID INT PRIMARY KEY,
  Title VARCHAR(255),
  Singer_ID INT,
  Duration INT,
  FOREIGN KEY (Singer_ID) REFERENCES singer(Singer_ID)
);
```

**Queries:**
1. SELECT T1.Name , AVG(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID GROUP BY T1.Name
Output:
[{'Name': 'SingerA', 'AVG(T2.Duration)': 450.0}, {'Name': 'SingerB', 'AVG(T2.Duration)': 300.0}]

2. SELECT T1.Name FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID
Output:
[{'Name': 'SingerA'}, {'Name': 'SingerA'}, {'Name': 'SingerB'}]

3. SELECT AVG(Duration) FROM song
Output:
[{'AVG(Duration)': 375.0}]

4. SELECT T1.Name , T2.Duration FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID
Output:
[{'Name': 'SingerA', 'Duration': 400}, {'Name': 'SingerA', 'Duration': 500}, {'Name': 'SingerB', 'Duration': 300}]

5. SELECT T1.Name , SUM(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID GROUP BY T1.Name
Output:
[{'Name': 'SingerA', 'SUM(T2.Duration)': 900}, {'Name': 'SingerB', 'SUM(T2.Duration)': 300}]

**Output:**
```json
[
  {
    "query": "SELECT T1.Name ,  AVG(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID GROUP BY T1.Name",
    "chain_of_thought": "This query correctly joins the tables, groups by singer name, and calculates the average duration. The INNER JOIN correctly filters for singers with at least one song. It perfectly answers the question.",
    "score": 4
  },
  {
    "query": "SELECT T1.Name FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID",
    "chain_of_thought": "This query joins the tables but is missing the aggregation (AVG) and the GROUP BY clause. It only returns a list of singers for each song they have. This is a poor answer.",
    "score": 1
  },
  {
    "query": "SELECT AVG(Duration) FROM song",
    "chain_of_thought": "This query calculates the average duration of all songs in the table, but it doesn't break it down by singer. This is a partial answer.",
    "score": 2
  },
  {
    "query": "SELECT T1.Name ,  T2.Duration FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID",
    "chain_of_thought": "This query returns the duration for each individual song alongside the singer's name but misses the aggregation (AVG) and GROUP BY. It does not calculate the average.",
    "score": 1
  },
  {
    "query": "SELECT T1.Name ,  SUM(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID GROUP BY T1.Name",
    "chain_of_thought": "This query correctly joins and groups, but it calculates the SUM of durations instead of the AVG. This answers a different question.",
    "score": 1
  }
]
```
---
"""

QUERY_SCORING_PROMPT = """
You are an expert in text-to-SQL. Your task is to evaluate a list of SQL queries based on a given question, database schema, a hint and a set of evaluation criteria. You must assign a score from 0 to 4 to each query, where 4 is the best score.

**Scoring Points (1-4):**
- **4 (Excellent):** The query directly and completely answers the question, and makes optimal use of the provided schema and hint.
- **3 (Good):** The query answers the question well, but might have minor issues like not fully utilizing the hint or having a slightly inefficient structure.
- **2 (Fair):** The query only partially answers the question or has significant inefficiencies.
- **1 (Poor):** The query does not answer the question in any meaningful way.

**Non-exhaustive list of score reducing criteria:
1. **Column Selection:**
    - The SQL is selecting more columns than required in the criteria.
    - The SQL is WRONGFULLY formatting columns in the response that provide state information for better readability when it's not required in the hint or question.(e.g., returning 'Yes' or 'No' instead of a column indicating the requested state)

2. **Table Relationships:**
    - The SQL is joining more tables than necessary or is not joining all the required tables to answer the question.
    - The SQL is not using the correct foreign keys when joining the tables(provided in the schema)

3. **Filtering Conditions:**
    - The SQL is not correctly filtering based on all the conditions provided in the question and evaluation criteria.
    - The SQL query is filtering based on extra conditions not provided in the question and evaluation criteria.
    - The SQL query uses incorrect comparison operators or incorrect aggregation operators('<' instead of '=' or 'COUNT' instead of 'AVG' or calculating average through division).
    - The SQL query uses incorrect literal values for filtering out the results (e.g filters for movies after 2013 when query asks for movies after 2012).
    - The SQL query does not handle NULL values properly when they can affect the results(e.g ordering by NULL values, selectin NULL values etc). NULLABLE in the schema indicates a column's value can be null.

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

9. **Output verification**
    - The SQL query is completely correct, however the output might not be correct(e.g., None response from a field when a valid value is expected).

**Instructions:**
1.  Carefully analyze the question, schema, and hint.
2.  Evaluate the correctness and relevance of each query in the batch using the list of score reduction criteria provided above.
3.  The “Relevant Entities” section lists database columns that match literals from the question or hint. It does not mean all of them are relevant to answering this question.
    You can refer to these as hints to understand what are some of the correct columns for filtering in the query based on a given literal from the question or hint.
4.  Assign a score from 1 to 4 for each query based on how many of the violations in the scoring criteria apply.
5.  Provide a short reasoning for your scoring for each query.

**Output Format**
- Provide the output in the following JSON format, with one entry for each query in the batch:
  ```json
  [
      {
        "chain_of_thought": "<SHORT reasoning logic for scoring query 1>",
        "score": <score number 0-4 for query 1>
      },
      {
        "chain_of_thought": "<SHORT reasoning logic for scoring query 2>",
        "score": <score number 0-4 for query 2>
      }
  ]
  ```
- Make sure to not use double quotes inside double quotes because it causes problems with the parsing.

Here are some examples:
{FEWSHOT_EXAMPLES}

Given the following information, score the list of queries.

**Question:** "{QUESTION}"

**Hint:**
{HINT}

**Schema:**
{DATABASE_SCHEMA}

** Relevant Entities **
{RELEVANT_ENTITIES}

**Queries:**
{QUERIES}

**Output:**
"""