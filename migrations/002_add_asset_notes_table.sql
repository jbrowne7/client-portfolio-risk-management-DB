-- Migration: add_asset_notes_table
-- Created: 2025-09-09 18:29:23.567005

-- Write your SQL changes below

CREATE TABLE IF NOT EXISTS asset_notes (
    note_id SERIAL PRIMARY KEY,
    asset_id INTEGER,
    note TEXT
);