FEWSHOT_EXAMPLES_WITH_CRITERIA = """
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

CRITERIA:

Output Requirements:
- What must be returned: A count of unique users
- Output format: A single numerical value

Mandatory Filters/Conditions (combined with AND logic):
- MUST filter for the movie's release year being 1924
- MUST filter for the director's name being 'Erich von Stroheim'
- MUST filter for users who are paying subscribers
- MUST filter for a rating score of 5

Required Operations:
- Aggregations: A COUNT of unique users is required

Completeness Checks:
- Verify that all four conditions (year, director, payment status, rating) are applied
- Check that the output is a count, as requested by "How many"

Correctness Checks:
- Verify logical consistency: all conditions must be met for a user to be counted
- The query must count users, not ratings or movies

Response:
```json
{
  "chain_of_thought_reasoning": "To answer this question, I need to: 1) Filter movies by director 'Erich von Stroheim' and release year 1924, 2) Join with ratings to find users who rated these movies, 3) Filter for paying subscribers (user_has_payment_method = 1) and rating score of 5, 4) Count the users. The director_name and movie_release_year columns are needed to identify the specific movie. The user_has_payment_method and rating_score columns are needed to filter the ratings. The movie_id is needed to join the tables. Note: movie_title, movie_popularity, user_id, and rating_timestamp_utc are NOT needed for this query.",
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

CRITERIA:

Output Requirements:
- What must be returned: A list of user identifiers and the movie's popularity score
- Output format: A list of records, each containing a user ID and the popularity value

Mandatory Filters/Conditions (combined with AND logic):
- MUST filter for the movie's title being 'Love Will Tear Us Apart'
- MUST filter for the rating score being the worst possible (value of 1, per hint)

Required Operations:
- No complex operations beyond selection and filtering

Completeness Checks:
- Verify both parts of the question are addressed: the list of users AND the movie's popularity must be in the output
- Check that the evidence for "worst rating" is incorporated

Correctness Checks:
- Check for correct interpretation of superlatives: "worst" correctly translates to the lowest rating score
- The popularity score for the correct movie must be returned alongside each user

Response:
```json
{
  "chain_of_thought_reasoning": "To answer this question, I need to: 1) Find the movie with title 'Love Will Tear Us Apart', 2) Find all ratings for this movie with score = 1, 3) List the user_ids who gave these ratings, 4) Include the movie's popularity. The movie_title column is needed to identify the specific movie. The rating_score column is needed to filter for worst ratings (score = 1). The user_id is needed to identify users. The movie_popularity is explicitly requested. The movie_id is needed to join the tables. Note: director_name and rating_id are NOT needed for this query.",
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

CRITERIA:

Output Requirements:
- What must be returned: Two separate calculated values: the average rating and a count of positive reviews
- Output format: Two calculated fields

Mandatory Filters/Conditions:
- For the average rating: MUST filter for the app's category being 'COMICS'
- For the positive attitude count: MUST filter for the app's category being 'COMICS' and the review sentiment being 'Positive'

Required Operations:
- Aggregations: AVG for the rating, COUNT for the sentiment

Completeness Checks:
- Verify that both distinct parts of the question (average rating and positive count) are answered
- Check that the hints for calculation and filtering are used

Correctness Checks:
- Verify logical consistency: The average rating and the positive sentiment count must both be calculated specifically for apps within the 'COMICS' category

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

CRITERIA:

Output Requirements:
- What must be returned: A list of superhero names and their corresponding weights
- Output format: A sorted list of records

Mandatory Filters/Conditions:
- MUST filter for the superpower's name being 'Super Strength'

Required Operations:
- Ordering: Results must be sorted by weight in descending order

Completeness Checks:
- Verify that the output includes both superhero names and their weights
- Check that the sorting instruction is followed
- Ensure the hint is incorporated to filter by the power's name

Correctness Checks:
- Validate comparison directions: The sort order must be descending (DESC), not ascending

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

CRITERIA:

Output Requirements:
- What must be returned: Two separate values: a count of trial-eligible users and the user ID with the most followers
- Output format: A single numerical value and a single identifier

Mandatory Filters/Conditions:
- For the user count: MUST filter for a list creation date within February 2016 AND for the user being eligible for a trial
- For identifying the top user: MUST filter for a list creation date within February 2016

Required Operations:
- Aggregations: COUNT for the number of users; MAX or an equivalent operation (like ordering by follower count descending and taking the first result) to find the top user
- Date operations: A pattern match or date range check to isolate records from February 2016

Completeness Checks:
- Verify both parts of the question are answered: the count and the specific user
- Check that all hints for date filtering and trial eligibility are used

Correctness Checks:
- Verify logical consistency: The trial eligibility condition applies ONLY to the count, not to finding the user with the most followers
- Check for correct interpretation of superlatives: "most" must correctly identify the maximum value of followers within the specified date range

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
Your task is to examine the provided database schema, understand the posed question, use the hint and the criteria to pinpoint the specific columns within tables that are essential for crafting a SQL query to answer the question.
This schema offers an in-depth description of the database's architecture, detailing tables, columns, primary keys, foreign keys, and any pertinent information regarding relationships or constraints. 

## Relevant information

1. The “Relevant Entities” section lists database columns whose value match phrases((which can be used for filtering rows) from the question. It does not mean all of them are relevant to answering the question.
 - If multiple columns are a plausible choice for performing the query, thoroughly think which ones make sense to filter on.
 - You can choose to provide multiple similar columns in the response.
2. The hint and criteria aim to direct your focus towards the specific elements of the database schema that are crucial for answering the question effectively.

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
Based on the database schema, question, hint, criteria, identify all the columns that are essential for crafting a final, correct SQL query.
For each of the selected columns, explain why exactly it is necessary for answering the question. Your reasoning should be concise and clear, demonstrating a logical connection between the columns and the question asked.

** DATABASE SCHEMA **  
{DATABASE_SCHEMA}

** RELEVANT ENTITIES **  
{RELEVANT_ENTITIES}

** QUESTION **  
{QUESTION}

** EVIDENCE **
{HINT}

** EVALUATIOM CRITERIA **
{CRITERIA} 
"""