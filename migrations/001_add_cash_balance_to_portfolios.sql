-- Migration: add_cash_balance_to_portfolios
-- Created: 2025-09-09 15:13:29.199351

-- Write your SQL changes below

ALTER TABLE portfolios ADD COLUMN cash_balance NUMERIC NOT NULL DEFAULT 0;