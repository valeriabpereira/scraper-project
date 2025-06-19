-- List of 10 authors with the highest average ratings during last month

CREATE VIEW ten_authors_highest_avg_rating AS

with tb as (
	select max(file_extraction_date) from "amazon-data"
)

select file_extraction_date, author, average_rating from "amazon-data"
where file_extraction_date in (select * from tb)
group by 1,2,3
order by average_rating DESC
limit 10