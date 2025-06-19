-- Find the average rating of the books by publication periog 

CREATE VIEW average_rating_by_period AS 
SELECT r.file_extraction_date, r.title, avg(r.average_rating) as average_rating
FROM "amazon-data" r
group by 1,2;