-- <query description>
-- Quantas corridas os campeões ganharam a cada ano?
-- </query description>
-- <query>
SELECT
    dc.year,
    dc.name AS champion_name,
    COUNT(rw.name) AS race_wins
FROM
    drivers_championship dc
JOIN
    race_wins rw
ON
    dc.name = rw.name AND dc.year = EXTRACT(YEAR FROM TO_DATE(rw.date, 'DD Mon YYYY'))
WHERE
    dc.position = '1'
GROUP BY
    dc.year, dc.name
ORDER BY
    dc.year;
-- </query>


-- <query description>
-- Comparar o número de vitórias vs posições no campeonato para construtores em 2019
-- </query description>
-- <query>
WITH race_wins_2019 AS (
    SELECT team, COUNT(*) AS wins
    FROM race_wins
    WHERE EXTRACT(YEAR FROM TO_DATE(date, 'DD Mon YYYY')) = 2019
    GROUP BY team
),
constructors_positions_2019 AS (
    SELECT team, position
    FROM constructors_championship
    WHERE year = 2019
)

SELECT cp.team, cp.position, COALESCE(rw.wins, 0) AS wins
FROM constructors_positions_2019 cp
LEFT JOIN race_wins_2019 rw ON cp.team = rw.team
ORDER BY cp.position;
-- </query>

-- <query description>
-- Mais vitórias por um piloto
-- </query description>
-- <query>
SELECT name, COUNT(*) AS win_count
FROM race_wins
GROUP BY name
ORDER BY win_count DESC
LIMIT 1;
-- </query>

-- <query description>
-- Qual equipe ganhou mais Campeonatos de Construtores?
-- </query description>
-- <query>
SELECT team, COUNT(*) AS championship_wins
FROM constructors_championship
WHERE position = 1
GROUP BY team
ORDER BY championship_wins DESC
LIMIT 1;
-- </query>
