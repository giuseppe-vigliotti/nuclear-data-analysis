SELECT COUNT(*) as total_rows
FROM nuclear_generation;
SELECT
    COUNT(DISTINCT country) as unique_countries,
    MIN(year) as start_year,
    MAX(year) as end_year
FROM nuclear_generation;
SELECT
    country,
    ROUND(AVG(nuclear_twh), 1) as avg_twh
FROM nuclear_generation
WHERE nuclear_twh > 0
GROUP BY country
ORDER BY avg_twh DESC
LIMIT 10;
SELECT 
    year,
    nuclear_twh
FROM nuclear_generation
WHERE country = 'Italy'
ORDER BY year;