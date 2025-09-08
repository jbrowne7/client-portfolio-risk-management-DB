INSERT INTO clients (name) VALUES
    ('Alice'),
    ('Bob');

INSERT INTO portfolios (client_id) VALUES
    (1),
    (2);

INSERT INTO assets (symbol, asset_class, base_currency) VALUES
    ('AAPL', 'Stock', 'USD'),
    ('GOOGL', 'Stock', 'USD'),
    ('GBP', 'Forex', 'USD');

INSERT INTO trades (portfolio_id, asset_id, trade_date, side, quantity, price) VALUES
    (1, 1, '2024-01-10 10:00:00', 'BUY', 10, 150.00),
    (2, 2, '2024-01-11 11:00:00', 'BUY', 5, 2800.00);

INSERT INTO prices (asset_id, price_date, price) VALUES
    (1, '2024-01-10', 151.00),
    (2, '2024-01-11', 2805.00);