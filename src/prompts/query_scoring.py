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

**Output:**
```json
{
  "scores": [
    {
      "query": "SELECT student_name FROM students WHERE student_id IN (SELECT student_id FROM enrollments GROUP BY student_id HAVING COUNT(course_id) > 3)",
      "score": 3,
      "chain_of_thought": "Uses a subquery to achieve the same result. It correctly answers the question, but without `DISTINCT` it may produce duplicates."
    },
    {
      "query": "SELECT COUNT(T1.student_id) FROM students AS T1",
      "score": 1,
      "chain_of_thought": "Only counts the total number of students. This is irrelevant to the question."
    },
    {
      "query": "SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id",
      "score": 2,
      "chain_of_thought": "Joins the tables but doesn't group or filter. This only partially addresses the question."
    },
    {
      "query": "SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3",
      "score": 3,
      "chain_of_thought": "This query is missing the `DISTINCT` keyword, which will lead to duplicate results. The query is otherwise correct."
    },
    {
      "query": "SELECT DISTINCT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3",
      "score": 4,
      "chain_of_thought": "Correctly joins `students` and `enrollments`, groups by `student_name`, and filters for students with more than 3 courses. This is a perfect answer."
    },
    {
      "query": "SELECT T1.student_name, count(*) FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  >  3",
      "score": 3,
      "chain_of_thought": "This query returns an extra column (the count), which was not requested."
    },
    {
      "query": "SELECT T1.student_name FROM students AS T1",
      "score": 1,
      "chain_of_thought": "This query only returns the student names without any filtering or aggregation."
    },
    {
      "query": "SELECT T1.student_name FROM students AS T1 JOIN enrollments AS T2 ON T1.student_id  =  T2.student_id GROUP BY T1.student_name HAVING count(*)  =  3",
      "score": 1,
      "chain_of_thought": "This query uses `=` instead of `>` in the `HAVING` clause, which is a critical error."
    },
    {
      "query": "SELECT T1.course_name FROM courses AS T1 JOIN enrollments AS T2 ON T1.course_id  =  T2.course_id GROUP BY T1.course_name HAVING count(*)  >  3",
      "score": 0,
      "chain_of_thought": "This query is completely irrelevant as it is querying courses instead of students."
    }
  ]
}
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

**Hint:** "The highest budget can be found using MAX(Budget)."

**Output:**
```json
{
  "scores": [
    {
      "query": "SELECT T1.Title FROM movie AS T1 WHERE T1.Year  =  2012 ORDER BY T1.Budget DESC LIMIT 1",
      "score": 2,
      "chain_of_thought": "This query finds the title of the movie with the highest budget in 2012, but it doesn't return the writer's name. This is a partial answer, missing a column."
    },
    {
      "query": "SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012",
      "score": 2,
      "chain_of_thought": "This query returns all movies from 2012 with their writers, but it doesn't find the one with the highest budget. This is a partial answer."
    },
    {
      "query": "SELECT MAX(Budget) FROM movie WHERE Year  =  2012",
      "score": 2,
      "chain_of_thought": "This query only returns the maximum budget for movies in 2012, not the title or the writer. This is a partial answer."
    },
    {
      "query": "SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012 AND T1.Budget  =  (SELECT min(Budget) FROM movie WHERE Year  =  2012)",
      "score": 1,
      "chain_of_thought": "This query is incorrect because it uses `min(Budget)` instead of `MAX(Budget)`."
    },
    {
      "query": "SELECT T1.Title FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012",
      "score": 1,
      "chain_of_thought": "This query is missing the writer's name and the budget filter."
    },
    {
      "query": "SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2013 AND T1.Budget  =  (SELECT MAX(Budget) FROM movie WHERE Year  =  2012)",
      "score": 1,
      "chain_of_thought": "This query has a mismatch in the year filter, which makes it incorrect."
    },
    {
      "query": "SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012 AND T1.Revenue  =  (SELECT MAX(Revenue) FROM movie WHERE Year  =  2012)",
      "score": 1,
      "chain_of_thought": "This query is looking for the highest revenue, not budget."
    },
    {
      "query": "SELECT T1.Title, T3.Name FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012 AND T1.Budget  =  (SELECT MAX(Budget) FROM movie WHERE Year  =  2012)",
      "score": 4,
      "chain_of_thought": "This query correctly joins the three tables, filters by year, and uses a subquery to find the movie with the highest budget. It also returns the writer's name. It perfectly answers the question."
    },
    {
      "query": "SELECT T1.Title, T3.Name, T1.Budget FROM movie AS T1 JOIN movie_writer AS T2 ON T1.MId  =  T2.MId JOIN writer AS T3 ON T2.WId  =  T3.WId WHERE T1.Year  =  2012 ORDER BY T1.Budget DESC",
      "score": 2,
      "chain_of_thought": "This query returns extra information (budget) and doesn't filter for the highest budget."
    }
  ]
}
```

**Example 3:**

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

**Output:**
```json
{
  "scores": [
    {
      "query": "SELECT d.DepartmentName, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID GROUP BY d.DepartmentName",
      "score": 2,
      "chain_of_thought": "This query counts the total number of employees in each department but fails to categorize them as 'New' or 'Experienced'. This is a partial answer."
    },
    {
      "query": "SELECT CASE WHEN HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience, COUNT(*) FROM employees GROUP BY Experience",
      "score": 2,
      "chain_of_thought": "This query correctly categorizes and counts employees as 'New' or 'Experienced' but fails to break down these counts by department. This is a partial answer."
    },
    {
      "query": "SELECT d.DepartmentName, CASE WHEN e.HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID GROUP BY d.DepartmentName, Experience",
      "score": 4,
      "chain_of_thought": "This query correctly joins the tables, uses a CASE statement to categorize employees based on the hire date, and groups by both department and the new category to get the required counts. It perfectly answers the question."
    },
    {
      "query": "SELECT d.DepartmentName, e.FirstName, e.LastName, CASE WHEN e.HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID",
      "score": 2,
      "chain_of_thought": "This query correctly categorizes each individual employee but fails to perform the aggregation (COUNT(*)) to show the number of employees in each category. This is a partial answer."
    },
    {
      "query": "SELECT d.DepartmentName, CASE WHEN e.HireDate < '2021-01-01' THEN 'New' ELSE 'Experienced' END AS Experience, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID GROUP BY d.DepartmentName, Experience",
      "score": 1,
      "chain_of_thought": "This query has a critical logic flaw. e.HireDate < '2021-01-01' is the same as being hired in or before 2020, so it incorrectly labels 'Experienced' employees as 'New'."
    },
    {
      "query": "SELECT d.DepartmentName, 'New' as Experience, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID WHERE e.HireDate > '2020-12-31' GROUP BY d.DepartmentName",
      "score": 1,
      "chain_of_thought": "This query incorrectly uses a WHERE clause to filter for only 'New' employees. As a result, it completely omits the counts for 'Experienced' employees, failing to answer the full question."
    },
    {
      "query": "SELECT d.DepartmentID, d.DepartmentName, CASE WHEN e.HireDate > '2020-12-31' THEN 'New' ELSE 'Experienced' END AS Experience, COUNT(*) FROM employees AS e JOIN departments AS d ON e.DepartmentID = d.DepartmentID GROUP BY d.DepartmentName, Experience, d.DepartmentID",
      "score": 3,
      "chain_of_thought": "This query provides the correct answer but also includes the DepartmentID, an extra column that was not requested in the output. This is a minor inefficiency."
    },
    {
      "query": "SELECT COUNT(DISTINCT DepartmentName) FROM departments",
      "score": 0,
      "chain_of_thought": "This query is completely irrelevant. It only counts the number of distinct departments and has nothing to do with employees or their hire dates."
    }
  ]
}
```

**Example 4:**

**Question:** "Find the names of singers who have a song that has a duration of more than 400."

**Schema:**
```sql
CREATE TABLE singer (
  Singer_ID INT PRIMARY KEY,
  Name VARCHAR(255),
  Country VARCHAR(255),
  Song_Name VARCHAR(255),
  Song_release_year INT,
  Age INT,
  Is_male BOOLEAN
);

CREATE TABLE song (
  Song_ID INT PRIMARY KEY,
  Title VARCHAR(255),
  Singer_ID INT,
  Duration INT,
  FOREIGN KEY (Singer_ID) REFERENCES singer(Singer_ID)
);
```

**Hint:** "The condition for the song is Duration > 400 in the song table."

**Output:**
```json
{
  "scores": [
    {
      "query": "SELECT T1.Name FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID WHERE T2.Duration  >  400",
      "score": 3,
      "chain_of_thought": "This query is correct in its logic but is missing the DISTINCT keyword. This will lead to duplicate singer names if a singer has multiple songs over 400 duration."
    },
    {
      "query": "SELECT T1.Name, T2.Title FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID WHERE T2.Duration  >  400",
      "score": 2,
      "chain_of_thought": "This query correctly finds the singers but returns an extra, unrequested column (Title). This makes it only partially correct."
    },
    {
      "query": "SELECT Name FROM singer WHERE Singer_ID IN (SELECT Singer_ID FROM song WHERE Duration > 400)",
      "score": 3,
      "chain_of_thought": "This query uses a subquery to correctly identify the singers. However, like query #2, it lacks DISTINCT and will produce duplicate names."
    },
    {
      "query": "SELECT COUNT(DISTINCT T1.Name) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID WHERE T2.Duration  >  400",
      "score": 2,
      "chain_of_thought": "This query correctly identifies the singers but returns a COUNT of them instead of their names. It answers \"how many\" instead of \"who\". This is a partial answer."
    },
    {
      "query": "SELECT DISTINCT T1.Name FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID WHERE T2.Duration  <  400",
      "score": 1,
      "chain_of_thought": "This query contains a critical logical error. It uses < 400 instead of > 400, finding singers with short songs, which is the opposite of what was asked."
    },
    {
      "query": "SELECT DISTINCT T1.Name FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID",
      "score": 2,
      "chain_of_thought": "This query correctly joins the tables but completely omits the WHERE clause for filtering by duration. It finds all singers who have any song, not just long ones."
    },
    {
      "query": "SELECT Name FROM singer WHERE Age > 40",
      "score": 0,
      "chain_of_thought": "This query is irrelevant. It queries the singer table on a condition (Age > 40) that has nothing to do with song duration."
    },
    {
      "query": "SELECT T2.Title FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID WHERE T2.Duration  >  400",
      "score": 1,
      "chain_of_thought": "This query correctly filters for the right songs but returns the song Title instead of the singer's Name as requested."
    },
    {
      "query": "SELECT DISTINCT T1.Name FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID WHERE T2.Duration  >  400",
      "score": 4,
      "chain_of_thought": "This query correctly joins the tables, filters by duration, and uses DISTINCT to return unique singer names as requested. It is a perfect answer."
    }
  ]
}
```

---

**Example 5:**

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
2. SELECT T1.Name FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID
3. SELECT AVG(Duration) FROM song
4. SELECT T1.Name , T2.Duration FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID
5. SELECT T1.Name , SUM(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID = T2.Singer_ID GROUP BY T1.Name

**Output:**
```json
{
  "scores": [
    {
      "query": "SELECT T1.Name ,  AVG(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID GROUP BY T1.Name",
      "score": 4,
      "chain_of_thought": "This query correctly joins the tables, groups by singer name, and calculates the average duration. The INNER JOIN correctly filters for singers with at least one song. It perfectly answers the question."
    },
    {
      "query": "SELECT T1.Name FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID",
      "score": 1,
      "chain_of_thought": "This query joins the tables but is missing the aggregation (AVG) and the GROUP BY clause. It only returns a list of singers for each song they have. This is a poor answer."
    },
    {
      "query": "SELECT AVG(Duration) FROM song",
      "score": 2,
      "chain_of_thought": "This query calculates the average duration of all songs in the table, but it doesn't break it down by singer. This is a partial answer."
    },
    {
      "query": "SELECT T1.Name ,  T2.Duration FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID",
      "score": 1,
      "chain_of_thought": "This query returns the duration for each individual song alongside the singer's name but misses the aggregation (AVG) and GROUP BY. It does not calculate the average."
    },
    {
      "query": "SELECT T1.Name ,  SUM(T2.Duration) FROM singer AS T1 JOIN song AS T2 ON T1.Singer_ID  =  T2.Singer_ID GROUP BY T1.Name",
      "score": 1,
      "chain_of_thought": "This query correctly joins and groups, but it calculates the SUM of durations instead of the AVG. This answers a different question."
    }
  ]
}
```

---
**Example 6:**

**Question:** "For each product category, find the name of the customer who spent the most money in that category during the year 2024. Show the product category, the customer's name, and the total amount they spent in that category."

**Schema:**
CREATE TABLE customers (
  CustomerID INT PRIMARY KEY,
  CustomerName VARCHAR(255),
  Country VARCHAR(255)
);

CREATE TABLE products (
  ProductID INT PRIMARY KEY,
  ProductName VARCHAR(255),
  Category VARCHAR(255)
);

CREATE TABLE orders (
  OrderID INT PRIMARY KEY,
  CustomerID INT,
  OrderDate DATE,
  FOREIGN KEY (CustomerID) REFERENCES customers(CustomerID)
);

CREATE TABLE order_details (
  OrderDetailID INT PRIMARY KEY,
  OrderID INT,
  ProductID INT,
  Quantity INT,
  Price DECIMAL(10, 2),
  FOREIGN KEY (OrderID) REFERENCES orders(OrderID),
  FOREIGN KEY (ProductID) REFERENCES products(ProductID)
);

**Hint:** "Total spending is the sum of Quantity * Price. The year can be extracted from OrderDate. You can find the highest spending per category using a window function, a correlated subquery, or by joining an aggregated list to itself."

**Queries:**
1. SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName ORDER BY p.Category, TotalSpent DESC
2. SELECT T1.Category, T1.CustomerName, T1.TotalSpent FROM (SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName) AS T1 WHERE T1.TotalSpent = (SELECT MAX(TotalSpent) FROM (SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName) AS T2 WHERE T2.Category = T1.Category)
3. SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID GROUP BY p.Category, c.CustomerName
4. WITH CategorySpending AS (SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent, ROW_NUMBER() OVER (PARTITION BY p.Category ORDER BY SUM(od.Quantity * od.Price) DESC) as rn FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName) SELECT Category, CustomerName, TotalSpent FROM CategorySpending WHERE rn = 1
5. WITH CategorySpending AS (SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent, RANK() OVER (PARTITION BY p.Category ORDER BY SUM(od.Quantity * od.Price) DESC) as rn FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName) SELECT Category, CustomerName, TotalSpent FROM CategorySpending WHERE rn = 1
6. SELECT p.Category, c.CustomerName, SUM(od.Quantity) AS TotalQuantity FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName
7. WITH CustomerCategorySpending AS (SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName) SELECT s1.Category, s1.CustomerName, s1.TotalSpent FROM CustomerCategorySpending s1 LEFT JOIN CustomerCategorySpending s2 ON s1.Category = s2.Category AND s1.TotalSpent < s2.TotalSpent WHERE s2.CustomerName IS NULL
8. SELECT c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY c.CustomerName ORDER BY TotalSpent DESC LIMIT 1

**Output:**
```json
{
  "scores": [
    {
      "query": "SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName ORDER BY p.Category, TotalSpent DESC",
      "score": 2,
      "chain_of_thought": "This query correctly calculates the spending for each customer in each category for 2024, but it does not filter to show only the top spender. It returns a list of all spenders, sorted, leaving the final filtering step to the user."
    },
    {
      "query": "SELECT T1.Category, T1.CustomerName, T1.TotalSpent FROM (SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName) AS T1 WHERE T1.TotalSpent = (SELECT MAX(TotalSpent) FROM (SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName) AS T2 WHERE T2.Category = T1.Category)",
      "score": 4,
      "chain_of_thought": "This is another perfect solution that uses a more traditional correlated subquery. It calculates the total spending for each customer per category, and then for each row, it checks if that spending is equal to the maximum spending for that same category. It's less performant than a window function but is logically sound and fully answers the question."
    },
    {
      "query": "SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID GROUP BY p.Category, c.CustomerName",
      "score": 1,
      "chain_of_thought": "This query calculates total spending per customer per category but omits the crucial WHERE clause to filter for the year 2024. This produces an incorrect result based on all-time data."
    },
    {
      "query": "WITH CategorySpending AS (SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent, ROW_NUMBER() OVER (PARTITION BY p.Category ORDER BY SUM(od.Quantity * od.Price) DESC) as rn FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName) SELECT Category, CustomerName, TotalSpent FROM CategorySpending WHERE rn = 1",
      "score": 3,
      "chain_of_thought": "This query is very close to perfect, but it uses ROW_NUMBER() instead of RANK(). If there is a tie for the top spender in a category, ROW_NUMBER() will arbitrarily pick one to be rank 1, while RANK() would correctly assign both rank 1. This means it could fail to return all correct results in the case of a tie."
    },
    {
      "query": "WITH CategorySpending AS (SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent, RANK() OVER (PARTITION BY p.Category ORDER BY SUM(od.Quantity * od.Price) DESC) as rn FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName) SELECT Category, CustomerName, TotalSpent FROM CategorySpending WHERE rn = 1",
      "score": 4,
      "chain_of_thought": "This is a perfect solution using a modern approach. It correctly joins all tables, filters by year, calculates total spending, and uses a CTE with the RANK() window function to correctly identify the top spender in each category. RANK() correctly handles ties."
    },
    {
      "query": "SELECT p.Category, c.CustomerName, SUM(od.Quantity) AS TotalQuantity FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName",
      "score": 1,
      "chain_of_thought": "This query has a critical logical flaw. It calculates the SUM of Quantity instead of the total spending (Quantity * Price), finding the customer who bought the most items, not the one who spent the most money."
    },
    {
      "query": "WITH CustomerCategorySpending AS (SELECT p.Category, c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID JOIN products p ON od.ProductID = p.ProductID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY p.Category, c.CustomerName) SELECT s1.Category, s1.CustomerName, s1.TotalSpent FROM CustomerCategorySpending s1 LEFT JOIN CustomerCategorySpending s2 ON s1.Category = s2.Category AND s1.TotalSpent < s2.TotalSpent WHERE s2.CustomerName IS NULL",
      "score": 4,
      "chain_of_thought": "This is a third, clever, and completely valid solution. It first calculates all spending totals, then uses a LEFT JOIN to join that result set to itself. It looks for rows where no other customer in the same category had a higher spending (s2.CustomerName IS NULL). This correctly isolates the top spender(s) in each category."
    },
    {
      "query": "SELECT c.CustomerName, SUM(od.Quantity * od.Price) AS TotalSpent FROM customers c JOIN orders o ON c.CustomerID = o.CustomerID JOIN order_details od ON o.OrderID = od.OrderID WHERE STRFTIME('%Y', o.OrderDate) = '2024' GROUP BY c.CustomerName ORDER BY TotalSpent DESC LIMIT 1",
      "score": 2,
      "chain_of_thought": "This query finds the single top customer across all categories combined, not the top spender within each category as requested. It fails to meet the core requirement of the question."
    }
  ]
}
```

---
"""

QUERY_SCORING_PROMPT = """
You are an expert in text-to-SQL. Your task is to evaluate a list of SQL queries based on a given question, database schema, a hint and a set of evaluation criteria. You must assign a score from 0 to 4 to each query, where 4 is the best score.

**Scoring Criteria (0-4):**
- **4 (Excellent):** The query directly and completely answers the question, and makes optimal use of the provided schema and hint.
- **3 (Good):** The query answers the question well, but might have minor issues like not fully utilizing the hint or having a slightly inefficient structure.
- **2 (Fair):** The query only partially answers the question or has significant inefficiencies.
- **1 (Poor):** The query does not answer the question in any meaningful way.
- **0 (Irrelevant):** The query is completely irrelevant to the question.

**Instructions:**
1.  Carefully analyze the question, schema, hint and criteria.
2.  For each query, evaluate its correctness and relevance.
3.  Assign a score from 0 to 4 based on the scoring criteria.
4.  Provide a step-by-step reasoning for your score for each query.

**Output Format**
Provide the output in the following format:
```json
{{
  "scores": [
    {{
      "query": "<SQL Query>",
      "score": <score number 0-4>,
      "chain_of_thought": "<reasoning logic for scoring"
    }}
  ]
}}
```

Here are some examples:
{FEWSHOT_EXAMPLES}


Given the following information, score the list of queries.

**Question:** "{QUESTION}"

**Schema:**
{DATABASE_SCHEMA}

**Hint:** "{HINT}"

**Queries:**
{QUERIES}

**Output:**
"""