-- List of the top 20 books with the greatest improvement from month 1 to 6

CREATE VIEW top_twenty_books_greatest_improvement AS

with tb as (
select max(average_rating) - min(average_rating) as diff_average_rating, title
 from "amazon-data"
 where DATE(CONCAT(file_extraction_date,'-01')) BETWEEN '2023-01-01' AND '2023-06-01'
 group by title
)
 
 select * from tb
 order by diff_average_rating DESC
 LIMIT 20