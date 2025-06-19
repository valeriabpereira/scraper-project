-- Visualize the evoluion of the sales rank for a given book

CREATE VIEW sales_rank_evolution AS 
WITH selected_book AS (
    SELECT 'The Red Necklace' AS book_title
)
SELECT r.file_extraction_date, r.title, r.sales_rank
FROM "amazon-data" r
JOIN selected_book s ON r.title = s.book_title
group by 1,2,3
ORDER BY file_extraction_date ASC;