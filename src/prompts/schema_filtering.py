
FEWSHOT_EXAMPLES="""
Example 1: Multi-table join with filtering and counting
Demonstrates identifying columns needed for filtering across multiple conditions and performing aggregation operations.

【DB_ID】<db_name>
【Schema】
# Table: movies
[
(movie_id: INTEGER, Primary Key, unique identifier for movies, Examples: [1, 2, 3]),
(movie_title: TEXT, Name of the movie, Examples: [La Antena, Sunset Boulevard, Citizen Kane]),
(movie_release_year: INTEGER, Release year of the movie, Examples: [1945, 2007, 1924]),
(director_name: TEXT, Full Name of the movie director, Examples: [Stanley Kubrick, Erich von Stroheim, Francis Ford Coppola]),
(movie_popularity: INTEGER, Number of Mubi users who love the movie, Examples: [1500, 850, 2000])
]

# Table: ratings_users
[
(user_id: INTEGER, Primary Key, unique identifier for users, Examples: [101, 102, 103]),
(movie_id: INTEGER, Foreign Key to movies.movie_id, Examples: [1, 2, 3]),
(rating_score: INTEGER, Rating score ranging from 1 to 5, Examples: [3, 5, 1]),
(user_has_payment_method: INTEGER, whether user was paying subscriber, Examples: [0, 1]),
(rating_timestamp_utc: TEXT, timestamp of rating, Examples: [2020-04-15, 2020-04-20])
]

Foreign keys: ratings_users.movie_id = movies.movie_id
Question: How many users, who were a paying subscriber when they rated the movie, gave the movie that was released in 1924 and directed by Erich von Stroheim a rating score of 5?
Hint: Directed by Erich von Stroheim refers to director_name = 'Erich von Stroheim'; released in 1924 refers to movie_release_year = 1924; paying subscriber refers to user_has_payment_method = 1; rating score of 5 refers to rating_score = 5;

Response:
```json
{
  "chain_of_thought_reasoning": "To answer this question, I need to: 1) Filter movies by director 'Erich von Stroheim' and release year 1924, 2) Join with ratings to find users who rated these movies, 3) Filter for paying subscribers (user_has_payment_method = 1) and rating score of 5, 4) Count the users. The director_name and movie_release_year columns are needed to identify the specific movie. The user_has_payment_method and rating_score columns are needed to filter the ratings. The movie_id is needed to join the tables. Note: movie_title and movie_popularity are NOT needed since they're not used in filtering or output.",
  "movies": ["movie_id", "director_name", "movie_release_year"],
  "ratings_users": ["movie_id", "rating_score", "user_has_payment_method"]
}
```

---

Example 2: Filtering with specific value lookup and displaying multiple attributes
Demonstrates identifying columns needed when filtering by exact match and retrieving specific display columns.

【DB_ID】<db_name>
【Schema】
# Table: movies
[
(movie_id: INTEGER, Primary Key, unique identifier for movies, Examples: [1, 2, 3]),
(movie_title: TEXT, Name of the movie, Examples: [La Antena, Love Will Tear Us Apart, Sunset Boulevard]),
(director_name: TEXT, Full Name of the movie director, Examples: [Stanley Kubrick, Jeannot Szwarc]),
(movie_popularity: INTEGER, Number of Mubi users who love the movie, Examples: [1500, 850, 2000])
]

# Table: ratings
[
(rating_id: INTEGER, Primary Key, unique identifier for ratings, Examples: [1, 2, 3]),
(movie_id: INTEGER, Foreign Key to movies.movie_id, Examples: [1, 2, 3]),
(rating_score: INTEGER, Rating score ranging from 1 to 5, Examples: [3, 5, 1]),
(user_id: INTEGER, identifier for users, Examples: [101, 102, 103])
]

Foreign keys: ratings.movie_id = movies.movie_id
Question: List the users who gave the worst rating for movie 'Love Will Tear Us Apart'. Also show the movie's popularity.
Hint: worst rating refers to rating_score = 1;
Response:
```json
{
  "chain_of_thought_reasoning": "To answer this question, I need to: 1) Find the movie with title 'Love Will Tear Us Apart', 2) Find all ratings for this movie with score = 1, 3) List the user_ids who gave these ratings, 4) Include the movie's popularity. The movie_title column is needed to identify the specific movie. The rating_score column is needed to filter for worst ratings (score = 1). The user_id is needed to identify users. The movie_popularity is explicitly requested. The movie_id is needed to join the tables. Note: director_name is NOT needed and rating_id is NOT needed for the output.",
  "movies": ["movie_id", "movie_title", "movie_popularity"],
  "ratings": ["movie_id", "rating_score", "user_id"]
}
```

---

Example 3: Category-based aggregation with sentiment analysis across tables
Demonstrates identifying columns for both numerical aggregation (AVG) and conditional counting across joined tables.

【DB_ID】<db_name>
【Schema】
# Table: playstore
[
(app_id: INTEGER, Primary Key, unique identifier for apps, Examples: [1, 2, 3]),
(App: TEXT, Application name, Examples: [Instagram, WhatsApp, Candy Crush]),
(Category: TEXT, Category of the app, Examples: [SOCIAL, COMMUNICATION, COMICS]),
(Rating: REAL, User rating of the app, Examples: [4.5, 3.2, 4.1]),
(Price: TEXT, Price of the app, Examples: [0, $0.99, $2.99]),
(Installs: TEXT, Number of user downloads, Examples: [10,000+, 1,000,000+, 50,000+])
]

# Table: user_reviews
[
(review_id: INTEGER, Primary Key, unique identifier for reviews, Examples: [1, 2, 3]),
(app_id: INTEGER, Foreign Key to playstore.app_id, Examples: [1, 2, 3]),
(Sentiment: TEXT, Sentiment of the review, Examples: [Positive, Negative, Neutral]),
(Sentiment_Subjectivity: TEXT, Sentiment subjectivity score, Examples: [0.53, 0.3, 0.7])
]

Foreign keys: user_reviews.app_id = playstore.app_id
Question: What is the average rating of comic category apps? How many users hold positive attitude towards comic apps?
Hint: average rating = AVG(Rating where Category = 'COMICS'); number of users who hold a positive attitude towards the app refers to COUNT(Sentiment = 'Positive');
Response:
```json
{
  "chain_of_thought_reasoning": "To answer this question, I need to: 1) Filter apps by Category = 'COMICS', 2) Calculate average Rating for these apps, 3) Join with user_reviews to find reviews for comic apps, 4) Count reviews with Sentiment = 'Positive'. The Category column is needed to filter for comic apps. The Rating column is needed for the average calculation. The Sentiment column is needed to count positive attitudes. The app_id is needed to join the tables. Note: App, Price, Installs, review_id, and Sentiment_Subjectivity are NOT needed for this query.",
  "playstore": ["app_id", "Category", "Rating"],
  "user_reviews": ["app_id", "Sentiment"]
}
```

---

Example 4: Three-table join with filtering and sorting
Demonstrates navigating many-to-many relationships through junction tables and identifying sort columns.

【DB_ID】<db_name>
【Schema】
# Table: superhero
[
(id: INTEGER, Primary Key, unique identifier of the superhero, Examples: [1, 2, 3]),
(superhero_name: TEXT, name of the superhero, Examples: [Spider-Man, Batman, Superman]),
(full_name: TEXT, full name of the superhero, Examples: [Peter Parker, Bruce Wayne, Clark Kent]),
(gender_id: INTEGER, gender of the superhero, Examples: [1, 2]),
(weight_kg: INTEGER, weight of the superhero in kg, Examples: [76, 95, 107])
]

# Table: hero_power
[
(hero_id: INTEGER, Foreign Key to superhero.id, Examples: [1, 2, 3]),
(power_id: INTEGER, Foreign Key to superpower.id, Examples: [1, 2, 3])
]

# Table: superpower
[
(id: INTEGER, Primary Key, unique identifier of the superpower, Examples: [1, 2, 3]),
(power_name: TEXT, the superpower name, Examples: [Super Strength, Flight, Telepathy])
]

Foreign keys: hero_power.hero_id = superhero.id, hero_power.power_id = superpower.id
Question: List all superheroes who have 'Super Strength' power and show their weights. Sort by weight in descending order.
Hint: Super Strength power refers to power_name = 'Super Strength';
Response:
```json
{
  "chain_of_thought_reasoning": "To answer this question, I need to: 1) Find the power_id for 'Super Strength' from superpower table, 2) Find heroes who have this power from hero_power table, 3) Get hero details including names and weights from superhero table, 4) Sort by weight descending. The power_name column is needed to filter for 'Super Strength'. The superhero_name and weight_kg columns are needed for the output (display and sorting). The id, hero_id, and power_id columns are needed to join the tables. Note: full_name and gender_id are NOT needed for this query.",
  "superhero": ["id", "superhero_name", "weight_kg"],
  "hero_power": ["hero_id", "power_id"],
  "superpower": ["id", "power_name"]
}
```

---

Example 5: Date-based filtering with aggregation and MAX finding
Demonstrates identifying columns for date range filtering, conditional counting, and finding records with maximum values.

【DB_ID】<db_name>
【Schema】
# Table: lists_users
[
(list_id: INTEGER, Primary Key, unique identifier for lists, Examples: [1, 2, 3]),
(user_id: INTEGER, identifier for users, Examples: [101, 102, 103]),
(list_title: TEXT, title of the list, Examples: [My Favorites, Action Movies, Classics]),
(list_creation_date_utc: TEXT, Creation date for the list, Examples: [2009-12-18, 2016-02-15, 2016-02-28]),
(user_eligible_for_trial: INTEGER, whether user is eligible for trial, Examples: [0, 1]),
(list_followers: INTEGER, Number of followers on the list, Examples: [5, 100, 25])
]
Question: How many users who created a list in February 2016 were eligible for trial when they created the list? Also identify the user with the most followers for their February 2016 list.
Hint: created a list in February 2016 refers to list_creation_date_utc LIKE '2016-02-%'; eligible for trial refers to user_eligible_for_trial = 1;
Response:

```json
{
  "chain_of_thought_reasoning": "To answer this question, I need to: 1) Filter lists created in February 2016 using list_creation_date_utc, 2) Count users who were eligible for trial (user_eligible_for_trial = 1), 3) Find the user_id with maximum list_followers among February 2016 lists. The list_creation_date_utc column is needed to filter for February 2016. The user_eligible_for_trial column is needed to filter for trial-eligible users. The user_id is needed to identify users. The list_followers column is needed to find the user with most followers. Note: list_id and list_title are NOT needed for this query.",
  "lists_users": ["user_id", "list_creation_date_utc", "user_eligible_for_trial", "list_followers"]
}
```
"""

PROMPT="""
You are an expert and very smart data analyst.
Your task is to examine the provided database schema, understand the posed question, and use the hint to pinpoint the specific columns within tables that are essential for crafting a SQL query to answer the question.
This schema offers an in-depth description of the database's architecture, detailing tables, columns, primary keys, foreign keys, and any pertinent information regarding relationships or constraints. 

## Relevant information
1. The evidence aims to direct your focus towards the specific elements of the database schema that are crucial for answering the question effectively.

## Output format
Please respond with a JSON object structured exactly as shown below:

```json
{{
  "chain_of_thought_reasoning": "Your reasoning for selecting the columns, be concise and clear.",
  "table_name1": ["column1", "column2", ...],
  "table_name2": ["column1", "column2", ...],
  ...
}}
```

**************************
Based on the database schema, question, hint,  your task is to identify all  the columns that are essential for crafting a final, correct SQL query.
For each of the selected columns, explain why exactly it is necessary for answering the question. Your reasoning should be concise and clear, demonstrating a logical connection between the columns and the question asked.

** DATABASE SCHEMA **  
{DATABASE_SCHEMA}

** QUESTION **  
{QUESTION}

** EVIDENCE **
{HINT}
"""