-- Countries above the world average nuclear production per year
-- Uses a CTE to calculate the world average per year
-- then joins it with nuclear_generation to filter countries above the threshold
WITH world_avg_per_year AS (
    SELECT
        year,
        AVG(nuclear_twh) AS world_avg
    FROM nuclear_generation
    WHERE nuclear_twh > 0
    GROUP BY year
)
SELECT
    g.country,
    g.year,
    g.nuclear_twh,
    ROUND(m.world_avg, 2) AS world_average
FROM nuclear_generation g
JOIN world_avg_per_year m ON g.year = m.year
WHERE g.nuclear_twh > m.world_avg
AND g.nuclear_twh > 0
ORDER BY g.year, g.nuclear_twh DESC;