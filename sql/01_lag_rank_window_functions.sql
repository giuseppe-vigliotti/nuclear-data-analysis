SELECT
    country,
    year,
    nuclear_twh,
    LAG(nuclear_twh) OVER (PARTITION BY country ORDER BY year) AS anno_precedente,
    ROUND(
        nuclear_twh - LAG(nuclear_twh) OVER (PARTITION BY country ORDER BY year)
    , 2) AS variazione
FROM nuclear_generation
WHERE country = 'France'
ORDER BY year;
SELECT
    country,
    year,
    nuclear_twh,
    RANK() OVER (PARTITION BY year ORDER BY nuclear_twh DESC) AS ranking
FROM nuclear_generation
WHERE year = 2020
ORDER BY ranking;
SELECT
    country,
    year,
    nuclear_twh,
    RANK() OVER (PARTITION BY year ORDER BY nuclear_twh DESC) AS ranking
FROM nuclear_generation
WHERE year = 2020
AND nuclear_twh > 0
ORDER BY ranking;
SELECT * FROM (
    SELECT
        country,
        year,
        nuclear_twh,
        RANK() OVER (PARTITION BY year ORDER BY nuclear_twh DESC) AS ranking
    FROM nuclear_generation
    WHERE nuclear_twh > 0
) 
WHERE ranking = 1
ORDER BY year;