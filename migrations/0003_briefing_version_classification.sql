-- Briefing versions carry their own classification so an older confidential
-- version cannot become readable when a later version cites lower-classification
-- inputs.
ALTER TABLE briefing_versions
    ADD COLUMN classification TEXT NOT NULL DEFAULT 'internal'
    CHECK (classification IN ('public', 'internal', 'confidential', 'restricted'));

-- Existing rows inherit the parent's (monotonic) classification as a safe upper
-- bound; no-op on a fresh database because the seed runs after migrations.
UPDATE briefing_versions
SET classification = (
    SELECT briefings.classification FROM briefings WHERE briefings.id = briefing_versions.briefing_id
)
WHERE EXISTS (SELECT 1 FROM briefings WHERE briefings.id = briefing_versions.briefing_id);

