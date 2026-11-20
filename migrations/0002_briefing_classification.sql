-- Briefings carry a classification so a generated briefing cannot leak
-- confidential content to a role that may not read its sources.
ALTER TABLE briefings
    ADD COLUMN classification TEXT NOT NULL DEFAULT 'internal'
    CHECK (classification IN ('public', 'internal', 'confidential', 'restricted'));
