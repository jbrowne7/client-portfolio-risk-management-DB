Migration: add_cash_balance_to_portfolios
-- Created: 2025-09-09 15:05:22.416110

-- Write your SQL changes below

ALTER TABLE portfolios ADD COLUMN cash_balance NUMERIC NOT NULL DEFAULT 0;