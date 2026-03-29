-- Countries above the world average nuclear production per year
-- Uses a CTE to calculate the world average per year
-- then joins it with nuclear_generation to filter countries above the threshold
WITH medmondxan AS (
    SELECT
        year,
        AVG(nuclear_twh) AS media_mondiale
    FROM nuclear_generation
    WHERE nuclear_twh > 0
    GROUP BY year
)
SELECT
    g.country,
    g.year,
    g.nuclear_twh,
    ROUND(m.media_mondiale, 2) AS world_average
FROM nuclear_generation g
JOIN medmondxan m ON g.year = m.year
WHERE g.nuclear_twh > m.media_mondiale
AND g.nuclear_twh > 0
ORDER BY g.year, g.nuclear_twh DESC;