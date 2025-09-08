CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE portfolios (
    portfolio_id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(client_id)
);

CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    symbol VARCHAR(8) NOT NULL,
    asset_class VARCHAR(20) NOT NULL,
    base_currency VARCHAR(20) NOT NULL
);

CREATE TABLE trades (
    trade_id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(portfolio_id),
    asset_id INTEGER NOT NULL REFERENCES assets(asset_id),
    trade_date TIMESTAMP NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity NUMERIC NOT NULL,
    price NUMERIC NOT NULL
);

create table prices (
    asset_id INTEGER NOT NULL REFERENCES assets(asset_id),
    price_date DATE NOT NULL,
    price NUMERIC NOT NULL,
    PRIMARY KEY (asset_id, price_date)
);