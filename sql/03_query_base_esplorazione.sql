SELECT COUNT(*) as totale_righe
FROM nuclear_generation;
SELECT 
    COUNT(DISTINCT country) as paesi_unici,
    MIN(year) as anno_inizio,
    MAX(year) as anno_fine
FROM nuclear_generation;
SELECT 
    country,
    ROUND(AVG(nuclear_twh), 1) as media_twh
FROM nuclear_generation
WHERE nuclear_twh > 0
GROUP BY country
ORDER BY media_twh DESC
LIMIT 10;
SELECT 
    year,
    nuclear_twh
FROM nuclear_generation
WHERE country = 'Italy'
ORDER BY year;