SELECT c.name AS client_name, p.portfolio_id
FROM clients c
JOIN portfolios p ON c.client_id = p.client_id;