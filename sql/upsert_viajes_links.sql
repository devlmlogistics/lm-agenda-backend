SELECT setval(
    pg_get_serial_sequence('jotform.links', 'id'),
    COALESCE((SELECT max(id) FROM jotform.links), 0) + 1,
    false
);

INSERT INTO jotform.links (nombre, link)
VALUES
    ('PICKUP_EMPTY_CHIQUITA-OXNARD', 'https://form.jotform.com/250806009572657'),
    ('CHECK-IN_CHIQUITA-OXNARD', 'https://form.jotform.com/241376918061055'),
    ('CHECK-OUT_CHIQUITA-OXNARD', 'https://form.jotform.com/241377172575058'),
    ('CHECK-IN_WALMART/KROGER', 'https://form.jotform.com/241397611247155'),
    ('CHECK-OUT_WALMART/KROGER', 'https://form.jotform.com/241376627923059'),
    ('RETURN_EMPTY_CHIQUITA-OXNARD', 'https://form.jotform.com/241528556019156')
ON CONFLICT (nombre)
DO UPDATE SET link = EXCLUDED.link;
