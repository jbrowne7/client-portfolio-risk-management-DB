-- Migration: add_first_and_last_name_to_clients
-- Created: 2025-09-09 18:52:39.689946

-- Write your SQL changes below

ALTER TABLE clients
    ADD COLUMN first_name VARCHAR(100),
    ADD COLUMN last_name VARCHAR(100);

UPDATE clients
SET first_name = split_part(name, ' ', 1),
    last_name = split_part(name, ' ', 2);

ALTER TABLE clients
    ALTER COLUMN first_name SET NOT NULL,
    ALTER COLUMN last_name SET NOT NULL;

ALTER TABLE clients
    DROP COLUMN name;