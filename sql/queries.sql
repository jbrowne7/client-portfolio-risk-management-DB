-- Map clients to portfolio IDs
SELECT c.name AS client_name, p.portfolio_id
FROM clients c
JOIN portfolios p ON c.client_id = p.client_id;

-- Get total value of assets a portfolio holds
SELECT p.portfolio_id, SUM(t.quantity * t.price) AS total_value
FROM portfolios p
JOIN trades t ON p.portfolio_id = t.portfolio_id
GROUP BY p.portfolio_id;

-- FIltering and WHERE


-- Grouping

-- Subqueries

-- Ordering and Limiting

-- Date Functions