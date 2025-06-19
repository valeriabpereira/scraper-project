# scraper-project

# Objective
Build web scraper ETL and deliver views to the analytics team

# Data Modelling

Tables:

  1. amazon-data: Table that consolidated all CSV files from amazon-data and add a column "file_extraction_date" as the date of the file name
  2. titles: Table that has all data from titles CSV
  3. titles-cleaned: Table that contains all book titles from titles CSV and also a column "data_cleaned" with the main title of the book without extra-information

Views:

  1. sales_rank_evolution: Visualize the evolution of the sales rank for a given book.
  2. top_twenty_books_greatest_improvement: Find the top 20 books with the greatest improvement in average rating from
month 1 to 6.
  3. average_rating_by_period: Plot the average rating of the books by publication period (year-month).
  4. ten_authors_highest_avg_rating: List the 10 authors with the highest average ratings during the last month.
