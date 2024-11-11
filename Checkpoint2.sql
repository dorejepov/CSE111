SELECT * FROM Drivers
WHERE payment_type = 'Zelle' OR payment_type = 'Wire Transfer';

SELECT * FROM Insurance
WHERE strftime('%Y', expiry_date) = '2026';

SELECT * FROM Dispatchers
WHERE payment_type = 'Zelle' AND carrier_id IS NOT NULL;

SELECT * FROM Brokers
WHERE credit_score IN ('A', 'B');

